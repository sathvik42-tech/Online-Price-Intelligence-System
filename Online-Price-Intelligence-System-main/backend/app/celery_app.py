"""
Celery Configuration for Asynchronous Task Processing

This module configures Celery to handle background tasks like web scraping,
image processing, and other long-running operations without blocking API responses.
"""

from celery import Celery
from celery.schedules import crontab
import os
from datetime import timedelta

# Configure Celery
celery_app = Celery(
    __name__,
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
)

# Celery Configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minute hard limit
    task_soft_time_limit=25 * 60,  # 25 minute soft limit warning
    
    # Worker configuration
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Result backend configuration
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
        "retry_on_timeout": True,
    },
    
    # Task routing
    task_routes={
        "app.tasks.scrape_all_platforms": {"queue": "scraping"},
        "app.tasks.process_price_history": {"queue": "processing"},
        "app.tasks.send_price_alert": {"queue": "alerts"},
        "app.tasks.generate_recommendations": {"queue": "ml"},
    },
    
    # Scheduled tasks (beat schedule)
    beat_schedule={
        "collect-price-history": {
            "task": "app.tasks.periodic_price_collection",
            "schedule": timedelta(hours=1),  # Every hour
            "options": {"queue": "processing"}
        },
        "generate-recommendations": {
            "task": "app.tasks.generate_recommendations",
            "schedule": timedelta(hours=6),  # Every 6 hours
            "options": {"queue": "ml"}
        },
        "send-pending-alerts": {
            "task": "app.tasks.send_pending_price_alerts",
            "schedule": timedelta(minutes=15),  # Every 15 minutes
            "options": {"queue": "alerts"}
        },
    }
)

# Load task module
celery_app.autodiscover_tasks(["backend.app"])


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f"Request: {self.request!r}")
