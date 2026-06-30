from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def search_ebay_selenium(keyword):
    """
    Searches eBay using Selenium with strict filtering for valid results.
    Handles placeholders and sponsored content.
    """
    # 1. Setup ChromeOptions
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Comment out to see browser
    
    # NEW: Add SSL and certificate ignore options to fix handshake errors
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    
    # Add anti-bot options to hide automation signatures (matching Amazon logic)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Standardize driver version using ChromeDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Hide 'navigator.webdriver' property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    products = []
    
    try:
        # 2. Open eBay search results page
        search_url = f"https://www.ebay.com/sch/i.html?_nkw={keyword.replace(' ', '+')}"
        print(f"Opening eBay (Selenium) for: '{keyword}'...")
        driver.get(search_url)

        # 3. Use WebDriverWait for results container
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.s-item')))

        # 4. Extract raw item elements
        items = driver.find_elements(By.CSS_SELECTOR, 'li.s-item')
        
        # 5. Print total raw results
        print(f"Total raw eBay results found: {len(items)}")

        # 6. Loop and extract first 5 VALID items
        valid_count = 0
        for item in items:
            if valid_count >= 10:
                break
                
            # --- Title ---
            try:
                title_elem = item.find_elements(By.CSS_SELECTOR, '.s-item__title')
                title = title_elem[0].text.strip() if title_elem else None
            except:
                title = None
            
            # --- Filtering Logic ---
            if not title or "shop on ebay" in title.lower() or "sponsored" in title.lower():
                continue
            
            # --- URL ---
            url = "N/A"
            try:
                url_elem = item.find_elements(By.CSS_SELECTOR, '.s-item__link')
                url = url_elem[0].get_attribute('href') if url_elem else "N/A"
            except: pass
            
            # --- Price ---
            price = "0.00"
            try:
                price_elem = item.find_elements(By.CSS_SELECTOR, '.s-item__price')
                price = price_elem[0].text.strip() if price_elem else "0.00"
            except: pass
            
            # --- Shipping ---
            shipping = "0.00"
            try:
                shipping_elem = item.find_elements(By.CSS_SELECTOR, '.s-item__shipping, .s-item__freeToS')
                shipping_text = shipping_elem[0].text.strip() if shipping_elem else "0.00"
                if "free" in shipping_text.lower():
                    shipping = "0.00"
                else:
                    shipping = shipping_text
            except: pass

            # --- Seller Rating (Placeholder for eBay as it's often not in the search grid) ---
            rating = "4.0" # Default for valid eBay listings for scoring purposes if missing

            products.append({
                "platform": "eBay",
                "title": title,
                "price": price,
                "currency": "USD",
                "availability": "In Stock",
                "product_url": url,
                "seller_rating": rating,
                "shipping_info": shipping
            })
            valid_count += 1

    except Exception as e:
        print(f"An error occurred during eBay Selenium search: {e}")

    finally:
        # 9. Print number of valid results
        print(f"Valid eBay products extracted: {len(products)}")
        
        # 10. Close driver properly
        driver.quit()

    return products

if __name__ == "__main__":
    results = search_ebay_selenium("iphone 13")
    for r in results:
        print(r)
