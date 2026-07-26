"""
Performance Optimization (Step 8)

Simple In-Memory Time-To-Live (TTL) Cache.

In production BI systems, dashboards are viewed by hundreds of executives simultaneously.
If every page refresh runs a complex SQL aggregation, the database will crash.
By caching the result for 60 seconds, 1000 requests become just 1 database query.

Note: In a true distributed system (like Kubernetes with multiple pods), 
you would use Redis instead of in-memory caching so all pods share the same cache.
"""
import time
from typing import Any, Dict

class TTLCache:
    """A simple thread-safe-ish TTL cache for expensive BI queries."""
    def __init__(self, ttl_seconds: int = 60):
        self.ttl = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Any:
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                return entry["data"]
            else:
                del self.cache[key]
        return None

    def set(self, key: str, data: Any):
        self.cache[key] = {
            "timestamp": time.time(),
            "data": data
        }

    def invalidate(self, key: str):
        if key in self.cache:
            del self.cache[key]

# Global singleton cache instance for analytics (60 second TTL)
analytics_cache = TTLCache(ttl_seconds=60)
