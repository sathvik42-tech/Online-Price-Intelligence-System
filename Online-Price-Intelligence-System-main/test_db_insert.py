from database import get_connection

def test_insert():
    """
    Connects to PostgreSQL and inserts sample data into products, prices, and search_history tables.
    """
    conn = get_connection()
    if not conn:
        print("Failed to connect for test insert.")
        return

    try:
        cur = conn.cursor()

        # 1. Insert Sample Product
        cur.execute("""
            INSERT INTO products (name, description, category) 
            VALUES (%s, %s, %s) RETURNING product_id;
        """, ("Test Product", "Testing database insertion", "Test Category"))
        product_id = cur.fetchone()[0]

        # 2. Insert Price Data
        cur.execute("""
            INSERT INTO prices (product_id, store_name, price, product_url) 
            VALUES (%s, %s, %s, %s);
        """, (product_id, "Walmart", 49.99, "https://walmart.com/test-product"))

        # 3. Insert Search History
        cur.execute("""
            INSERT INTO search_history (query) 
            VALUES (%s);
        """, ("test search",))

        # 4. Commit changes
        conn.commit()
        print("Successfully inserted sample data into products, prices, and search_history.")

        cur.close()
    except Exception as e:
        print(f"Error during test insertion: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    test_insert()
