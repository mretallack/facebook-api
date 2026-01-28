"""Simple in-memory cache manager with TTL support"""
import time
from typing import Any, Optional, Dict
from dataclasses import dataclass


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class CacheManager:
    """In-memory cache with TTL"""
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # Check if expired
        if time.time() > entry.expires_at:
            del self._cache[key]
            return None
        
        return entry.value
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL in seconds"""
        expires_at = time.time() + ttl
        self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
    
    async def clear(self):
        """Clear all cache"""
        self._cache.clear()
    
    async def cleanup_expired(self):
        """Remove expired entries"""
        now = time.time()
        expired = [k for k, v in self._cache.items() if now > v.expires_at]
        for key in expired:
            del self._cache[key]
    
    def stats(self) -> Dict:
        """Get cache statistics"""
        now = time.time()
        total = len(self._cache)
        expired = sum(1 for v in self._cache.values() if now > v.expires_at)
        
        return {
            'total_entries': total,
            'active_entries': total - expired,
            'expired_entries': expired
        }


# Global cache instance
cache = CacheManager()
