import logging
import re
import time
import random
from typing import List, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


def search_flipkart(keyword: str) -> List[Dict[str, Any]]:
    """
    Searches Flipkart.com using Selenium (mirrors the Amazon scraper pattern).
    Returns prices in INR.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    products: List[Dict[str, Any]] = []

    try:
        search_url = f"https://www.flipkart.com/search?q={keyword.replace(' ', '+')}"
        logger.info(f"Opening Flipkart (Selenium) for: '{keyword}'...")
        driver.get(search_url)

        # Dismiss login popup if it appears
        try:
            close_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button._2KpZ6l._2doB4z"))
            )
            close_btn.click()
        except Exception:
            pass

        # Wait for product cards
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[data-id], div._1AtVbE, div._2kHMtA")
                )
            )
        except Exception:
            logger.warning("Flipkart: No product cards found within timeout.")
            return []

        time.sleep(1)

        # Try multiple card selectors used by Flipkart
        card_selectors = [
            "div._1AtVbE",      # standard product cards
            "div._2kHMtA",      # alternate grid cards
            "div[data-id]",     # any annotated product card
        ]

        result_cards = []
        for selector in card_selectors:
            result_cards = driver.find_elements(By.CSS_SELECTOR, selector)
            if result_cards:
                break

        seen = set()

        for card in result_cards[:20]:
            if len(products) >= 10:
                break
            try:
                # ── Title ──────────────────────────────────────────────────────
                title = ""
                for sel in [
                    "div._4rR01T",
                    "a.s1Q9rs",
                    "div._2WkVRV",
                    "a.IRpwTa",
                    "div.KzDlHZ",
                    "_2B099V",
                ]:
                    elems = card.find_elements(By.CSS_SELECTOR, sel)
                    if elems:
                        candidate = elems[0].text.strip()
                        if candidate:
                            title = candidate
                            break

                # Also try <a> tags to find any product links with text
                if not title:
                    anchors = card.find_elements(By.TAG_NAME, "a")
                    for a in anchors:
                        t = a.text.strip()
                        if t and len(t) > 5:
                            title = t
                            break

                if not title:
                    continue

                # ── URL ────────────────────────────────────────────────────────
                url = ""
                for sel in ["div._4rR01T a", "a.s1Q9rs", "a._1fQZEK", "a"]:
                    link_elems = card.find_elements(By.CSS_SELECTOR, sel)
                    if link_elems:
                        href = link_elems[0].get_attribute("href") or ""
                        if href and "flipkart.com" in href:
                            url = href
                            break

                if not url:
                    # Try any anchor with flipkart.com href
                    anchors = card.find_elements(By.TAG_NAME, "a")
                    for a in anchors:
                        href = a.get_attribute("href") or ""
                        if href and "flipkart.com" in href:
                            url = href
                            break

                # ── Price ──────────────────────────────────────────────────────
                price = 0.0
                for sel in [
                    "div._30jeq3",   # main price
                    "div._1_WHN1",   # sale price
                    "div._3I9_wc",   # deal price
                    "div.Nx9bqj",    # alternate price
                ]:
                    price_elems = card.find_elements(By.CSS_SELECTOR, sel)
                    if price_elems:
                        price_text = price_elems[0].text.strip()
                        cleaned = re.sub(r"[^\d.]", "", price_text)
                        if cleaned:
                            try:
                                price = float(cleaned)
                                if price > 0:
                                    break
                            except ValueError:
                                pass

                # ── Rating ─────────────────────────────────────────────────────
                rating = "4.0"
                for sel in ["div._3LWZlK", "span._1lRcqv"]:
                    rating_elems = card.find_elements(By.CSS_SELECTOR, sel)
                    if rating_elems:
                        rt = rating_elems[0].text.strip()
                        if rt and re.match(r"[\d.]+", rt):
                            rating = rt
                            break

                # ── Image ──────────────────────────────────────────────────────
                image_url = ""
                img_elems = card.find_elements(By.CSS_SELECTOR, "img._396cs4, img._2r_T1I, img")
                if img_elems:
                    image_url = img_elems[0].get_attribute("src") or ""

                key = (title.lower(), url)
                if key in seen:
                    continue
                seen.add(key)

                products.append(
                    {
                        "platform": "flipkart",
                        "title": title,
                        "price": price,
                        "currency": "INR",
                        "availability": "In Stock",
                        "product_url": url or f"https://www.flipkart.com/search?q={keyword.replace(' ', '+')}",
                        "image_url": image_url,
                        "seller_rating": rating,
                        "shipping_info": "Free Delivery Available",
                    }
                )
            except Exception:
                continue

    except Exception as e:
        logger.error(f"Flipkart scraper error: {e}")
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    logger.info(f"Flipkart: found {len(products)} products for '{keyword}'")
    return products


if __name__ == "__main__":
    results = search_flipkart("pencil")
    for r in results:
        print(r.get("title"), r.get("price"), r.get("product_url"))
