"""
Performance Profiler Module

Monitors and profiles API endpoint performance to identify bottlenecks.
Collects metrics on:
- Request/response times
- Memory usage
- Database query times
- Cache hit rates
"""

import time
import logging
from collections import defaultdict
from typing import Dict, Any
import psutil
import os

logger = logging.getLogger(__name__)


class PerformanceProfiler:
    """Collect and analyze performance metrics"""
    
    def __init__(self):
        self.request_times = defaultdict(list)
        self.endpoint_stats = defaultdict(dict)
        self.process = psutil.Process(os.getpid())
    
    def record_request(self, endpoint: str, method: str, duration: float):
        """Record request timing for an endpoint"""
        key = f"{method} {endpoint}"
        self.request_times[key].append(duration)
        
        # Keep only last 1000 requests
        if len(self.request_times[key]) > 1000:
            self.request_times[key] = self.request_times[key][-1000:]
        
        # Update stats
        times = self.request_times[key]
        self.endpoint_stats[key] = {
            "count": len(times),
            "min": min(times),
            "max": max(times),
            "avg": sum(times) / len(times),
            "p95": sorted(times)[int(len(times) * 0.95)] if len(times) > 0 else 0,
            "p99": sorted(times)[int(len(times) * 0.99)] if len(times) > 0 else 0,
        }
    
    def get_slowest_endpoints(self, top_n: int = 10) -> list:
        """Get slowest endpoints by average response time"""
        sorted_endpoints = sorted(
            self.endpoint_stats.items(),
            key=lambda x: x[1].get("avg", 0),
            reverse=True
        )
        return sorted_endpoints[:top_n]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current process memory usage"""
        try:
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,  # Resident set size
                "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual memory size
                "percent": memory_percent
            }
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {}
    
    def get_cpu_stats(self) -> Dict[str, Any]:
        """Get current process CPU usage"""
        try:
            cpu_percent = self.process.cpu_percent(interval=0.1)
            
            return {
                "percent": cpu_percent,
                "system_percent": psutil.cpu_percent(interval=0.1)
            }
        except Exception as e:
            logger.error(f"Error getting CPU stats: {e}")
            return {}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            "endpoints": dict(self.endpoint_stats),
            "memory": self.get_memory_stats(),
            "cpu": self.get_cpu_stats(),
            "slowest_endpoints": [
                {
                    "endpoint": ep,
                    "stats": stats
                }
                for ep, stats in self.get_slowest_endpoints(5)
            ]
        }


# Global profiler instance
profiler = PerformanceProfiler()


# Decorators for easy profiling of functions

def profile_function(func):
    """Decorator to profile function execution time"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} took {duration:.2f}s")
    return wrapper


# Database Query Profiling

class QueryProfiler:
    """Profile database query performance"""
    
    def __init__(self):
        self.query_times = defaultdict(list)
        self.query_stats = defaultdict(dict)
    
    def record_query(self, query: str, duration: float, rows: int = 0):
        """Record query timing"""
        # Normalize query (remove specific values for grouping)
        normalized = self.normalize_query(query)
        self.query_times[normalized].append({
            "time": duration,
            "rows": rows
        })
        
        # Update stats
        times = [q["time"] for q in self.query_times[normalized]]
        self.query_stats[normalized] = {
            "count": len(times),
            "min": min(times),
            "max": max(times),
            "avg": sum(times) / len(times),
            "total_time": sum(times),
            "avg_rows": sum(q["rows"] for q in self.query_times[normalized]) / len(times)
        }
    
    def normalize_query(self, query: str) -> str:
        """Normalize SQL query for grouping"""
        # Remove specific values
        import re
        normalized = re.sub(r"'[^']*'", "'?'", query)
        normalized = re.sub(r"\d+", "?", normalized)
        return normalized
    
    def get_slowest_queries(self, top_n: int = 10) -> list:
        """Get slowest queries by average execution time"""
        sorted_queries = sorted(
            self.query_stats.items(),
            key=lambda x: x[1].get("avg", 0),
            reverse=True
        )
        return sorted_queries[:top_n]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get query performance summary"""
        return {
            "total_queries": sum(stats.get("count", 0) for stats in self.query_stats.values()),
            "total_time": sum(stats.get("total_time", 0) for stats in self.query_stats.values()),
            "slowest_queries": [
                {
                    "query": query,
                    "stats": stats
                }
                for query, stats in self.get_slowest_queries(10)
            ]
        }


# Global query profiler
query_profiler = QueryProfiler()


# Cache Performance Tracking

class CacheProfiler:
    """Track cache hit/miss rates"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.trend = []
    
    def record_hit(self):
        """Record cache hit"""
        self.hits += 1
    
    def record_miss(self):
        """Record cache miss"""
        self.misses += 1
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate percentage"""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100
    
    def get_summary(self) -> Dict[str, Any]:
        """Get cache performance summary"""
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total": total,
            "hit_rate": self.get_hit_rate(),
            "miss_rate": 100 - self.get_hit_rate()
        }


# Global cache profiler
cache_profiler = CacheProfiler()
