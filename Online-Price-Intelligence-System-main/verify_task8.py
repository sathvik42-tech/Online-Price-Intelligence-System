from main_scraper import search_all_platforms
import json

def verify_system():
    print("--- Task 8 Verification ---")
    query = "wireless mouse"
    results = search_all_platforms(query)
    
    print(f"\nResults for '{query}':")
    for platform, items in results.items():
        print(f"{platform.upper()}: found {len(items)} items")
        if items:
            # Check standard format of the first item
            first = items[0]
            required_keys = ["platform", "title", "price", "currency", "availability", "product_url", "seller_rating", "shipping_info"]
            missing = [k for k in required_keys if k not in first]
            if missing:
                print(f"  [ERROR] Missing keys in {platform}: {missing}")
            else:
                print(f"  [SUCCESS] {platform} format is correct.")
    
    with open("verification_results.json", "w") as f:
        json.dump(results, f, indent=4)
    print("\nVerification results saved to 'verification_results.json'")

if __name__ == "__main__":
    verify_system()
