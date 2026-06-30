import json
from backend.utils.statistics import calculate_statistics
from backend.utils.scoring import find_best_deal

# Alias for external use
calculate_stats = calculate_statistics

def build_comparison_output(products):
    """
    Consolidates statistics and best deal information into a structured JSON report.
    
    Returns:
        str: A formatted JSON string containing summary stats and the best deal details.
    """
    if not products:
        return json.dumps({
            "lowest_price": 0.0,
            "highest_price": 0.0,
            "average_price": 0.0,
            "best_deal": None,
            "total_products_compared": 0
        }, indent=4)

    # 1. Calculate price statistics
    stats = calculate_statistics(products)
    
    # 2. Find the best deal
    # find_best_deal already adds the 'score' field to products
    best_deal = find_best_deal(products)
    
    # 3. Build the structured output dictionary
    output = {
        "lowest_price": stats.get("min_price"),
        "highest_price": stats.get("max_price"),
        "average_price": stats.get("avg_price"),
        "best_deal": best_deal,
        "total_products_compared": stats.get("count")
    }
    
    # 4. Return as formatted JSON string
    return json.dumps(output, indent=4)

if __name__ == "__main__":
    # Test data
    sample_products = [
        {"name": "Laptop Pro", "price": 1200.0, "seller_rating": 4.8, "shipping": 10.0},
        {"name": "Budget Laptop", "price": 800.0, "seller_rating": 4.2, "shipping": 0.0},
        {"name": "Mid-range Laptop", "price": 1000.0, "seller_rating": 4.5, "shipping": 5.0},
    ]
    
    print("Generating comparison report...\n")
    report_json = build_comparison_output(sample_products)
    print(report_json)
