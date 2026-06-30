import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- CONFIGURATION ---
# Target product URL
TARGET_URL = "https://www.target.com/p/apple-iphone-13-128gb-midnight-at-38-t/-/A-84153096"

def scrape_target_with_selenium(url):
    """
    Uses Selenium to open a Target product page and extract details.
    """
    # 1. Set up Chrome WebDriver options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment to run without a visible window
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("window-size=1920,1080")
    
    # Realistic User-Agent to avoid detection
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    print(f"Opening browser and navigating to: {url}...")
    
    try:
        # 2. Open the Target product URL
        driver.get(url)

        # 3. Wait for the page to load using WebDriverWait
        # We wait up to 10 seconds for the title to appear
        wait = WebDriverWait(driver, 10)
        
        print("Waiting for elements to load...")
        
        # 4. Extract Data
        
        # --- Extract Title ---
        # Selector: h1[data-test="product-title"]
        try:
            title_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[data-test="product-title"]')))
            title = title_elem.text.strip()
        except TimeoutException:
            title = "Title not found"

        # --- Extract Price ---
        # Selector: [data-test="product-price"]
        try:
            price_elem = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price"]')
            price = price_elem.text.strip()
        except NoSuchElementException:
            price = "Price not found"

        # --- Extract Rating ---
        # Search for any element with aria-label containing "out of 5 stars"
        try:
            # We look for an element that contains the rating text in its aria-label
            rating_elem = driver.find_element(By.XPATH, '//*[contains(@aria-label, "out of 5 stars")]')
            rating = rating_elem.get_attribute("aria-label").strip()
        except NoSuchElementException:
            rating = "Rating not found"

        # 9. Print output in the requested format
        print("\n" + "-" * 32)
        print("TARGET PRODUCT DETAILS (via Selenium)")
        print("-" * 32)
        print(f"Title:  {title}")
        print(f"Price:  {price}")
        print(f"Rating: {rating}")
        print("-" * 32 + "\n")

    except Exception as e:
        # 5. Add proper exception handling
        print(f"An unexpected error occurred: {e}")

    finally:
        # 6. Ensure the browser closes even if an error occurs
        print("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    scrape_target_with_selenium(TARGET_URL)
