import psycopg2
from database import get_connection
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_search_history_table():
    """
    Creates the search_history table in the PostgreSQL database.
    """
    conn = get_connection()
    if not conn:
        logging.error("Could not connect to database. Table creation failed.")
        return

    try:
        cur = conn.cursor()
        logging.info("Updating search_history table...")

        # Drop existing table if it was created differently in previous steps to ensure strict compliance with requirement
        cur.execute("DROP TABLE IF EXISTS search_history CASCADE;")

        cur.execute("""
            CREATE TABLE search_history (
              id SERIAL PRIMARY KEY,
              user_id INTEGER,
              search_query TEXT,
              search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        logging.info("Table 'search_history' updated successfully.")
        cur.close()

    except Exception as e:
        logging.error(f"Error updating table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_search_history_table()
