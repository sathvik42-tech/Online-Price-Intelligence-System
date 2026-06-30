
import asyncio
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.app.fast_search import fast_search_all_platforms
from utils.aggregation import aggregate_prices

async def test_search():
    query = "Wireless Mouse"
    print(f"Testing fast search for: {query}")
    try:
        raw_results = await fast_search_all_platforms(query)
        print(f"Fast search returned {len(raw_results)} platform entries.")
        
        aggregated = aggregate_prices(raw_results, query=query)
        print(f"Aggregated into {len(aggregated)} products.")
        
        for platform, items in raw_results.items():
            print(f"- {platform}: {len(items)} items")
            
    except Exception as e:
        print(f"Search failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search())
