import os
import requests
import base64
import json
from dotenv import load_dotenv

def test_ebay_browse_api(access_token):
    print("\n--- eBay Browse API Search Test (Production) ---")
    
    # eBay Browse API Search endpoint
    # Search for "laptop" as requested
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "q": "laptop",
        "limit": 3
    }
    
    print(f"Requesting search from: {url}?q=laptop")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            total_items = data.get("total", 0)
            items = data.get("itemSummaries", [])
            
            print(f"\nTotal Items Found: {total_items}")
            print("\nTop 3 Products:")
            print("-" * 40)
            
            for i, item in enumerate(items):
                title = item.get("title")
                price_data = item.get("price", {})
                price = price_data.get("value")
                currency = price_data.get("currency")
                
                print(f"{i+1}. {title}")
                print(f"   Price: {price} {currency}")
                print("-" * 40)
            
            print("\n" + "="*40)
            print("Browse API Working Successfully")
            print("="*40)
        else:
            print(f"\nBrowse API Search Failed! Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\nAn error occurred during Browse API search: {str(e)}")

def test_ebay_oauth_connection():
    print("\n--- eBay OAuth Token Test (Production) ---")
    
    # Load environment variables from .env
    load_dotenv()
    
    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("Error: EBAY_CLIENT_ID or EBAY_CLIENT_SECRET missing in .env file.")
        return None

    # eBay Production OAuth endpoint
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    
    # eBay requires Basic Auth with base64 encoded client_id:client_secret
    auth_str = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64_auth}"
    }
    
    # Body for Client Credentials Grant
    payload = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    
    print(f"Requesting token from: {url}")
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response_json = response.json()
        
        if response.status_code == 200:
            access_token = response_json.get('access_token')
            print("\n" + "="*40)
            print("eBay Production API Connected Successfully")
            print("="*40)
            return access_token
        else:
            print("\n" + "="*40)
            print(f"OAuth Connection Failed! Status Code: {response.status_code}")
            print("="*40)
            print(json.dumps(response_json, indent=4))
            return None
            
    except Exception as e:
        print(f"\nAn error occurred during OAuth: {str(e)}")
        return None

def verify_env_setup():
    print("--- Environment Setup Verification ---")
    env_path = ".env"
    if os.path.exists(env_path):
        print(f"Found .env file at: {os.path.abspath(env_path)}")
    else:
        print("Warning: .env file NOT found in current directory!")
        
    load_dotenv()
    client_id = os.getenv("EBAY_CLIENT_ID")
    if client_id:
        print(f"EBAY_CLIENT_ID: {client_id}")
    else:
        print("Error: EBAY_CLIENT_ID not found in environment.")

if __name__ == "__main__":
    verify_env_setup()
    access_token = test_ebay_oauth_connection()
    if access_token:
        test_ebay_browse_api(access_token)
