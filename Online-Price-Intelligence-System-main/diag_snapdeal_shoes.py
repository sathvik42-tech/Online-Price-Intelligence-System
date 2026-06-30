
import asyncio
import json
import logging
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from scrapers.snapdeal_scraper import search_snapdeal

async def test():
    results = search_snapdeal("Running Shoes")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(test())
