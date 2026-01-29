from fastapi import APIRouter, Query, HTTPException
from src.scraper.session_manager import SessionManager
from src.scraper.feed_aggregator import FeedAggregator

router = APIRouter(prefix="/posts", tags=["posts"])
session_manager: SessionManager = None
posts_service = None
cache_service = None

def set_session_manager(sm: SessionManager):
    global session_manager
    session_manager = sm

def set_posts_service(service):
    global posts_service
    posts_service = service

def set_cache_service(service):
    global cache_service
    cache_service = service

@router.get("/feed")
async def get_posts(
    limit: int = Query(20, ge=1, le=100),
    friends: str = Query("", description="Comma-separated friend profile URLs"),
    fresh: bool = Query(False, description="Force fresh scrape, bypass cache")
):
    """Extract posts from friends using GraphQL interception with caching"""
    
    if not session_manager or not session_manager.page:
        raise HTTPException(status_code=503, detail="Browser not ready")
    
    # Try cache first unless fresh is requested
    if cache_service and not fresh:
        cached = cache_service.get_posts(limit=limit)
        if cached and len(cached) > 0:
            return {
                "count": len(cached),
                "posts": cached,
                "cached": True
            }
    
    # Parse friends list
    friend_list = []
    if friends:
        for url in friends.split(','):
            url = url.strip()
            if url:
                name = url.split('/')[-1].replace('.', ' ').title()
                friend_list.append({'name': name, 'url': url})
    else:
        # Default test friend
        friend_list = [{'name': 'Mark Retallack', 'url': 'https://www.facebook.com/mark.retallack'}]
    
    # Scrape fresh posts
    aggregator = FeedAggregator(session_manager.page, session_manager)
    posts = await aggregator.get_feed(friend_list, [], limit=limit, include_own_profile=False)
    
    # Store in cache
    if cache_service and posts:
        print(f"[DEBUG] Storing {len(posts)} posts in cache")
        for post in posts:
            print(f"[DEBUG] Storing post: {post['id'][:50]}...")
            cache_service.store_post(
                post_id=post['id'],
                author_name=post['author']['name'],
                author_url=post['author']['profile_url'],
                content=post['content'],
                url=post['url'],
                timestamp=post.get('timestamp', ''),
                image_url=post.get('image_url'),
                source_type='friend'
            )
        print(f"[DEBUG] Finished storing posts")
    else:
        print(f"[DEBUG] Not storing: cache_service={cache_service is not None}, posts={len(posts) if posts else 0}")
    
    return {
        "count": len(posts),
        "posts": posts,
        "cached": False
    }

@router.post("/feed/refresh")
async def refresh_feed(
    friends: str = Query("", description="Comma-separated friend profile URLs"),
    limit: int = Query(20, ge=1, le=100)
):
    """Refresh feed cache in background - call this periodically"""
    
    if not session_manager or not session_manager.page:
        raise HTTPException(status_code=503, detail="Browser not ready")
    
    # Parse friends list
    friend_list = []
    if friends:
        for url in friends.split(','):
            url = url.strip()
            if url:
                name = url.split('/')[-1].replace('.', ' ').title()
                friend_list.append({'name': name, 'url': url})
    else:
        friend_list = [{'name': 'Mark Retallack', 'url': 'https://www.facebook.com/mark.retallack'}]
    
    # Scrape and cache
    aggregator = FeedAggregator(session_manager.page, session_manager)
    posts = await aggregator.get_feed(friend_list, [], limit=limit, include_own_profile=False)
    
    if cache_service and posts:
        for post in posts:
            cache_service.store_post(
                post_id=post['id'],
                author_name=post['author']['name'],
                author_url=post['author']['profile_url'],
                content=post['content'],
                url=post['url'],
                timestamp=post.get('timestamp', ''),
                image_url=post.get('image_url'),
                source_type='friend'
            )
    
    return {
        "status": "refreshed",
        "count": len(posts),
        "cached": True
    }
