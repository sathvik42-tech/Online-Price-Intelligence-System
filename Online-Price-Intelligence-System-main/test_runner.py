from reporting import build_comparison_output

def main():
    """
    Main entry point for testing the price comparison reporting module.
    """
    # 1. Create sample product data
    # Each product is a dictionary with name, price, rating, and shipping cost.
    sample_products = [
        {
            "name": "High-End Smartphone",
            "price": 999.0,
            "seller_rating": 4.9,
            "shipping": 0.0
        },
        {
            "name": "Mid-Range Smartphone",
            "price": 599.0,
            "seller_rating": 4.5,
            "shipping": 15.0
        },
        {
            "name": "Budget Smartphone",
            "price": 299.0,
            "seller_rating": 3.8,
            "shipping": 10.0
        },
        {
            "name": "Luxury Smartphone",
            "price": 1499.0,
            "seller_rating": 5.0,
            "shipping": 0.0
        }
    ]

    print("--- Price Intelligence System: Test Runner ---")
    print(f"Testing with {len(sample_products)} products...\n")

    # 2. Call the reporting function
    # This function uses utils.statistics and utils.scoring internally.
    report_json = build_comparison_output(sample_products)

    # 3. Print the formatted JSON output
    print("Generated Report:")
    print(report_json)

if __name__ == "__main__":
    main()
