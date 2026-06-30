import time

class MemoryCache:
    def __init__(self, expiration_seconds=3600):
        self.cache = {}
        self.expiration_seconds = expiration_seconds

    def get(self, key):
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.expiration_seconds:
                return entry['data']
            else:
                del self.cache[key]
        return None

    def set(self, key, data):
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }

# Global cache instance
comparison_cache = MemoryCache(expiration_seconds=1800) # 30 minutes
