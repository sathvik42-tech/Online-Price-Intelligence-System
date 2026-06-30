import logging
import random
import re
import time
import requests
from typing import List, Dict, Any
import json
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

def _parse_price(price_text: str) -> float:
    """Extract numeric price from a price string."""
    if not price_text:
        return 0.0
    cleaned = re.sub(r"[^\d.]", "", str(price_text))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def search_target(keyword: str) -> List[Dict[str, Any]]:
    """
    Searches Target.com using their internal API endpoint.
    Falls back to empty list on any error or block.
    Returns prices in USD (conversion is handled in aggregation).
    """
    products = []
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.target.com/",
    }

    try:
        logger.info(f"Searching Target for: {keyword}")
        # Target's internal search API
        api_url = (
            "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2"
            f"?key=9f36aeafbe60771e321a7cc95a78140772ab3e96"
            f"&channel=WEB&count=10&default_purchasability_filter=true"
            f"&include_sponsored=false&keyword={keyword.replace(' ', '%20')}"
            f"&offset=0&platform=desktop&pricing_store_id=3991"
            f"&scheduled_delivery_store_id=3991&store_ids=3991&useragent=Mozilla"
            f"&visitor_id=01874FA04A9E0201A2338CE4FC5C8F30"
        )
        resp = requests.get(api_url, headers=headers, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("data", {}).get("search", {}).get("products", [])
            for item in items[:8]:
                try:
                    title = item.get("item", {}).get("product_description", {}).get("title", "")
                    if not title:
                        continue
                    price_usd = item.get("price", {}).get("current_retail", 0) or \
                                item.get("price", {}).get("reg_retail", 0) or 0
                    tcin = item.get("item", {}).get("tcin", "")
                    url = f"https://www.target.com/p/-/A-{tcin}" if tcin else "https://www.target.com"
                    image_url = item.get("item", {}).get("enrichment", {}).get("images", {}).get("primary_image_url", "")
                    rating = item.get("ratings_and_reviews", {}).get("statistics", {}).get("rating", {}).get("average", 4.2)
                    products.append({
                        "platform": "target",
                        "title": title,
                        "price": float(price_usd) if price_usd else 0.0,
                        "currency": "USD",
                        "availability": "In Stock",
                        "product_url": url,
                        "image_url": image_url,
                        "seller_rating": str(round(float(rating or 4.2), 1)),
                        "shipping_info": "Standard Shipping",
                    })
                except Exception:
                    continue
        else:
            logger.warning(f"Target API returned status {resp.status_code}")
            products = _scrape_target_html(keyword, headers)

    except requests.exceptions.Timeout:
        logger.warning("Target search timed out.")
        products = _scrape_target_html(keyword, headers)
    except Exception as e:
        logger.error(f"Target search failed: {e}")

    logger.info(f"Target: found {len(products)} products for '{keyword}'")
    return products


def _scrape_target_html(keyword: str, headers: dict) -> List[Dict[str, Any]]:
    """
    HTML fallback scraper for Target.com.
    Target pages are Next.js and embed product data in a __NEXT_DATA__ script.
    """
    q = (keyword or "").strip()
    if not q:
        return []

    url = f"https://www.target.com/s?searchTerm={q.replace(' ', '%20')}"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        script = soup.select_one("script#__NEXT_DATA__")
        if not script or not script.string:
            return []

        data = json.loads(script.string)

        # Walk the JSON tree and pull dicts that look like products (title + tcin)
        def walk(obj):
            stack = [obj]
            while stack:
                cur = stack.pop()
                yield cur
                if isinstance(cur, dict):
                    stack.extend(cur.values())
                elif isinstance(cur, list):
                    stack.extend(cur)

        items = []
        for node in walk(data):
            if not isinstance(node, dict):
                continue
            title = node.get("title") or node.get("name") or ""
            tcin = node.get("tcin") or node.get("id") or ""
            if title and tcin and isinstance(title, str):
                items.append(node)

        products = []
        seen = set()
        for node in items:
            if len(products) >= 8:
                break
            try:
                title = (node.get("title") or node.get("name") or "").strip()
                tcin = str(node.get("tcin") or node.get("id") or "").strip()
                if not title or not tcin:
                    continue

                key = (title.lower(), tcin)
                if key in seen:
                    continue
                seen.add(key)

                # price can appear under various keys
                price = 0.0
                for price_key in ("current_retail", "currentPrice", "current_price", "price"):
                    if price_key in node:
                        price = _parse_price(node.get(price_key))
                        if price:
                            break
                if not price and isinstance(node.get("price"), dict):
                    price = _parse_price(node["price"].get("current_retail") or node["price"].get("formatted_current_price"))

                image_url = ""
                img = node.get("primary_image_url") or node.get("image") or node.get("image_url")
                if isinstance(img, str):
                    image_url = img
                elif isinstance(img, dict):
                    image_url = img.get("url") or img.get("src") or ""

                products.append({
                    "platform": "target",
                    "title": title,
                    "price": float(price) if price else 0.0,
                    "currency": "USD",
                    "availability": "In Stock",
                    "product_url": f"https://www.target.com/p/-/A-{tcin}",
                    "image_url": image_url,
                    "seller_rating": "4.2",
                    "shipping_info": "Standard Shipping",
                })
            except Exception:
                continue

        return products
    except Exception as e:
        logger.error(f"Target HTML scrape failed: {e}")
        return []


if __name__ == "__main__":
    results = search_target("analog watch")
    for r in results:
        print(r)
