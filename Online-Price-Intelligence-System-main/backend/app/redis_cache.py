"""
Redis Caching Module for Performance Optimization

Features:
- Distributed caching with Redis
- Automatic expiration (configurable TTL)
- Support for different data types
- Connection pooling for efficiency
- Graceful fallback if Redis is unavailable
"""

import redis
import json
import logging
from typing import Any, Optional
from datetime import timedelta
import os
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis-based caching system for distributed cache management"""
    
    def __init__(
        self,
        host: str = os.getenv("REDIS_HOST", "localhost"),
        port: int = int(os.getenv("REDIS_PORT", 6379)),
        db: int = int(os.getenv("REDIS_DB", 0)),
        default_ttl: int = 600  # 10 minutes default
    ):
        """
        Initialize Redis connection with connection pooling
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            default_ttl: Default time-to-live in seconds
        """
        self.default_ttl = default_ttl
        self.redis_available = False
        
        try:
            # Create connection pool for better performance
            self.pool = redis.ConnectionPool(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                max_connections=20,
                socket_connect_timeout=1,
                socket_timeout=1,
                socket_keepalive=True
            )
            self.client = redis.Redis(connection_pool=self.pool)
            
            # Test connection
            self.client.ping()
            self.redis_available = True
            logger.info(f"Redis connected at {host}:{port}")
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.warning(f"Redis not available: {e}. Caching disabled.")
            self.redis_available = False
            self.client = None

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve cached data
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        if not self.redis_available or not self.client:
            return None
            
        try:
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
            self.redis_available = False
            return None

    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        Store data in cache
        
        Args:
            key: Cache key
            data: Data to cache (must be JSON-serializable)
            ttl: Time-to-live in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.redis_available or not self.client:
            return False
            
        try:
            ttl = ttl or self.default_ttl
            self.client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(data)
            )
            logger.debug(f"Cached key: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            self.redis_available = False
            return False

    def delete(self, key: str) -> bool:
        """Delete cached data"""
        if not self.redis_available or not self.client:
            return False
            
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache: {e}")
            self.redis_available = False
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern
        
        Args:
            pattern: Key pattern (e.g., "compare_*")
            
        Returns:
            Number of keys deleted
        """
        if not self.redis_available or not self.client:
            return 0
            
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern: {e}")
            self.redis_available = False
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis_available or not self.client:
            return False
            
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Error checking cache existence: {e}")
            self.redis_available = False
            return False

    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.redis_available or not self.client:
            return {"available": False}
            
        try:
            info = self.client.info()
            return {
                "available": True,
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands": info.get("total_commands_processed"),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_ratio": info.get("keyspace_hits", 0) / max(
                    info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1), 1
                )
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            self.redis_available = False
            return {"available": False}

    def close(self):
        """Close Redis connection"""
        try:
            if self.client:
                self.pool.disconnect()
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")

    # --- Extra Redis primitives used by the app (optional) ---

    def zincrby(self, name: str, amount: float, member: str) -> Optional[float]:
        """Increment a sorted-set score (used for popular searches)."""
        if not self.redis_available or not self.client:
            return None
        try:
            return float(self.client.zincrby(name, amount, member))
        except Exception as e:
            logger.error(f"Error updating sorted set {name}: {e}")
            self.redis_available = False
            return None

    def zrevrange(self, name: str, start: int, end: int, withscores: bool = False):
        """Get a sorted-set range in descending order."""
        if not self.redis_available or not self.client:
            return []
        try:
            return self.client.zrevrange(name, start, end, withscores=withscores)
        except Exception as e:
            logger.error(f"Error reading sorted set {name}: {e}")
            self.redis_available = False
            return []

    def expire(self, key: str, ttl: int) -> bool:
        """Set key expiration (seconds)."""
        if not self.redis_available or not self.client:
            return False
        try:
            return bool(self.client.expire(key, ttl))
        except Exception as e:
            logger.error(f"Error expiring key {key}: {e}")
            self.redis_available = False
            return False


# Global cache instance
cache = RedisCache()


# Cache Decorators for easy usage
def cache_result(ttl: int = 600, key_prefix: str = ""):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_suffix = hashlib.md5(
                f"{str(args)}{str(kwargs)}".encode()
            ).hexdigest()
            cache_key = f"{key_prefix or func.__name__}_{key_suffix}"
            
            # Try to get from cache first
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached
            
            # Execute function if not cached
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl=ttl)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_suffix = hashlib.md5(
                f"{str(args)}{str(kwargs)}".encode()
            ).hexdigest()
            cache_key = f"{key_prefix or func.__name__}_{key_suffix}"
            
            # Try to get from cache first
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached
            
            # Execute function if not cached
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl=ttl)
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


import asyncio


def invalidate_cache_pattern(pattern: str):
    """Invalidate cache entries matching a pattern"""
    return cache.clear_pattern(pattern)


# Predefined cache keys and TTLs
CACHE_KEYS = {
    "search": {
        "key": "search_{query}",
        "ttl": 600  # 10 minutes
    },
    "compare": {
        "key": "compare_{query}",
        "ttl": 600  # 10 minutes
    },
    "product_details": {
        "key": "product_{id}",
        "ttl": 600  # 10 minutes
    },
    "popular_searches": {
        "key": "popular_searches",
        "ttl": 600  # 10 minutes
    },
    "recommendations": {
        "key": "recommendations_{user_id}",
        "ttl": 1800  # 30 minutes
    },
    "wishlist": {
        "key": "wishlist_{user_id}",
        "ttl": 1200  # 20 minutes
    },
    "price_history": {
        "key": "price_history_{product_id}",
        "ttl": 3600  # 1 hour
    },
    "user_preferences": {
        "key": "user_pref_{user_id}",
        "ttl": 3600  # 1 hour
    }
}
