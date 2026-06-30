import psycopg2
from database import get_connection
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_price_history_table():
    """
    Creates the price_history table in the PostgreSQL database.
    """
    conn = get_connection()
    if not conn:
        logging.error("Could not connect to database. Table creation failed.")
        return

    try:
        cur = conn.cursor()
        logging.info("Creating price_history table...")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id SERIAL PRIMARY KEY,
                product_id VARCHAR(255),
                price NUMERIC,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        logging.info("Table 'price_history' created successfully.")
        cur.close()

    except Exception as e:
        logging.error(f"Error creating table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_price_history_table()
