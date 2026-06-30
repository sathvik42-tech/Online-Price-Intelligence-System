import logging

try:
    from backend.database import get_connection
except ImportError:
    from database import get_connection

logger = logging.getLogger(__name__)

def record_price_history(products):
    """
    Records the current price of products into the price_history table.
    'products' should be a list of dicts with 'product_url' and 'price'.
    """
    conn = get_connection()
    if not conn:
        logger.error("Could not connect to database for price history recording.")
        return

    try:
        cur = conn.cursor()
        for product in products:
            price = product.get('price')
            product_id = product.get('product_url')
            
            if price is not None and product_id:
                try:
                    cur.execute(
                        "INSERT INTO price_history (product_id, price) VALUES (%s, %s)",
                        (product_id, price)
                    )
                except Exception as e:
                    logger.warning(f"Failed to record price for {product_id}: {e}")
                    conn.rollback()
                    continue
        
        conn.commit()
        cur.close()
    except Exception as e:
        logger.error(f"Error in record_price_history: {e}")
        conn.rollback()
    finally:
        conn.close()
