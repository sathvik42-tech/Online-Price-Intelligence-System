import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from backend.app.fast_search import fast_search_all_platforms
import json

async def main():
    print("Starting search for 'Wireless Mouse'...")
    try:
        results = await fast_search_all_platforms("Wireless Mouse")
        total = sum(len(v) for v in results.values())
        print(f"Search completed. Found {total} items.")
        for platform, items in results.items():
            print(f"  - {platform}: {len(items)} items")
    except Exception as e:
        print(f"\n[!] SEARCH FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
