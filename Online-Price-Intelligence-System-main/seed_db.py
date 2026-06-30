import psycopg2
from database import get_connection
import datetime

def seed_database():
    """
    Creates tables if they don't exist and inserts sample data.
    """
    conn = get_connection()
    if not conn:
        print("Could not connect to database. Seed failed.")
        return

    try:
        cur = conn.cursor()

        # 1. Create Tables
        print("Creating tables...")
        
        # Products table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100)
            );
        """)

        # Prices table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(id),
                price DECIMAL(12, 2) NOT NULL,
                platform VARCHAR(50),
                currency VARCHAR(10),
                url TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Search History table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id SERIAL PRIMARY KEY,
                query VARCHAR(255) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Insert Sample Data
        print("Inserting sample data...")

        # Sample Product
        cur.execute("""
            INSERT INTO products (name, description, category)
            VALUES (%s, %s, %s) RETURNING id;
        """, ("Sample Laptop", "A high-performance sample laptop for testing.", "Electronics"))
        
        product_id = cur.fetchone()[0]

        # Sample Price
        cur.execute("""
            INSERT INTO prices (product_id, price, platform, currency, url)
            VALUES (%s, %s, %s, %s, %s);
        """, (product_id, 999.99, "Amazon", "USD", "https://example.com/sample-laptop"))

        # Sample Search History
        cur.execute("""
            INSERT INTO search_history (query)
            VALUES (%s);
        """, ("laptop",))

        # 3. Commit changes
        conn.commit()
        print("Sample data inserted successfully and changes committed.")

        cur.close()

    except Exception as e:
        print(f"Error during seeding: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    seed_database()
