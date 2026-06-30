import sys
import os
import asyncio
import logging

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from scrapers.meesho_scraper import search_meesho
from scrapers.snapdeal_scraper import search_snapdeal
from scrapers.flipkart_scraper import search_flipkart

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scraper(name, fn, query):
    print(f"\n--- Testing {name} Scraper ---")
    try:
        results = fn(query)
        print(f"Status: SUCCESS" if results else "Status: NO RESULTS")
        print(f"Results Count: {len(results)}")
        for i, res in enumerate(results[:3]):
            print(f"  [{i+1}] {res.get('title')[:50]}... | Price: {res.get('price')} {res.get('currency')}")
            print(f"      URL: {res.get('product_url')[:50]}...")
            print(f"      Logo Status: {'OK' if res.get('image_url') else 'MISSING'}")
        return len(results) > 0
    except Exception as e:
        print(f"Status: FAILED")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    query = "laptop"
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    
    print(f"Verifying Indian Scrapers for: '{query}'")
    
    meesho_ok = test_scraper("Meesho", search_meesho, query)
    snapdeal_ok = test_scraper("Snapdeal", search_snapdeal, query)
    # Flipkart is Selenium-based and might be slow
    flipkart_ok = test_scraper("Flipkart", search_flipkart, query)
    
    print("\n" + "="*30)
    print(f"Meesho: {'✅' if meesho_ok else '❌'}")
    print(f"Snapdeal: {'✅' if snapdeal_ok else '❌'}")
    print(f"Flipkart: {'✅' if flipkart_ok else '❌'}")
    print("="*30)
