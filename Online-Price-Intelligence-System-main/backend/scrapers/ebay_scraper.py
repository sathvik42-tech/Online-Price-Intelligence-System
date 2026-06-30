import logging
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
from selenium_stealth import stealth
try:
    from backend.utils.headers import USER_AGENTS
except ImportError:
    from utils.headers import USER_AGENTS

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_ebay(keyword: str) -> List[Dict[str, Any]]:
    """
    Scrapes eBay (fallback) using Selenium with Stealth to bypass bot detection.
    Uses version-safe driver setup.
    """
    products = []
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    ua = random.choice(USER_AGENTS)
    chrome_options.add_argument(f"user-agent={ua}")
    
    driver = None
    try:
        logging.info(f"Starting eBay search (Stealth) for: {keyword}")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        
        url = f"https://www.ebay.com/sch/i.html?_nkw={keyword.replace(' ', '+')}"
        driver.get(url)
        
        # Wait for product items
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.s-item')))
        except:
            logging.warning("eBay results container not found.")
            return []

        items = driver.find_elements(By.CSS_SELECTOR, 'li.s-item')
        
        valid_count = 0
        for i, item in enumerate(items):
            if valid_count >= 10: break
            
            try:
                # 1. Title
                title_elem = item.find_elements(By.CSS_SELECTOR, '.s-item__title')
                title = title_elem[0].text.strip() if title_elem else ""
                if title.lower().startswith("new listing"):
                    title = title[11:].strip()

                if not title or "shop on ebay" in title.lower() or "sponsored" in title.lower():
                    continue

                # 2. Price
                price = "0.00"
                price_elems = item.find_elements(By.CSS_SELECTOR, '.s-item__price')
                if price_elems:
                    price = price_elems[0].text.strip()

                # 3. URL
                url = "N/A"
                link_elem = item.find_elements(By.CSS_SELECTOR, 'a.s-item__link')
                if link_elem:
                    url = link_elem[0].get_attribute('href')

                # 4. Shipping
                shipping = "0.00"
                ship_elem = item.find_elements(By.CSS_SELECTOR, '.s-item__shipping')
                if ship_elem:
                    shipping_text = ship_elem[0].text.strip().lower()
                    if "free" in shipping_text:
                        shipping = "0.00"
                    else:
                        shipping = shipping_text

                products.append({
                    "platform": "ebay",
                    "title": title,
                    "price": price,
                    "currency": "USD",
                    "availability": "In Stock",
                    "product_url": url,
                    "seller_rating": "4.0",
                    "shipping_info": shipping
                })
                valid_count += 1
            except: continue

    except Exception as e:
        logging.error(f"eBay search failed: {e}")
    finally:
        if driver:
            driver.quit()

    return products

if __name__ == "__main__":
    results = search_ebay("iphone")
    for r in results:
        print(r)
