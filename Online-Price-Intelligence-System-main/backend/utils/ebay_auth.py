import os
import requests
import base64
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_ebay_access_token():
    """
    Fetch a fresh eBay OAuth access token using Client Credentials Grant.
    Returns: string access_token or None if failed.
    """
    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        logging.error("eBay Credentials missing in .env")
        return None

    url = "https://api.ebay.com/identity/v1/oauth2/token"
    
    # Basic Auth: b64encode(client_id:client_secret)
    auth_str = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64_auth}"
    }
    
    payload = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    
    try:
        logging.info("Requesting fresh eBay OAuth token...")
        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            logging.info("Successfully retrieved eBay access token.")
            return token
        else:
            logging.error(f"eBay OAuth failed. Status: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"eBay OAuth Exception: {str(e)}")
        return None
