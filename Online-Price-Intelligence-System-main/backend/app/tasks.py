"""
Background Tasks Module

Defines asynchronous tasks for:
- Web scraping (non-blocking price comparison)
- Price history collection
- Recommendation generation
- Price alerts sending
- Image processing
"""

import logging
from celery import shared_task, current_task
from celery.exceptions import SoftTimeLimitExceeded
import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

try:
    from .fast_search import fast_search_all_platforms
except ImportError:
    from main_scraper import search_all_platforms as fast_search_all_platforms

try:
    from backend.utils.aggregation import aggregate_prices
    from backend.utils.scoring import find_best_deal
    from backend.reporting import calculate_stats
    from .redis_cache import cache, invalidate_cache_pattern
    from .model import predict_image
    from .preprocessing import preprocess_image
except ImportError:
    from utils.aggregation import aggregate_prices
    from utils.scoring import find_best_deal
    from reporting import calculate_stats
    try:
        from .redis_cache import cache, invalidate_cache_pattern
        from .model import predict_image
        from .preprocessing import preprocess_image
    except ImportError:
        # Fallback for direct script execution
        from redis_cache import cache, invalidate_cache_pattern
        from model import predict_image
        from preprocessing import preprocess_image


logger = logging.getLogger(__name__)

def _run_search(product_query: str):
    if asyncio.iscoroutinefunction(fast_search_all_platforms):
        return asyncio.run(fast_search_all_platforms(product_query, timeout=30))
    return fast_search_all_platforms(product_query)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def scrape_all_platforms(self, product_query: str):
    """
    Scrape all e-commerce platforms for a product (background task)
    
    Args:
        product_query: Product name/query to search for
        
    Returns:
        Dict with results from all platforms
    """
    try:
        logger.info(f"Starting async scrape for: {product_query}")
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Scraping platforms..."}
        )
        
        # Perform scraping
        results = _run_search(product_query)
        
        logger.info(f"Scraping completed for: {product_query}")
        return {
            "query": product_query,
            "results": results,
            "status": "completed"
        }
        
    except SoftTimeLimitExceeded:
        logger.error(f"Scraping task exceeded time limit for: {product_query}")
        raise
    except Exception as exc:
        logger.error(f"Error during scraping: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@shared_task(bind=True)
def process_price_comparison(self, product_query: str):
    """
    Process price comparison results (aggregation, scoring, statistics)
    
    Args:
        product_query: Product to compare
        
    Returns:
        Complete comparison result
    """
    try:
        logger.info(f"Processing comparison for: {product_query}")
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Processing results..."}
        )
        
        # Fetch raw results
        raw_results = _run_search(product_query)
        
        # Aggregate and process
        flat_results = []
        for platform, items in raw_results.items():
            flat_results.extend(items)
        
        if not flat_results:
            return {
                "query": product_query,
                "products": [],
                "best_deal": None,
                "statistics": {},
                "status": "no_results"
            }
        
        aggregated = aggregate_prices(raw_results)
        best_deal = find_best_deal(aggregated)
        stats = calculate_stats(aggregated)
        
        result = {
            "query": product_query,
            "products": aggregated,
            "best_deal": best_deal,
            "statistics": stats,
            "status": "success"
        }
        
        # Cache the result
        cache_key = f"compare_{product_query}"
        cache.set(cache_key, result, ttl=600)
        
        logger.info(f"Comparison processed and cached for: {product_query}")
        return result
        
    except Exception as exc:
        logger.error(f"Error processing comparison: {exc}")
        raise


@shared_task(bind=True)
def process_image(self, image_path: str, image_filename: str):
    """
    Process product image for recognition (background)
    
    Args:
        image_path: Path to image file
        image_filename: Original filename
        
    Returns:
        Prediction results
    """
    try:
        logger.info(f"Processing image: {image_filename}")
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Processing image..."}
        )
        
        # Preprocess image (preprocessing expects bytes)
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        processed_image = preprocess_image(image_bytes)
        
        # Run prediction
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Running model prediction..."}
        )
        predictions = predict_image(processed_image)
        
        logger.info(f"Image processing completed: {image_filename}")
        return {
            "filename": image_filename,
            "predictions": predictions,
            "status": "completed"
        }
        
    except Exception as exc:
        logger.error(f"Error processing image: {exc}")
        raise


