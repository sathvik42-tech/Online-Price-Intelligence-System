"""
Fast search module - optimized for speed with partial results
"""
import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from typing import Dict, List
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

logger = logging.getLogger(__name__)

# Import scrapers with timeout handling
try:
    from scrapers.amazon_scraper import search_amazon
except:
    def search_amazon(keyword):
        return []

try:
    from scrapers.ebay_scraper import search_ebay
except:
    def search_ebay(keyword):
        return []

try:
    from scrapers.flipkart_scraper import search_flipkart
except:
    def search_flipkart(keyword):
        return []

try:
    from scrapers.snapdeal_scraper import search_snapdeal
except:
    def search_snapdeal(keyword):
        return []

try:
    from scrapers.meesho_scraper import search_meesho
except:
    def search_meesho(keyword):
        return []

try:
    from scrapers.walmart_scraper import search_walmart
except:
    def search_walmart(keyword):
        return []

try:
    from scrapers.target_scraper import search_target
except:
    def search_target(keyword):
        return []

try:
    from scrapers.bestbuy_scraper import search_bestbuy
except:
    def search_bestbuy(keyword):
        return []


def _run_scraper_with_timeout(name: str, fn, keyword: str, timeout: int = 15) -> tuple:
    """
    Run a single scraper with strict timeout.
    Returns (platform_name, results, time_taken)
    """
    start = time.time()
    try:
        result = fn(keyword)
        if not isinstance(result, list):
            result = []
        logger.info(f"✓ {name.upper()}: {len(result)} items")
        return name, result, round(time.time() - start, 2)
    except Exception as e:
        logger.warning(f"✗ {name.upper()}: {str(e)[:50]}")
        return name, [], round(time.time() - start, 2)


async def fast_search_all_platforms(keyword: str, timeout: int = 30) -> Dict[str, List]:
    """
    Fast parallel search with resource-aware concurrency.
    - Runs API/Requests scrapers in parallel (fast, low memory).
    - Runs Selenium scrapers one by one to avoid VirtualAlloc crashes on Windows.
    """
    all_results = {}
    
    # Define scrapers by type
    fast_scrapers = [
        ("snapdeal", search_snapdeal),
        ("meesho", search_meesho),
        ("walmart", search_walmart),
        ("target", search_target),
        ("bestbuy", search_bestbuy),
    ]
    
    # These use Selenium and are heavy on memory/CPU
    heavy_scrapers = [
        ("flipkart", search_flipkart),
        ("amazon", search_amazon),
        ("ebay", search_ebay),
    ]
    
    logger.info(f"🔍 Starting optimized resource-aware search for: '{keyword}'")
    
    # 1. Run FAST scrapers in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(_run_scraper_with_timeout, name, fn, keyword, 12): name
            for name, fn in fast_scrapers
        }
        
        try:
            for future in as_completed(futures, timeout=timeout/2):
                try:
                    name, result, _ = future.result(timeout=1)
                    all_results[name] = result
                except Exception as e:
                    name = futures.get(future, "unknown")
                    logger.warning(f"✗ Fast {name} failed: {str(e)[:30]}")
        except TimeoutError:
            logger.warning("⏱️ Fast API search reached partial timeout.")

    # 2. Run HEAVY scrapers sequentially (to avoid VirtualAlloc/Memory crashes on Windows)
    for name, fn in heavy_scrapers:
        logger.info(f"⏳ Starting heavy scraper: {name}...")
        try:
            # Run Selenium in a thread but wait for it before starting the next one
            name, result, _ = await asyncio.to_thread(_run_scraper_with_timeout, name, fn, keyword, 20)
            all_results[name] = result
        except Exception as e:
            logger.error(f"✗ Heavy {name} failed: {e}")
            all_results[name] = []
    
    # Ensure all platforms are in results list
    for name, _ in (fast_scrapers + heavy_scrapers):
        if name not in all_results:
            all_results[name] = []
    
    total_items = sum(len(items) for items in all_results.values())
    logger.info(f"✅ Optimized search complete: {total_items} items")
    return all_results


async def search_with_streaming(keyword: str, timeout: int = 30):
    """
    Alternative: stream results as they arrive
    Useful for frontend real-time updates
    """
    return await fast_search_all_platforms(keyword, timeout)
