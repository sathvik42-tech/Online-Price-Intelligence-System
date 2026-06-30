from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def search_amazon_selenium(keyword):
    """
    Searches Amazon India using Selenium with advanced anti-bot measures.
    Runs in visible mode to handle modern bot detection more reliably.
    """
    # 1. Setup ChromeOptions
    chrome_options = Options()
    
    # Run in visible mode as requested (NOT headless)
    # chrome_options.add_argument("--headless") 
    
    # 3. Add anti-bot options to hide automation signatures
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Standard realistic user-agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # 4. Hide 'navigator.webdriver' property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    products = []
    
    try:
        # 5. Open the Amazon search results page
        search_url = f"https://www.amazon.in/s?k={keyword.replace(' ', '+')}"
        logging.info(f"Opening Amazon (Selenium) for: '{keyword}'...")
        driver.get(search_url)

        # 6. Wait for results
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')))

        results = driver.find_elements(By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')
        logging.info(f"Total Amazon results found: {len(results)}")

        for i, result in enumerate(results[:10]):  # Extract top 10 results
            try:
                # --- Title ---
                title = "N/A"
                title_elem = result.find_elements(By.CSS_SELECTOR, 'h2 a span')
                if title_elem:
                    title = title_elem[0].text.strip()

                # --- URL ---
                url = "N/A"
                url_elem = result.find_elements(By.CSS_SELECTOR, 'h2 a')
                if url_elem:
                    url = url_elem[0].get_attribute('href')
                    if not url.startswith('http'):
                        url = "https://www.amazon.in" + url

                # --- Price ---
                price = "0.00"
                currency = "INR"
                price_whole = result.find_elements(By.CSS_SELECTOR, '.a-price-whole')
                price_fraction = result.find_elements(By.CSS_SELECTOR, '.a-price-fraction')
                if price_whole:
                    price = price_whole[0].text.strip().replace(',', '')
                    if price_fraction:
                        price += "." + price_fraction[0].text.strip()
                
                # --- Rating ---
                rating = "N/A"
                rating_elem = result.find_elements(By.CSS_SELECTOR, 'span[aria-label*="out of 5 stars"]')
                if rating_elem:
                    rating_text = rating_elem[0].get_attribute('aria-label')
                    rating = rating_text.split(' ')[0]

                # --- Shipping ---
                shipping = "0.00"
                if "FREE" in result.text:
                    shipping = "0.00"
                else:
                    # Simple placeholder if specific shipping text not found
                    shipping = "Check Amazon"

                # --- Availability ---
                availability = "In Stock"
                if "Currently unavailable" in result.text or "Out of Stock" in result.text:
                    availability = "Out of Stock"

                products.append({
                    "platform": "Amazon",
                    "title": title,
                    "price": price,
                    "currency": currency,
                    "availability": availability,
                    "product_url": url,
                    "seller_rating": rating,
                    "shipping_info": shipping
                })

            except Exception as item_error:
                logging.debug(f"Error parsing item {i}: {item_error}")
                continue

    except Exception as e:
        logging.error(f"CRITICAL ERROR during search: {e}")

    except Exception as e:
        print(f"\nCRITICAL ERROR during search: {e}")

    finally:
        # 8. Print count
        print(f"\nDebug version finished. Products collected: {len(products)}")
        
        # 13. Close driver properly
        driver.quit()

    return products

if __name__ == "__main__":
    test_results = search_amazon_selenium("iphone 13")
    for r in test_results:
        print(r)
