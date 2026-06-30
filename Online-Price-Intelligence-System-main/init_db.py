import psycopg2
from database import get_connection
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_database():
    """
    Standardizes the database schema for Milestone 2.
    Creates tables with proper naming conventions and indexes.
    """
    conn = get_connection()
    if not conn:
        logging.error("Could not connect to database. Initialization failed.")
        return

    try:
        cur = conn.cursor()

        logging.info("Initializing database schema...")

        # Drop existing users table to ensure correct schema
        cur.execute("DROP TABLE IF EXISTS users CASCADE;")

        # 1. Products Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(100),
                image_url TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Prices Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                price_id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
                store_name VARCHAR(50) NOT NULL,
                price DECIMAL(12, 2) NOT NULL,
                currency VARCHAR(10) DEFAULT 'USD',
                product_url TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 3. Search History Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                search_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                search_query VARCHAR(255) NOT NULL,
                search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 4. Price History Table (for tracking price changes)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                history_id SERIAL PRIMARY KEY,
                product_id VARCHAR(255),
                store_name VARCHAR(50),
                price DECIMAL(12, 2),
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 5. Wishlist Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS wishlist (
                wishlist_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                product_id VARCHAR(255),
                product_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 6. Price Alerts Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS price_alerts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                product_id VARCHAR(255),
                product_name VARCHAR(255),
                current_price DECIMAL(12, 2),
                target_price DECIMAL(12, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 7. Users Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                reset_password_token VARCHAR(255),
                reset_password_expires TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 8. Indexes for performance
        logging.info("Creating indexes...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_prices_product_id ON prices(product_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_search_history_user_time ON search_history(user_id, search_time DESC);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_prices_timestamp ON prices(timestamp DESC);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_prices_product_time ON prices(product_id, timestamp DESC);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_price_history_product_time ON price_history(product_id, recorded_at DESC);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_search_history_time ON search_history(search_time DESC);")

        conn.commit()
        logging.info("Database initialized successfully.")

        cur.close()

    except Exception as e:
        logging.error(f"Error during database initialization: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()
