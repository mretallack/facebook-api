"""
Cache management API routes.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cache", tags=["cache"])

cache_service = None
refresh_tasks = None


def set_cache_service(service):
    """Set the cache service instance."""
    global cache_service
    cache_service = service


def set_refresh_tasks(tasks):
    """Set the refresh tasks instance."""
    global refresh_tasks
    refresh_tasks = tasks


@router.get("/status")
async def get_cache_status() -> Dict:
    """Get cache status and metadata."""
    if not cache_service:
        raise HTTPException(status_code=503, detail="Cache service not initialized")
    
    status = {}
    for key in ['posts', 'friends', 'profile', 'requests']:
        meta = cache_service.get_metadata(key)
        if meta:
            status[key] = {
                'last_fetch': meta['last_fetch'].isoformat() if meta['last_fetch'] else None,
                'next_fetch': meta['next_fetch'].isoformat() if meta['next_fetch'] else None,
                'fetch_count': meta['fetch_count'],
                'error_count': meta['error_count']
            }
        else:
            status[key] = {'status': 'not_initialized'}
    
    return status


@router.post("/refresh/{data_type}")
async def refresh_cache(data_type: str) -> Dict:
    """Manually trigger cache refresh for specific data type."""
    if not refresh_tasks:
        raise HTTPException(status_code=503, detail="Refresh tasks not initialized")
    
    if data_type == 'posts':
        await refresh_tasks.refresh_posts()
    elif data_type == 'friends':
        await refresh_tasks.refresh_friends()
    elif data_type == 'profile':
        await refresh_tasks.refresh_profile()
    elif data_type == 'requests':
        await refresh_tasks.refresh_friend_requests()
    else:
        raise HTTPException(status_code=400, detail=f"Invalid data type: {data_type}")
    
    return {'success': True, 'message': f'Refreshed {data_type}'}


@router.delete("/clear")
async def clear_cache() -> Dict:
    """Clear all cached data."""
    if not cache_service:
        raise HTTPException(status_code=503, detail="Cache service not initialized")
    
    # Clear all caches by setting empty data with 0 expiry
    cache_service.set_posts([], 0)
    cache_service.set_friends([], 0)
    cache_service.set_profile({'name': None, 'bio': None, 'url': None}, 0)
    cache_service.set_friend_requests([], 0)
    
    return {'success': True, 'message': 'Cache cleared'}
