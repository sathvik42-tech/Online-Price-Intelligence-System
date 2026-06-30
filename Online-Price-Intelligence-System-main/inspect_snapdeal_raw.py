
import requests
import json
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

def inspect_snapdeal_raw():
    q = "Teddy"
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Referer": "https://www.snapdeal.com/",
    }
    api_url = (
        f"https://www.snapdeal.com/acors/json/product/get/search"
        f"?keyword={q.replace(' ', '%20')}&numFound=5&start=0&sort=rlvncy"
    )
    print(f"Requesting: {api_url}")
    resp = requests.get(api_url, headers=headers, timeout=12)
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, indent=2)[:5000]) # Print first 5000 chars
    else:
        print(f"Failed with status: {resp.status_code}")

if __name__ == "__main__":
    inspect_snapdeal_raw()
