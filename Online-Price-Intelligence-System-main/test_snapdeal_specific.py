
import asyncio
import json
import logging
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from scrapers.snapdeal_scraper import search_snapdeal
from utils.aggregation import aggregate_prices

def test_specific_product():
    logging.basicConfig(level=logging.INFO)
    keyword = "Teddy toothbrushes holder pack of 2"
    print(f"Searching Snapdeal for: {keyword}")
    results = search_snapdeal(keyword)
    
    print(f"Found {len(results)} items from Snapdeal.")
    for item in results:
        print(f"Title: {item.get('title')}")
        print(f"Price: {item.get('price')}")
        print(f"Raw Price from item: {item.get('price')}")
        print("-" * 20)
        
    all_results = {"snapdeal": results}
    aggregated = aggregate_prices(all_results, query=keyword)
    print(f"Aggregated count: {len(aggregated)}")
    for item in aggregated:
        print(f"Aggregated Title: {item.get('title')}, Price: {item.get('price')}")
        if item.get('price') <= 0:
            print(f"!!! ZERO OR NEGATIVE PRICE ITEM FOUND: {item.get('title')}")

if __name__ == "__main__":
    test_specific_product()
