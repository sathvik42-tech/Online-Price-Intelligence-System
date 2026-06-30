import requests
from bs4 import BeautifulSoup
from utils import get_random_headers, throttle_request

def search_amazon(keyword):
    """
    Constructs a search URL, fetches the results page, and extracts the first 5 products.
    Returns a list of dictionaries containing product details.
    """
    # 1. Construct search URL targeting Amazon India
    search_url = f"https://www.amazon.in/s?k={keyword.replace(' ', '+')}"
    print(f"Searching Amazon for: '{keyword}'...")
    
    products = []
    
    try:
        # 2. Use get_random_headers() from utils.py for the request
        headers = get_random_headers()
        response = requests.get(search_url, headers=headers)
        
        # 3. Call throttle_request() from utils.py before parsing (as requested)
        throttle_request()
        
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return []

        # 4. Use BeautifulSoup with html.parser
        soup = BeautifulSoup(response.content, "html.parser")

        # 5. Extract first 5 product results
        result_items = soup.select('div[data-component-type="s-search-result"]')[:5]

        for item in result_items:
            # --- Title ---
            title_elem = item.select_one('h2 a span')
            title = title_elem.get_text().strip() if title_elem else "Title not found"

            # --- Price ---
            price_elem = item.select_one('span.a-price-whole')
            price = price_elem.get_text().strip() if price_elem else "Price not found"

            # --- Product URL ---
            url_elem = item.select_one('h2 a')
            product_url = "https://www.amazon.in" + url_elem['href'] if url_elem else "URL not found"

            # --- Rating ---
            rating_elem = item.select_one('i.a-icon-star-small span.a-icon-alt')
            if not rating_elem:
                rating_elem = item.select_one('i.a-icon-star span.a-icon-alt')
            rating = rating_elem.get_text().strip() if rating_elem else "Rating not found"

            # Add to products list as a dictionary
            products.append({
                "title": title,
                "price": price,
                "url": product_url,
                "rating": rating
            })

    except Exception as e:
        print(f"An error occurred during Amazon search: {e}")

    return products

# Example usage for testing and beginner clarity
if __name__ == "__main__":
    # Test keyword
    sample_keyword = "wireless mouse"
    
    results = search_amazon(sample_keyword)
    
    print(f"\nFound {len(results)} results:")
    for idx, p in enumerate(results, 1):
        print(f"\n--- Result {idx} ---")
        print(f"Title:  {p['title']}")
        print(f"Price:  {p['price']}")
        print(f"Rating: {p['rating']}")
        print(f"URL:    {p['url']}")
        print("-" * 20)
