import re
from backend.utils.normalization import normalize_name

# Platforms that price in USD — convert to INR
USD_PLATFORMS = {"ebay"}
USD_TO_INR = 83
INR = "INR"


def _parse_float(value):
    """Clean and convert price/shipping strings to float."""
    if value is None or value == "" or value == "N/A":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    
    text_val = str(value)
    # Remove dots in currency prefixes (e.g. Rs.) to avoid them becoming leading decimals
    text_val = re.sub(r"(?i)Rs\.", "Rs", text_val)
    
    cleaned = re.sub(r'[^\d.]', '', text_val)
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def aggregate_prices(results, query=None):
    """
    Aggregates product results from multiple platforms into a unified list.
    - Normalizes product names
    - Converts all prices to INR
    - Filters out highly irrelevant results if a query is provided
    - Unifies keys: title, product_url, currency, image_url, platform, score, seller_rating
    """
    from backend.utils.normalization import fuzzy_match
    aggregated_list = []

    for platform, items in results.items():
        if not isinstance(items, list):
            continue

        platform_lower = platform.lower()
        is_usd = platform_lower in USD_PLATFORMS

        for item in items:
            # Resolve title
            title = (
                item.get("title")
                or item.get("name")
                or item.get("original_name")
                or ""
            )

            # Handle missing/placeholder titles
            if not title or title.strip().upper() in ("N/A", "UNKNOWN", ""):
                title = query if query else "Unknown Product"

            # Fuzzy match filter — drop completely unrelated items
            if query and title != query and fuzzy_match(title, query) < 0.15:
                continue

            # Resolve URL
            product_url = item.get("product_url") or item.get("url") or "#"

            # Resolve image
            image_url = item.get("image_url") or item.get("image") or ""

            # Price — convert USD → INR if needed
            raw_price = _parse_float(item.get("price"))
            if is_usd and raw_price > 0:
                price = round(raw_price * USD_TO_INR, 2)
            else:
                price = raw_price

            # Shipping
            shipping_raw = item.get("shipping_info") or item.get("shipping") or "0"
            shipping = _parse_float(shipping_raw)
            # Convert shipping too if USD platform
            if is_usd and shipping > 0:
                shipping = round(shipping * USD_TO_INR, 2)

            # Safety check: skip items with zero or negative price
            if price <= 0:
                continue

            # Rating — keep as string, normalise to 0–5 scale
            seller_rating = item.get("seller_rating") or "N/A"

            availability = item.get("availability") or "In Stock"

            unified_item = {
                "platform": platform.capitalize(),
                "title": title,
                "original_name": title,
                "normalized_name": normalize_name(title),
                "price": price,
                "shipping": shipping,
                "total_cost": round(price + shipping, 2),
                "product_url": product_url,
                "image_url": image_url,
                "seller_rating": seller_rating,
                "availability": availability,
                "currency": INR,
                "score": 0,
            }

            aggregated_list.append(unified_item)

    return aggregated_list
