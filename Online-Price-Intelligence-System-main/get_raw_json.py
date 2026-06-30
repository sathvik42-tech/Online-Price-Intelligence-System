
import json
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from scrapers.snapdeal_scraper import search_snapdeal
from utils.aggregation import aggregate_prices

def get_raw_json():
    keyword = "Teddy"
    results = search_snapdeal(keyword)
    
    output = {
        "raw_results": results,
        "aggregated": aggregate_prices({"snapdeal": results}, query=keyword)
    }
    
    with open("raw_diagnostic.json", "w") as f:
        json.dump(output, f, indent=4)
    print("Results saved to raw_diagnostic.json")

if __name__ == "__main__":
    get_raw_json()
