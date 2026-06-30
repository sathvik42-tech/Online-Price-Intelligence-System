import logging
import random
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]


def _parse_price(price_text: str) -> float:
    if not price_text:
        return 0.0
    cleaned = re.sub(r"[^\d.]", "", str(price_text))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def search_bestbuy(keyword: str) -> List[Dict[str, Any]]:
    """
    Searches BestBuy.com using their internal search API.
    Falls back to empty list on any error or bot block.
    Returns prices in USD (conversion is handled in aggregation).
    """
    products = []
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.bestbuy.com/",
    }

    try:
        logger.info(f"Searching BestBuy for: {keyword}")

        # HTML scrape is generally more reliable across networks/regions than BestBuy's internal JSON API.
        products = _scrape_bestbuy_html(keyword, headers)

        # If HTML returned nothing, try the internal JSON API as a best-effort fallback.
        if not products:
            api_url = (
                f"https://www.bestbuy.com/api/2.0/json/search"
                f"?q={keyword.replace(' ', '+')}&start=0&pageSize=10"
                f"&sort=BEST_MATCH,ASC&ads=false"
            )
            resp = requests.get(api_url, headers=headers, timeout=10)

            if resp.status_code == 200:
                try:
                    data = resp.json()
                except Exception:
                    data = {}

                items = data.get("products", []) or []
                for item in items[:8]:
                    try:
                        title = item.get("name", "")
                        if not title:
                            continue
                        price_usd = item.get("salePrice") or item.get("regularPrice") or 0
                        sku = item.get("sku", "")
                        url = f"https://www.bestbuy.com/site/-/{sku}.p?skuId={sku}" if sku else "https://www.bestbuy.com"
                        image_url = item.get("image", "")
                        rating = item.get("customerReviewAverage", 4.0) or 4.0
                        products.append({
                            "platform": "bestbuy",
                            "title": title,
                            "price": float(price_usd) if price_usd else 0.0,
                            "currency": "USD",
                            "availability": "In Stock" if item.get("inStoreAvailability") or item.get("onlineAvailability") else "Check Website",
                            "product_url": url,
                            "image_url": image_url,
                            "seller_rating": str(round(float(rating), 1)),
                            "shipping_info": "Free Shipping" if item.get("freeShipping") else "Standard Shipping",
                        })
                    except Exception:
                        continue
            else:
                logger.warning(f"BestBuy API returned status {resp.status_code}")

    except requests.exceptions.Timeout:
        logger.warning("BestBuy search timed out.")
    except Exception as e:
        logger.error(f"BestBuy search failed: {e}")

    logger.info(f"BestBuy: found {len(products)} products for '{keyword}'")
    return products


def _scrape_bestbuy_html(keyword: str, headers: dict) -> List[Dict[str, Any]]:
    """HTML fallback scraper for BestBuy."""
    products = []
    try:
        url = f"https://www.bestbuy.com/site/searchpage.jsp?st={keyword.replace(' ', '+')}"
        # BestBuy can be slow or blocked on some networks; fail fast to avoid stalling the whole scan.
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select("li.sku-item")
        for item in items[:8]:
            try:
                title_el = item.select_one(".sku-title a") or item.select_one("h4.sku-header a")
                title = title_el.get_text(strip=True) if title_el else ""
                if not title:
                    continue
                price_el = item.select_one(".priceView-customer-price span") or item.select_one(".priceView-price span")
                price_usd = _parse_price(price_el.get_text(strip=True) if price_el else "0")
                link_el = item.select_one(".sku-title a") or item.select_one("h4.sku-header a")
                link = "https://www.bestbuy.com" + link_el.get("href", "") if link_el else "https://www.bestbuy.com"
                rating_el = item.select_one(".c-ratings-reviews .ugc-ratings-link")
                rating = "4.0"
                if rating_el:
                    match = re.search(r"([\d.]+)", rating_el.get("aria-label", ""))
                    if match:
                        rating = match.group(1)
                products.append({
                    "platform": "bestbuy",
                    "title": title,
                    "price": float(price_usd) if price_usd else 0.0,
                    "currency": "USD",
                    "availability": "In Stock",
                    "product_url": link,
                    "image_url": "",
                    "seller_rating": rating,
                    "shipping_info": "Free Shipping",
                })
            except Exception:
                continue
    except Exception as e:
        logger.error(f"BestBuy HTML scrape failed: {e}")
    return products


if __name__ == "__main__":
    results = search_bestbuy("analog watch")
    for r in results:
        print(r)
