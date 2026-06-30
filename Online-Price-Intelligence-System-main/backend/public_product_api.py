import requests

# --- CONFIGURATION ---
# Public API endpoint for a single product (iPhone 9 in this case)
API_URL = "https://dummyjson.com/products/1"

def fetch_product_data():
    """
    Sends a GET request to a public API and prints specific product details.
    """
    print(f"Requesting data from: {API_URL}...\n")
    
    try:
        # 1. Send GET request to the public API
        response = requests.get(API_URL)
        
        # 3. Handle status code properly
        if response.status_code == 200:
            # Parse the JSON response into a Python dictionary
            product_data = response.json()
            
            # 2. Extract and Print specific fields
            title = product_data.get("title", "N/A")
            price = product_data.get("price", "N/A")
            rating = product_data.get("rating", "N/A")
            brand = product_data.get("brand", "N/A")
            
            # 4. Clean formatted output
            print("-" * 30)
            print("PUBLIC API PRODUCT DETAILS")
            print("-" * 30)
            print(f"Title:  {title}")
            print(f"Price:  ${price}")
            print(f"Rating: {rating}/5")
            print(f"Brand:  {brand}")
            print("-" * 30)
            
        else:
            print(f"Failed to fetch data. Status Code: {response.status_code}")
            
    except Exception as e:
        # Catch network errors or parsing issues
        print(f"An error occurred: {e}")

# entry point of the script
if __name__ == "__main__":
    fetch_product_data()
