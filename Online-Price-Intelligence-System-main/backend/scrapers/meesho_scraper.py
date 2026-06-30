import logging
import random
import re
import json
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]


def _parse_price(text: str) -> float:
    if not text:
        return 0.0
    cleaned = re.sub(r"[^\d.]", "", str(text))
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def search_meesho(keyword: str) -> List[Dict[str, Any]]:
    """
    Searches Meesho.com using their GraphQL API.
    Returns prices in INR.
    """
    q = (keyword or "").strip()
    if not q:
        return []

    products: List[Dict[str, Any]] = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://meesho.com",
        "Referer": "https://meesho.com/",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    try:
        logger.info(f"Searching Meesho for: {q}")

        # Meesho GraphQL endpoint
        payload = {
            "operationName": "SearchResultsFeed",
            "variables": {
                "filters": [],
                "page": 1,
                "query": q,
                "screen": "SEARCH",
                "searchType": "manual",
                "sortOrder": "RELEVANCE",
            },
            "query": (
                "query SearchResultsFeed($query: String!, $page: Int, $sortOrder: String, "
                "$filters: [FilterQueryInput], $screen: String, $searchType: String) { "
                "getFeedData(query: $query, page: $page, sortOrder: $sortOrder, "
                "filters: $filters, screen: $screen, searchType: $searchType) { "
                "page { products { id name price images { url } catalog { id urlSlug } } } } }"
            ),
        }

        resp = requests.post(
            "https://meesho.com/api/v1/products/search",
            json=payload, headers=headers, timeout=12
        )

        if resp.status_code == 200:
            try:
                data = resp.json()
                items = (
                    data.get("data", {})
                        .get("getFeedData", {})
                        .get("page", {})
                        .get("products", [])
                )
            except Exception:
                items = []

            for item in items[:8]:
                try:
                    title = item.get("name") or ""
                    if not title:
                        continue
                    raw_p = item.get("price") or 0
                    price_inr = _parse_price(raw_p)
                    # Heuristic: If price is a small decimal (e.g. 0.476), it's likely scaled in thousands
                    if 0 < price_inr < 10:
                        price_inr *= 1000
                    slug = (item.get("catalog") or {}).get("urlSlug") or str(item.get("id", ""))
                    product_url = f"https://meesho.com/{slug}" if slug else "https://meesho.com"
                    images = item.get("images") or []
                    image_url = images[0].get("url", "") if images else ""

                    products.append({
                        "platform": "meesho",
                        "title": title.strip(),
                        "price": price_inr,
                        "currency": "INR",
                        "availability": "In Stock",
                        "product_url": product_url,
                        "image_url": image_url,
                        "seller_rating": "4.0",
                        "shipping_info": "Free Delivery Available",
                    })
                except Exception:
                    continue

        # Fallback: scrape search page HTML
        if not products:
            products = _scrape_meesho_html(q, headers)

    except requests.exceptions.Timeout:
        logger.warning("Meesho search timed out.")
    except Exception as e:
        logger.error(f"Meesho search failed: {e}")

    logger.info(f"Meesho: found {len(products)} products for '{q}'")
    return products


def _scrape_meesho_html(keyword: str, headers: dict) -> List[Dict[str, Any]]:
    """HTML fallback: parse Meesho search page for __NEXT_DATA__."""
    products = []
    try:
        url = f"https://meesho.com/search?q={keyword.replace(' ', '%20')}&searchType=manual"
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        script = soup.select_one("script#__NEXT_DATA__")
        if not script or not script.string:
            return []

        data = json.loads(script.string)

        # Walk the __NEXT_DATA__ for product dictionaries
        def walk(obj):
            stack = [obj]
            while stack:
                cur = stack.pop()
                yield cur
                if isinstance(cur, dict):
                    stack.extend(cur.values())
                elif isinstance(cur, list):
                    stack.extend(cur)

        seen = set()
        for node in walk(data):
            if len(products) >= 8:
                break
            if not isinstance(node, dict):
                continue
            name = node.get("name") or node.get("title") or ""
            price_raw = node.get("price") or node.get("discountedPrice") or ""
            if not name or not price_raw:
                continue
            if name in seen:
                continue
            seen.add(name)

            price = _parse_price(price_raw)
            slug = node.get("urlSlug") or ""
            product_url = f"https://meesho.com/{slug}" if slug else "https://meesho.com"
            images = node.get("images") or []
            image_url = ""
            if isinstance(images, list) and images:
                first = images[0]
                if isinstance(first, dict):
                    image_url = first.get("url") or ""
                elif isinstance(first, str):
                    image_url = first

            products.append({
                "platform": "meesho",
                "title": name.strip(),
                "price": price,
                "currency": "INR",
                "availability": "In Stock",
                "product_url": product_url,
                "image_url": image_url,
                "seller_rating": "4.0",
                "shipping_info": "Free Delivery Available",
            })

    except Exception as e:
        logger.error(f"Meesho HTML scrape failed: {e}")
    return products


if __name__ == "__main__":
    results = search_meesho("pencil")
    for r in results:
        print(r.get("title"), r.get("price"), r.get("product_url"))
