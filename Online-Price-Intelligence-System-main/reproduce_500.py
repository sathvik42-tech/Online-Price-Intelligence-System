
import asyncio
import os
import sys

# Ensure the root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.app.fast_search import fast_search_all_platforms
from backend.utils.aggregation import aggregate_prices
from backend.utils.scoring import find_best_deal
from backend.reporting import calculate_stats

async def test_search():
    q_key = "Wireless Mouse"
    print(f"Testing search for: {q_key}")
    
    try:
        print("Calling fast_search_all_platforms...")
        raw_results = await fast_search_all_platforms(q_key, timeout=25)
        
        print(f"Raw results type: {type(raw_results)}")
        if hasattr(raw_results, 'items'):
             print(f"Platforms found: {list(raw_results.keys())}")
        else:
             print("ERROR: raw_results does not have .items()!!")
             print(f"Raw results value: {raw_results}")
             return

        print("Calling aggregate_prices...")
        aggregated = aggregate_prices(raw_results, query=q_key)
        print(f"Aggregated count: {len(aggregated)}")
        
        print("Calling find_best_deal...")
        best_deal = find_best_deal(aggregated)
        print(f"Best deal: {best_deal.get('title') if best_deal else 'None'}")
        
        print("Calling calculate_stats...")
        stats = calculate_stats(aggregated)
        print(f"Stats: {stats}")
        
        print("SUCCESS! No crash.")
        
    except Exception as e:
        print(f"CRASH: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search())
