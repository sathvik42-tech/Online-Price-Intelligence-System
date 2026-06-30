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
    text_str = str(text)
    # Remove common currency prefixes that might contain dots (e.g. Rs.)
    # We do a case-insensitive replacement of "Rs." with "Rs" to avoid the dot being kept
    text_str = re.sub(r"Rs\.", "Rs", text_str, flags=re.I)
    
    cleaned = re.sub(r"[^\d.]", "", text_str)
    # If multiple dots, keep only the first one
    if cleaned.count('.') > 1:
        parts = cleaned.split('.')
        cleaned = parts[0] + '.' + ''.join(parts[1:])
    try:
        val = float(cleaned) if cleaned else 0.0
        return val
    except ValueError:
        return 0.0


def search_snapdeal(keyword: str) -> List[Dict[str, Any]]:
    """
    Searches Snapdeal.com using their JSON API endpoint.
    Returns prices in INR.
    """
    q = (keyword or "").strip()
    if not q:
        return []

    products: List[Dict[str, Any]] = []

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-IN,en;q=0.9",
        "Referer": "https://www.snapdeal.com/",
    }

    try:
        logger.info(f"Searching Snapdeal for: {q}")
        # Snapdeal's public search API
        api_url = (
            f"https://www.snapdeal.com/acors/json/product/get/search"
            f"?keyword={q.replace(' ', '%20')}&numFound=10&start=0&sort=rlvncy"
        )
        resp = requests.get(api_url, headers=headers, timeout=12)
        if resp.status_code == 200:
            try:
                data = resp.json()
                items = data.get("products", [])
            except Exception:
                items = []

            for item in items[:8]:
                try:
                    title = item.get("title") or item.get("name") or ""
                    if not title:
                        continue
                    raw_p = item.get("discounted_price") or item.get("sellingPrice") or 0
                    price_inr = _parse_price(raw_p)
                    # Heuristic: If price is a small decimal (e.g. 0.476), it's likely scaled in thousands
                    if 0 < price_inr < 10:
                        price_inr *= 1000
                    product_url = item.get("productUrl") or item.get("url") or ""
                    if product_url and not product_url.startswith("http"):
                        product_url = "https://www.snapdeal.com" + product_url
                    image_url = item.get("imageUrl") or item.get("imageUrls", [None])[0] or ""
                    rating = str(item.get("avgRating") or 4.0)

                    if price_inr <= 0:
                        logger.warning(f"Snapdeal: Skipping zero price item: {title}")
                        continue

                    products.append({
                        "platform": "snapdeal",
                        "title": title.strip(),
                        "price": price_inr,
                        "currency": "INR",
                        "availability": "In Stock",
                        "product_url": product_url or "https://www.snapdeal.com",
                        "image_url": image_url,
                        "seller_rating": rating,
                        "shipping_info": "Free Shipping Available",
                    })
                except Exception as e:
                    logger.debug(f"Snapdeal item parse error: {e}")
                    continue

        # Fallback: HTML scraping if API returned nothing
        if not products:
            products = _scrape_snapdeal_html(q, headers)

    except requests.exceptions.Timeout:
        logger.warning("Snapdeal search timed out.")
    except Exception as e:
        logger.error(f"Snapdeal search failed: {e}")

    logger.info(f"Snapdeal: found {len(products)} products for '{q}'")
    return products


def _scrape_snapdeal_html(keyword: str, headers: dict) -> List[Dict[str, Any]]:
    """HTML fallback scraper for Snapdeal."""
    products = []
    try:
        url = f"https://www.snapdeal.com/search?keyword={keyword.replace(' ', '%20')}&sort=rlvncy"
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("div.product-tuple-listing") or soup.select("div.favDp")

        seen = set()
        for card in cards[:10]:
            if len(products) >= 8:
                break
            try:
                title_el = card.select_one("p.product-title") or card.select_one(".product-title")
                title = title_el.get_text(strip=True) if title_el else ""
                if not title:
                    continue

                price_el = card.select_one("span.lfloat.product-price") or card.select_one(".product-price")
                price = _parse_price(price_el.get_text(strip=True) if price_el else "0")

                link_el = card.select_one("a.dp-widget-link") or card.select_one("a[href]")
                link = ""
                if link_el:
                    href = link_el.get("href", "")
                    link = href if href.startswith("http") else "https://www.snapdeal.com" + href

                img_el = card.select_one("img.product-image") or card.select_one("img")
                image_url = (img_el.get("src") or img_el.get("data-src") or "") if img_el else ""

                key = (title.lower(), link)
                if key in seen:
                    continue
                seen.add(key)

                if price <= 0:
                    continue

                products.append({
                    "platform": "snapdeal",
                    "title": title,
                    "price": price,
                    "currency": "INR",
                    "availability": "In Stock",
                    "product_url": link or "https://www.snapdeal.com",
                    "image_url": image_url,
                    "seller_rating": "4.0",
                    "shipping_info": "Free Shipping Available",
                })
            except Exception:
                continue

    except Exception as e:
        logger.error(f"Snapdeal HTML scrape failed: {e}")
    return products


if __name__ == "__main__":
    results = search_snapdeal("pencil")
    for r in results:
        print(r.get("title"), r.get("price"), r.get("product_url"))
