
import requests
from bs4 import BeautifulSoup
import re
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

def _parse_price(text: str) -> float:
    if not text:
        return 0.0
    text_str = str(text)
    text_str = re.sub(r"Rs\.", "Rs", text_str, flags=re.I)
    cleaned = re.sub(r"[^\d.]", "", text_str)
    if cleaned.count('.') > 1:
        parts = cleaned.split('.')
        cleaned = parts[0] + '.' + ''.join(parts[1:])
    try:
        val = float(cleaned) if cleaned else 0.0
        return val
    except ValueError:
        return 0.0

def test_html_scrape(keyword):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    url = f"https://www.snapdeal.com/search?keyword={keyword.replace(' ', '%20')}&sort=rlvncy"
    resp = requests.get(url, headers=headers, timeout=12)
    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select("div.product-tuple-listing") or soup.select("div.favDp")
    
    for card in cards[:5]:
        title_el = card.select_one("p.product-title") or card.select_one(".product-title")
        title = title_el.get_text(strip=True) if title_el else ""
        price_el = card.select_one("span.lfloat.product-price") or card.select_one(".product-price")
        price_text = price_el.get_text(strip=True) if price_el else "0"
        price_val = _parse_price(price_text)
        print(f"TITLE: {title} | RAW PRICE: '{price_text}' | PARSED: {price_val}")

if __name__ == "__main__":
    test_html_scrape("Running Shoes")
