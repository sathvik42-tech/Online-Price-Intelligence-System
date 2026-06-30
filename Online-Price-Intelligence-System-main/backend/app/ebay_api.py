import os
import requests
import logging
from typing import Dict, Any, List
from backend.utils.ebay_auth import get_ebay_access_token

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_ebay_products(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Searches eBay Browse API (Production) for products.
    Generates a fresh token for every request to ensure reliability.
    """
    access_token = get_ebay_access_token()
    
    if not access_token:
        logging.error("Could not obtain eBay access token. Aborting search.")
        return [{"error": "Authentication failed"}]
    
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "q": query,
        "limit": limit
    }
    
    try:
        logging.info(f"Searching eBay Production API for: '{query}'")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("itemSummaries", [])
            
            results = []
            for item in items:
                results.append({
                    "title": item.get("title"),
                    "price": item.get("price", {}).get("value"),
                    "currency": item.get("price", {}).get("currency"),
                    "itemWebUrl": item.get("itemWebUrl"),
                    "image": item.get("image", {}).get("imageUrl")
                })
            return results
        else:
            logging.error(f"eBay API search failed. Status: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return [{"error": f"API Error {response.status_code}"}]
            
    except Exception as e:
        logging.error(f"eBay API request exception: {str(e)}")
        return [{"error": str(e)}]

if __name__ == "__main__":
    # Test block
    results = search_ebay_products("laptop", limit=3)
    print(results)
