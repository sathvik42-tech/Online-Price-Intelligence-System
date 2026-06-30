def calculate_score(product, lowest_price):
    """
    Calculates a preference score (0-100) for a product based on price, rating, and shipping.
    
    Formula: score = (price_factor * 0.55) + (seller_factor * 0.30) - (extras_penalty * 0.15)
    """
    try:
        price = float(product.get("price", 0))
        lowest_price = float(lowest_price)
        
        if price <= 0 or lowest_price <= 0:
            return 0
            
        # 1. Price Factor (Scale 0-100)
        # Closer to lowest price = higher score
        price_factor = (lowest_price / price) * 100
        
        # 2. Seller Factor (Scale 0-100)
        rating_str = str(product.get("seller_rating", "0"))
        import re
        rating_match = re.search(r'(\d+\.?\d*)', rating_str)
        rating = float(rating_match.group(1)) if rating_match else 0.0
        rating = min(rating, 5.0)
        seller_factor = (rating / 5.0) * 100
        
        # 3. Shipping Penalty
        shipping = float(product.get("shipping", 0))
        # Penalty is based on how much shipping adds to the base price
        shipping_penalty = (shipping / price) * 100 if price > 0 else 0
        
        # Calculate Final Score
        # Weightage: 55% Price, 35% Seller, 10% Shipping Penalty
        score = (price_factor * 0.55) + (seller_factor * 0.35) - (shipping_penalty * 0.10)
        
        return round(max(0, min(100, score)), 1)
        
    except Exception as e:
        return 0

def find_best_deal(products):
    """
    Identifies the best product deal based on calculated value scores.
    1. Finds the lowest price in the list.
    2. Scores every product using calculate_score().
    3. Returns the product with the highest score.
    """
    if not products:
        return None
        
    # 1. Calculate lowest price
    valid_prices = [float(p.get("price", 0)) for p in products if float(p.get("price", 0)) > 0]
    if not valid_prices:
        return None
        
    lowest_price = min(valid_prices)
    
    # 2. Score every product
    for product in products:
        product["score"] = calculate_score(product, lowest_price)
        
    # 3. Return product with highest score
    # Use max() with a key to find the dictionary with the highest 'score'
    best_deal = max(products, key=lambda x: x.get("score", 0))
    
    return best_deal

if __name__ == "__main__":
    # Test cases
    test_products = [
        {"name": "Best Deal", "price": 100.0, "seller_rating": 5, "shipping": 0},
        {"name": "Reliable but Pricey", "price": 120.0, "seller_rating": 4.8, "shipping": 5.0},
        {"name": "Cheap but Bad Rating", "price": 105.0, "seller_rating": 2.1, "shipping": 15.0},
    ]
    
    print("Finding the best deal from products...\n")
    best = find_best_deal(test_products)
    
    if best:
        print(f"Winner: {best['name']}")
        print(f"Score:  {best['score']}")
        print(f"Price:  ${best['price']}")
        print(f"Rating: {best['seller_rating']}")
    else:
        print("No products found.")
