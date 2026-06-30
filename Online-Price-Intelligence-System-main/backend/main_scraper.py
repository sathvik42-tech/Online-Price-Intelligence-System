import concurrent.futures
import json
import logging

from .app.ebay_api import search_ebay_products as search_ebay_api
from .scrapers.amazon_scraper import search_amazon
from .scrapers.bestbuy_scraper import search_bestbuy
from .scrapers.ebay_scraper import search_ebay
from .scrapers.flipkart_scraper import search_flipkart
from .scrapers.meesho_scraper import search_meesho
from .scrapers.snapdeal_scraper import search_snapdeal
from .scrapers.target_scraper import search_target
from .scrapers.walmart_scraper import search_walmart

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def _standardize_ebay_api(items):
    """Convert eBay API results to the common scraper format."""
    standardized = []
    for item in items:
        standardized.append(
            {
                "platform": "ebay",
                "title": item.get("title", ""),
                "price": item.get("price", 0),
                "currency": item.get("currency", "USD"),
                "availability": "In Stock",
                "product_url": item.get("itemWebUrl", ""),
                "image_url": item.get("image", {}).get("imageUrl", "")
                if isinstance(item.get("image"), dict)
                else "",
                "seller_rating": "4.0",
                "shipping_info": "Check Website",
            }
        )
    return standardized


def _run_scraper(name, fn, keyword):
    """Run a single scraper, catching all exceptions."""
    try:
        result = fn(keyword)
        logger.info(f"{name}: returned {len(result)} items")
        return name, result
    except Exception as e:
        logger.error(f"{name} scraper crashed: {e}")
        return name, []


def search_all_platforms(keyword: str, deep_scan: bool = False, timeout: int = 45):
    """
    Parallel search across platforms with a hard global timeout.

    Why this exists:
    - Selenium scrapers can hang for minutes due to bot protection / slow page loads.
    - A naive `as_completed()` loop can block forever waiting for stuck futures.

    Behavior:
    - deep_scan=False (default): run requests/API scrapers + eBay API only, enforce a global timeout,
      and return partial results quickly.
    - deep_scan=True: also run Selenium scrapers (Amazon/Flipkart and eBay fallback) and wait for them.
    """
    all_results = {}
    logger.info(
        f"Starting multi-platform search for: '{keyword}' (deep_scan={deep_scan}, timeout={timeout}s)"
    )

    # eBay: try API first (fast, reliable)
    ebay_results = []
    try:
        logger.info("Attempting eBay Production API...")
        ebay_api_results = search_ebay_api(keyword)
        if ebay_api_results and "error" not in ebay_api_results[0]:
            logger.info("eBay API search successful.")
            ebay_results = _standardize_ebay_api(ebay_api_results)
        else:
            raise ValueError("eBay API returned error")
    except Exception:
        if deep_scan:
            logger.warning("eBay API failed. Falling back to Selenium...")
            _, ebay_results = _run_scraper("ebay", search_ebay, keyword)
        else:
            logger.warning("eBay API failed. Skipping Selenium fallback (deep_scan=False).")
            ebay_results = []
    all_results["ebay"] = ebay_results

    # Requests/API scrapers (fast and already have request timeouts internally)
    scrapers_to_run = [
        ("snapdeal", search_snapdeal),
        ("meesho", search_meesho),
        ("walmart", search_walmart),
        ("target", search_target),
        ("bestbuy", search_bestbuy),
    ]

    # Selenium scrapers are opt-in (avoid hanging requests by default)
    if deep_scan:
        scrapers_to_run.extend(
            [
                ("amazon", search_amazon),
                ("flipkart", search_flipkart),
            ]
        )

    executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=min(len(scrapers_to_run), 6) or 1
    )
    future_to_name = {}
    try:
        future_to_name = {
            executor.submit(_run_scraper, name, fn, keyword): name
            for name, fn in scrapers_to_run
        }

        done, not_done = concurrent.futures.wait(
            future_to_name.keys(),
            timeout=timeout,
            return_when=concurrent.futures.ALL_COMPLETED,
        )

        for fut in done:
            name = future_to_name[fut]
            try:
                _, result = fut.result()
                all_results[name] = result
            except Exception as e:
                logger.error(f"{name} future failed: {e}")
                all_results[name] = []

        # Anything still running becomes empty so callers can respond quickly.
        for fut in not_done:
            name = future_to_name[fut]
            logger.warning(f"{name} timed out after {timeout}s (deep_scan={deep_scan})")
            all_results[name] = []
            fut.cancel()
    finally:
        # If deep_scan is off, never block waiting for slow threads (especially Selenium).
        try:
            executor.shutdown(wait=deep_scan, cancel_futures=True)
        except TypeError:
            executor.shutdown(wait=deep_scan)

    # Ensure all platforms are present in results
    for name, _ in scrapers_to_run:
        all_results.setdefault(name, [])

    for platform, items in all_results.items():
        logger.info(f"  {platform.upper()}: {len(items)} items")

    return all_results


import sys


def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter product to search (default 'laptop'): ") or "laptop"

    results = search_all_platforms(query)

    print(f"\nSearch Results for: {query}")
    print("=" * 30)
    for platform, items in results.items():
        print(f"{platform.upper()}: found {len(items)} items")

    with open("results_summary.json", "w") as f:
        json.dump(results, f, indent=4)
        print("\nFull results saved to 'results_summary.json'")


if __name__ == "__main__":
    main()

