import json
import logging
import random
import re
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

try:
    from backend.utils.headers import USER_AGENTS
except ImportError:
    from utils.headers import USER_AGENTS

logger = logging.getLogger(__name__)


def _parse_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r"[^\d.]", "", str(value))
    try:
        return float(cleaned) if cleaned else 0.0
    except Exception:
        return 0.0


def _extract_next_data(html: str) -> Optional[dict]:
    soup = BeautifulSoup(html, "html.parser")
    script = soup.select_one('script#__NEXT_DATA__')
    if not script or not script.string:
        return None
    try:
        return json.loads(script.string)
    except Exception:
        return None


def _walk(obj: Any):
    """Yield all nested dict/list nodes."""
    stack = [obj]
    while stack:
        cur = stack.pop()
        yield cur
        if isinstance(cur, dict):
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)


def _extract_items(next_data: dict) -> List[dict]:
    """
    Walmart search page embeds product data inside __NEXT_DATA__.
    The exact shape can change, so we walk the tree and pick likely product dicts.
    """
    items: List[dict] = []
    for node in _walk(next_data):
        if not isinstance(node, dict):
            continue
        # common keys seen in Walmart Next.js payloads
        if "name" in node and ("canonicalUrl" in node or "productPageUrl" in node or "usItemId" in node):
            items.append(node)
        elif node.get("__typename") in {"Product", "ProductUi"} and "name" in node:
            items.append(node)
    return items


def search_walmart(keyword: str) -> List[Dict[str, Any]]:
    """
    Scrape Walmart search results using request + __NEXT_DATA__ parsing.
    This is much faster/less fragile than Selenium and avoids long timeouts.
    Returns prices in USD (conversion is handled in aggregation).
    """
    q = (keyword or "").strip()
    if not q:
        return []

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.walmart.com/",
    }

    url = f"https://www.walmart.com/search?q={q.replace(' ', '+')}"
    try:
        logger.info(f"Searching Walmart for: {q}")
        # Walmart blocks many automated requests; fail fast to avoid stalling comparisons.
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code != 200:
            logger.warning(f"Walmart returned status {resp.status_code}")
            return []

        if "Robot or Human" in resp.text or "blocked" in resp.text.lower():
            logger.warning("Walmart bot detection page returned.")
            return []

        next_data = _extract_next_data(resp.text)
        if not next_data:
            logger.warning("Walmart __NEXT_DATA__ not found.")
            return []

        raw_items = _extract_items(next_data)
        products: List[Dict[str, Any]] = []
        seen = set()

        for item in raw_items:
            if len(products) >= 8:
                break
            try:
                title = (item.get("name") or "").strip()
                if not title:
                    continue

                # price can appear as: priceInfo.currentPrice.price, price, or currentPrice
                price = 0.0
                pi = item.get("priceInfo") or {}
                cp = (pi.get("currentPrice") or {}) if isinstance(pi, dict) else {}
                price = _parse_float(cp.get("price") if isinstance(cp, dict) else 0.0) or _parse_float(item.get("price"))
                if price <= 0:
                    # some nodes store min/max price structures
                    price = _parse_float((item.get("priceRange") or {}).get("minPrice"))

                canonical = item.get("canonicalUrl") or item.get("productPageUrl") or ""
                product_url = canonical
                if product_url and not product_url.startswith("http"):
                    product_url = "https://www.walmart.com" + product_url
                if not product_url:
                    us_item_id = item.get("usItemId") or item.get("id")
                    if us_item_id:
                        product_url = f"https://www.walmart.com/ip/{us_item_id}"

                # image
                image_url = ""
                img = item.get("imageInfo") or item.get("image")
                if isinstance(img, dict):
                    image_url = img.get("thumbnailUrl") or img.get("url") or ""
                elif isinstance(img, str):
                    image_url = img

                key = (title.lower(), product_url)
                if key in seen:
                    continue
                seen.add(key)

                products.append({
                    "platform": "walmart",
                    "title": title,
                    "price": price,
                    "currency": "USD",
                    "availability": "In Stock",
                    "product_url": product_url or "https://www.walmart.com",
                    "image_url": image_url,
                    "seller_rating": "4.0",
                    "shipping_info": "Standard Shipping",
                })
            except Exception:
                continue

        logger.info(f"Walmart: found {len(products)} products for '{q}'")
        return products

    except requests.exceptions.Timeout:
        logger.warning("Walmart search timed out.")
        return []
    except Exception as e:
        logger.error(f"Walmart search failed: {e}")
        return []


if __name__ == "__main__":
    results = search_walmart("pencil")
    for r in results:
        print(r.get("title"), r.get("price"), r.get("product_url"))
