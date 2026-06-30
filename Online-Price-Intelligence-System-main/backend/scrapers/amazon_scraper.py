from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_amazon(keyword):
    """
    Searches Amazon India using Selenium.
    Extracts: title, price (INR), product URL, image_url, seller_rating, availability.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    products = []

    try:
        search_url = f"https://www.amazon.in/s?k={keyword.replace(' ', '+')}"
        logging.info(f"Opening Amazon (Selenium) for: '{keyword}'...")
        driver.get(search_url)

        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')))

        results = driver.find_elements(By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')

        for i, result in enumerate(results[:10]):
            try:
                # ── Title ──────────────────────────────────────────────────────
                title = ""
                for selector in [
                    'h2 a span',
                    'h2 .a-size-medium',
                    'h2 .a-size-base-plus',
                    '.a-size-medium.a-color-base.a-text-normal',
                    'h2 span',
                    '.a-link-normal .a-text-normal',
                    '[data-cy="title-recipe-title"]',
                ]:
                    title_elems = result.find_elements(By.CSS_SELECTOR, selector)
                    if title_elems:
                        candidate = title_elems[0].text.strip()
                        if candidate and candidate.lower() not in ("", "n/a"):
                            title = candidate
                            break

                if not title:
                    title = keyword  # use keyword as fallback

                # ── URL ────────────────────────────────────────────────────────
                url = ""
                url_elem = result.find_elements(By.CSS_SELECTOR, 'h2 a')
                if url_elem:
                    url = url_elem[0].get_attribute('href') or ""
                    if url and not url.startswith('http'):
                        url = "https://www.amazon.in" + url

                # ── Price ──────────────────────────────────────────────────────
                price = "0.00"
                price_elem = result.find_elements(By.CSS_SELECTOR, '.a-price .a-offscreen')
                if price_elem:
                    price_text = price_elem[0].get_attribute('innerHTML') or price_elem[0].text
                    price = "".join(filter(lambda x: x.isdigit() or x == '.', price_text))
                else:
                    price_whole = result.find_elements(By.CSS_SELECTOR, '.a-price-whole')
                    price_fraction = result.find_elements(By.CSS_SELECTOR, '.a-price-fraction')
                    if price_whole:
                        price = price_whole[0].text.strip().replace(',', '').rstrip('.')
                        if price_fraction:
                            price += "." + price_fraction[0].text.strip()

                # ── Rating ─────────────────────────────────────────────────────
                rating = "4.0"
                rating_elem = result.find_elements(By.CSS_SELECTOR, 'span[aria-label*="out of 5 stars"]')
                if rating_elem:
                    aria = rating_elem[0].get_attribute('aria-label') or ""
                    m = re.search(r'([\d.]+)\s+out of', aria)
                    if m:
                        rating = m.group(1)
                else:
                    irating = result.find_elements(By.CSS_SELECTOR, '.a-icon-alt')
                    if irating:
                        m = re.search(r'([\d.]+)', irating[0].get_attribute('innerHTML') or "")
                        if m:
                            rating = m.group(1)

                # ── Image ──────────────────────────────────────────────────────
                image_url = ""
                img_elem = result.find_elements(By.CSS_SELECTOR, 'img.s-image')
                if img_elem:
                    image_url = img_elem[0].get_attribute('src') or ""

                # ── Shipping ───────────────────────────────────────────────────
                shipping = "0.00"
                if "FREE" in result.text or "free delivery" in result.text.lower():
                    shipping = "0.00"
                else:
                    shipping = "Standard Shipping"

                # ── Availability ───────────────────────────────────────────────
                availability = "In Stock"
                if "Currently unavailable" in result.text or "Out of Stock" in result.text:
                    availability = "Out of Stock"

                products.append({
                    "platform": "amazon",
                    "title": title,
                    "price": price,
                    "currency": "INR",
                    "availability": availability,
                    "product_url": url,
                    "image_url": image_url,
                    "seller_rating": rating,
                    "shipping_info": shipping
                })
            except Exception:
                continue

    except Exception as e:
        logging.error(f"Amazon scraper error: {e}")
    finally:
        driver.quit()

    logging.info(f"Amazon: found {len(products)} products for '{keyword}'")
    return products


if __name__ == "__main__":
    test_results = search_amazon("analog watch")
    for r in test_results:
        print(r)
