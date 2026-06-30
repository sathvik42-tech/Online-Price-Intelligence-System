
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from utils.aggregation import aggregate_prices

def test_aggregation():
    sample_results = {
        "ebay": [
            {
                "title": "Test Product",
                "price": 10,
                "currency": "USD",
                "shipping_info": "2",
                "product_url": "http://ebay.com/test",
                "image_url": "http://ebay.com/test.jpg"
            }
        ],
        "amazon": [
            {
                "title": "Test Product Amazon",
                "price": 800,
                "currency": "INR",
                "shipping_info": "50",
                "product_url": "http://amazon.com/test",
                "image_url": "http://amazon.com/test.jpg"
            }
        ]
    }
    
    try:
        aggregated = aggregate_prices(sample_results, query="Test")
        print(f"Aggregated {len(aggregated)} items successfully.")
        for item in aggregated:
            print(f"- {item['platform']}: {item['title']} - Price: {item['price']} - Shipping: {item['shipping']}")
    except Exception as e:
        print(f"Aggregation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_aggregation()
