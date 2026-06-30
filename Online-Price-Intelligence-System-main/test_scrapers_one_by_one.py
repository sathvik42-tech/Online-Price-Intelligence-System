
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

scrapers = [
    ("snapdeal", "search_snapdeal"),
    ("meesho", "search_meesho"),
    ("walmart", "search_walmart"),
    ("target", "search_target"),
    ("bestbuy", "search_bestbuy"),
    ("flipkart", "search_flipkart"),
    ("amazon", "search_amazon"),
    ("ebay", "search_ebay"),
]

for name, func_name in scrapers:
    print(f"Testing {name}...")
    start = time.time()
    try:
        module_path = f"scrapers.{name}_scraper"
        print(f"  Importing {module_path}...")
        module = __import__(module_path, fromlist=[func_name])
        func = getattr(module, func_name)
        print(f"  Imported {name} in {time.time() - start:.2f}s")
        
        print(f"  Running {name} search...")
        # Use a very simple query
        res = func("mouse")
        print(f"  {name} search finished in {time.time() - start:.2f}s, found {len(res)} items")
    except Exception as e:
        print(f"  {name} FAILED: {e}")
    print("-" * 20)

print("All tests finished.")
