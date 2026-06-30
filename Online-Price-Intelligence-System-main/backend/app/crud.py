try:
    from backend.database import get_connection
except ImportError:
    from database import get_connection
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_product(name: str, category: str = None, image_url: str = None, description: str = None) -> Optional[int]:
    """Inserts a new product and returns its product_id."""
    conn = get_connection()
    if not conn: return None
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO products (name, category, image_url, description) VALUES (%s, %s, %s, %s) RETURNING product_id;",
            (name, category, image_url, description)
        )
        product_id = cur.fetchone()[0]
        conn.commit()
        return product_id
    except Exception as e:
        logging.error(f"Error creating product: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def log_price(product_id: int, store_name: str, price: float, currency: str = 'USD', product_url: str = None) -> bool:
    """Logs a price entry for a specific product."""
    conn = get_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO prices (product_id, store_name, price, currency, product_url) VALUES (%s, %s, %s, %s, %s);",
            (product_id, store_name, price, currency, product_url)
        )
        conn.commit()
        return True
    except Exception as e:
        logging.error(f"Error logging price: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def log_search(query: str, user_id: int = None) -> bool:
    """Logs a search query to the history."""
    conn = get_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO search_history (query, user_id) VALUES (%s, %s);",
            (query, user_id)
        )
        conn.commit()
        return True
    except Exception as e:
        logging.error(f"Error logging search: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_product_prices(product_id: int) -> List[Dict[str, Any]]:
    """Retrieves all price entries for a given product."""
    conn = get_connection()
    if not conn: return []
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT store_name, price, currency, product_url, timestamp FROM prices WHERE product_id = %s ORDER BY price ASC;",
            (product_id,)
        )
        rows = cur.fetchall()
        return [
            {"store_name": r[0], "price": float(r[1]), "currency": r[2], "product_url": r[3], "timestamp": r[4]}
            for r in rows
        ]
    except Exception as e:
        logging.error(f"Error fetching prices: {e}")
        return []
    finally:
        conn.close()

def delete_product(product_id: int) -> bool:
    """Deletes a product and its associated prices."""
    conn = get_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE product_id = %s;", (product_id,))
        conn.commit()
        return True
    except Exception as e:
        logging.error(f"Error deleting product: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