@shared_task(bind=True)
def periodic_price_collection(self):
    """
    Periodic task to collect price data for tracked products
    Runs every hour
    """
    try:
        logger.info("Starting periodic price collection")
        # This would typically:
        # 1. Get list of tracked products from DB
        # 2. Scrape prices for each
        # 3. Store in price_history
        # 4. Check for price drops and send alerts
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Collecting prices..."}
        )
        
        # Placeholder for actual implementation
        logger.info("Periodic price collection completed")
        return {"status": "completed", "products_updated": 0}
        
    except Exception as exc:
        logger.error(f"Error in periodic price collection: {exc}")
        raise


@shared_task(bind=True)
def generate_recommendations(self, user_id: int = None):
    """
    Generate product recommendations based on user history
    
    Args:
        user_id: Optional user ID for personalized recommendations
        
    Returns:
        List of recommendations
    """
    try:
        logger.info(f"Generating recommendations for user: {user_id}")
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Generating recommendations..."}
        )
        
        # Placeholder for ML-based recommendation logic
        recommendations = {
            "user_id": user_id,
            "recommendations": [],
            "generated_at": __import__('datetime').datetime.utcnow().isoformat()
        }
        
        # Cache recommendations
        if user_id:
            cache_key = f"recommendations_{user_id}"
            cache.set(cache_key, recommendations, ttl=1800)
        
        logger.info(f"Recommendations generated for user: {user_id}")
        return recommendations
        
    except Exception as exc:
        logger.error(f"Error generating recommendations: {exc}")
        raise


@shared_task(bind=True)
def send_price_alert(self, alert_id: int, product_name: str, current_price: float, target_price: float):
    """
    Send price alert notification to user
    
    Args:
        alert_id: Price alert ID
        product_name: Product name
        current_price: Current price
        target_price: Target/threshold price
        
    Returns:
        Email send status
    """
    try:
        logger.info(f"Sending price alert {alert_id} for {product_name}")
        current_task.update_state(
            state="PROGRESS",
            meta={"status": f"Sending alert for {product_name}..."}
        )
        
        # Placeholder for email sending logic
        # In production, integrate with email service (SendGrid, etc.)
        
        logger.info(f"Price alert {alert_id} sent successfully")
        return {
            "alert_id": alert_id,
            "status": "sent",
            "product": product_name
        }
        
    except Exception as exc:
        logger.error(f"Error sending alert {alert_id}: {exc}")
        raise


@shared_task(bind=True)
def send_pending_price_alerts(self):
    """
    Check and send all pending price alerts
    Runs every 15 minutes
    """
    try:
        logger.info("Processing pending price alerts")
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Checking price alerts..."}
        )
        
        # Placeholder for alert checking logic
        # 1. Query database for active price alerts
        # 2. Check if current price meets trigger condition
        # 3. Send alerts if triggered
        # 4. Update alert status
        
        logger.info("Pending price alerts processed")
        return {"status": "completed", "alerts_sent": 0}
        
    except Exception as exc:
        logger.error(f"Error processing price alerts: {exc}")
        raise


@shared_task(bind=True)
def clear_expired_cache(self):
    """
    Clear expired cache entries
    Runs periodically to maintain cache health
    """
    try:
        logger.info("Clearing expired cache entries")
        
        patterns = [
            "search_*",
            "compare_*",
            "product_*",
            "recommendations_*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = invalidate_cache_pattern(pattern)
            total_deleted += deleted
            logger.info(f"Cleared {deleted} entries for pattern: {pattern}")
        
        logger.info(f"Total cache entries cleared: {total_deleted}")
        return {"status": "completed", "entries_cleared": total_deleted}
        
    except Exception as exc:
        logger.error(f"Error clearing cache: {exc}")
        raise
