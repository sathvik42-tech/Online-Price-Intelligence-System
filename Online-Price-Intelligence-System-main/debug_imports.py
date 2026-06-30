import sys
import os
import traceback

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Importing backend.app.main_optimized...")
    from backend.app.main_optimized import app
    print("Import successful!")
    
    # Try to simulate the search call
    print("Testing aggregation...")
    from backend.utils.aggregation import aggregate_prices
    print("Testing scoring...")
    from backend.utils.scoring import find_best_deal
    print("Testing reporting...")
    from backend.reporting import calculate_stats
    
    print("All core imports look good now.")
    
    # Test the compare endpoint logic if possible
    print("\nTesting compare-prices logic path...")
    from backend.app.routers.compare import compare_prices
    print("compare_prices imported.")
    
except Exception:
    print("\n[!] FATAL IMPORT ERROR:")
    traceback.print_exc()
