import logging
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from utils.headers import USER_AGENTS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_walmart(keyword):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        url = f"https://www.walmart.com/search?q={keyword.replace(' ', '+')}"
        logging.info(f"Navigating to {url}")
        driver.get(url)
        
        # Sleep to allow JS to run
        time.sleep(10)
        
        # Log some page info
        logging.info(f"Page Title: {driver.title}")
        
        # Search for any item IDs or common classes
        items = driver.find_elements(By.CSS_SELECTOR, "div[data-item-id]")
        logging.info(f"Found {len(items)} items using 'div[data-item-id]'")
        
        if len(items) == 0:
            # Check for bot detection
            if "Robot or Human" in driver.page_source or "verification" in driver.page_source.lower():
                logging.error("Walmart detected bot or triggered verification.")
            else:
                logging.info("Searching for alternative containers...")
                all_divs = driver.find_elements(By.TAG_NAME, "div")
                logging.info(f"Total divs on page: {len(all_divs)}")
                
                # Look for 'Search Results' or similar text
                if "No results found" in driver.page_source:
                    logging.warning("Walmart says No results found.")
                
        for i, item in enumerate(items[:3]):
            logging.info(f"Item {i+1} text snippet: {item.text[:100]}...")

    except Exception as e:
        logging.error(f"Debug failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_walmart("laptop")
