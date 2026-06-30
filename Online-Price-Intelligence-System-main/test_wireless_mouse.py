
import asyncio
import os
import sys
import logging

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure the root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.app.fast_search import fast_search_all_platforms
from utils.aggregation import aggregate_prices
from utils.scoring import find_best_deal
from reporting import calculate_stats

async def debug_search():
    q_key = "Wireless Mouse"
    print(f"DEBUG: Starting search for: {q_key}")
    
    try:
        print("DEBUG: Calling fast_search_all_platforms...")
        raw_results = await fast_search_all_platforms(q_key, timeout=30)
        
        for platform, items in raw_results.items():
            print(f"DEBUG: {platform.upper()}: {len(items)} items")
            if items:
                print(f"  Sample: {items[0].get('title')} - {items[0].get('price')} {items[0].get('currency')}")

        print("DEBUG: Calling aggregate_prices...")
        aggregated = aggregate_prices(raw_results, query=q_key)
        print(f"DEBUG: Aggregated {len(aggregated)} items")
        
        if len(aggregated) > 0:
            print("DEBUG: Calling find_best_deal...")
            best_deal = find_best_deal(aggregated)
            print(f"DEBUG: Best deal: {best_deal.get('title') if best_deal else 'None'} from {best_deal.get('platform') if best_deal else 'N/A'}")
            
            print("DEBUG: Calling calculate_stats...")
            stats = calculate_stats(aggregated)
            print(f"DEBUG: Stats: {stats}")
        else:
            print("DEBUG: No items aggregated.")
            
        print("DEBUG: SUCCESS!")
        
    except Exception as e:
        print(f"DEBUG: CRASH DETECTED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_search())
