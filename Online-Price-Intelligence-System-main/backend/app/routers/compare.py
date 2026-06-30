from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
import logging
import sys
import os

# Ensure the root directory is in sys.path to import modules from scrapers/ and utils/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

try:
    from backend.main_scraper import search_all_platforms
    from backend.utils.aggregation import aggregate_prices
    from backend.utils.scoring import find_best_deal
    from backend.reporting import calculate_stats
except ImportError:
    from main_scraper import search_all_platforms
    from utils.aggregation import aggregate_prices
    from utils.scoring import find_best_deal
    from reporting import calculate_stats

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/compare")
async def compare_prices(q: str = Query(..., description="The product to compare")):
    """
    Orchestrates search across multiple platforms and returns structured comparison data.
    """
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query string must be at least 2 characters long.")

    try:
        logger.info(f"Received comparison request for: {q}")
        
        # 1. Scrape all platforms
        raw_results = search_all_platforms(q)
        
        # 2. Aggregate and normalize results
        # search_all_platforms returns a dict {platform: [items...]}
        # We need a flat list for aggregation
        flat_results = []
        for platform, items in raw_results.items():
            flat_results.extend(items)
            
        if not flat_results:
            return {
                "query": q,
                "products": [],
                "best_deal": None,
                "statistics": {
                    "min_price": 0,
                    "max_price": 0,
                    "avg_price": 0,
                    "count": 0
                },
                "status": "no_results"
            }

        # 3. Process data
        aggregated_items = aggregate_prices(raw_results)
        best_deal = find_best_deal(aggregated_items)
        stats = calculate_stats(aggregated_items)

        return {
            "query": q,
            "products": aggregated_items,
            "best_deal": best_deal,
            "statistics": stats,
            "status": "success"
        }

    except Exception as e:
        logger.error(f"Error during price comparison for '{q}': {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
