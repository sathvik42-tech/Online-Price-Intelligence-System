import psycopg2
from database import get_connection
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_wishlist_table():
    """
    Creates the wishlist table in the PostgreSQL database.
    """
    conn = get_connection()
    if not conn:
        logging.error("Could not connect to database. Table creation failed.")
        return

    try:
        cur = conn.cursor()
        logging.info("Creating wishlist table...")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS wishlist (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                product_id VARCHAR(255),
                product_name TEXT,
                product_image TEXT,
                price NUMERIC,
                store TEXT,
                product_link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        logging.info("Table 'wishlist' created successfully.")
        cur.close()

    except Exception as e:
        logging.error(f"Error creating table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_wishlist_table()
