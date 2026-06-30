def calculate_statistics(products):
    """
    Calculates basic price statistics from a list of product dictionaries.
    
    Expects products to have a 'price' key with a float value.
    Returns: A dictionary with 'min_price', 'max_price', and 'avg_price'.
    """
    if not products:
        return {
            "min_price": 0.0,
            "max_price": 0.0,
            "avg_price": 0.0,
            "count": 0
        }
    
    # Extract prices
    prices = [p.get("price", 0.0) for p in products if isinstance(p.get("price"), (int, float))]
    
    if not prices:
        return {
            "min_price": 0.0,
            "max_price": 0.0,
            "avg_price": 0.0,
            "count": 0
        }
    
    # Calculate stats
    min_p = min(prices)
    max_p = max(prices)
    avg_p = sum(prices) / len(prices)
    
    return {
        "min_price": round(min_p, 2),
        "max_price": round(max_p, 2),
        "avg_price": round(avg_p, 2),
        "count": len(prices)
    }

if __name__ == "__main__":
    # Test cases
    test_products = [
        {"name": "Laptop A", "price": 45000.0},
        {"name": "Laptop B", "price": 52000.5},
        {"name": "Laptop C", "price": 48999.99},
    ]
    
    print("Calculating statistics for test products...")
    stats = calculate_statistics(test_products)
    print(f"Stats: {stats}")
    
    print("\nTesting empty list...")
    print(f"Stats: {calculate_statistics([])}")
