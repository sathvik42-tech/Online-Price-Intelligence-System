import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

from scrapers.amazon_scraper import search_amazon
from scrapers.ebay_scraper import search_ebay
from scrapers.flipkart_scraper import search_flipkart
from scrapers.meesho_scraper import search_meesho
from scrapers.snapdeal_scraper import search_snapdeal
from scrapers.walmart_scraper import search_walmart
from scrapers.target_scraper import search_target
from scrapers.bestbuy_scraper import search_bestbuy


SCRAPERS = [
    ("flipkart", search_flipkart, 25),
    ("snapdeal", search_snapdeal, 15),
    ("meesho", search_meesho, 15),
    ("amazon", search_amazon, 30),
    ("walmart", search_walmart, 20),
    ("target", search_target, 20),
    ("bestbuy", search_bestbuy, 20),
    ("ebay", search_ebay, 35),
]


def _run(name, fn, keyword, timeout):
    start = time.time()
    try:
        results = fn(keyword)
        count = len(results) if isinstance(results, list) else 0
        return {
            "name": name,
            "ok": True,
            "count": count,
            "seconds": round(time.time() - start, 2),
            "error": None,
        }
    except Exception as e:
        return {
            "name": name,
            "ok": False,
            "count": 0,
            "seconds": round(time.time() - start, 2),
            "error": str(e),
        }


def main():
    keyword = "headphones"
    print(f"Scraper verification for query: {keyword}\n")

    results = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = []
        for name, fn, timeout in SCRAPERS:
            futures.append((name, timeout, executor.submit(_run, name, fn, keyword, timeout)))

        for name, timeout, fut in futures:
            try:
                results.append(fut.result(timeout=timeout))
            except FutureTimeout:
                results.append({
                    "name": name,
                    "ok": False,
                    "count": 0,
                    "seconds": timeout,
                    "error": f"timeout after {timeout}s",
                })
            except Exception as e:
                results.append({
                    "name": name,
                    "ok": False,
                    "count": 0,
                    "seconds": 0,
                    "error": str(e),
                })

    print("Summary")
    print("-" * 60)
    for r in results:
        status = "OK" if r["ok"] else "FAIL"
        count = str(r["count"]).rjust(3)
        print(f"{r['name']:<10} {status:<4} items={count} time={r['seconds']}s error={r['error'] or '-'}")

    print("\nNotes")
    print("- Amazon/Flipkart/eBay use Selenium and need Chrome + webdriver.")
    print("- If those fail, the rest should still return quickly.")


if __name__ == "__main__":
    main()
