import requests
import json
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

def debug_snapdeal(q):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.snapdeal.com/",
    }
    api_url = (
        f"https://www.snapdeal.com/acors/json/product/get/search"
        f"?keyword={q.replace(' ', '%20')}&numFound=10&start=0&sort=rlvncy"
    )
    
    try:
        resp = requests.get(api_url, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_snapdeal("pencil")
