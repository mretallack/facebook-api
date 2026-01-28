from fastapi import APIRouter, Query, HTTPException, Response
from typing import Optional, List
from src.api.models import Post, CreatePostRequest, CommentRequest, ShareRequest, ReactionRequest, PostActionResponse
from src.scraper.session_manager import SessionManager
from src.scraper.post_extractor import PostExtractor
from src.scraper.content_classifier import ContentClassifier
from datetime import datetime

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

@router.get("/feed", response_model=List[Post])
async def get_posts(
    response: Response,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    exclude_ads: bool = Query(False),
    exclude_suggested: bool = Query(False),
    post_type: Optional[str] = Query(None),
    fresh: bool = Query(False)
):
    """Extract posts from friends' feed"""
    
    # Try cache first if enabled and not requesting fresh data
    if cache_service and not fresh:
        # Get posts from both friend and following sources
        cached_posts = cache_service.get_posts(limit * 2, source_type=None)
        if cached_posts:
            # Apply filtering
            filtered = ContentClassifier.filter_posts(
                cached_posts,
                exclude_ads=exclude_ads,
                exclude_suggested=exclude_suggested,
                post_type=post_type
            )
            
            response.headers["X-Cache-Hit"] = "true"
            response.headers["X-Cache-Age"] = "0"
            return filtered[offset:offset + limit]
    
    response.headers["X-Cache-Hit"] = "false"
    
    if not session_manager or not session_manager.page:
        raise HTTPException(status_code=503, detail="Browser not initialized")
    
    # Extract posts
    extractor = PostExtractor(session_manager.page)
    posts = await extractor.extract_posts(limit + offset)
    
    # Filter posts
    filtered = ContentClassifier.filter_posts(
        posts,
        exclude_ads=exclude_ads,
        exclude_suggested=exclude_suggested,
        post_type=post_type
    )
    
    # Apply pagination
    return filtered[offset:offset + limit]

@router.get("/following", response_model=List[Post])
async def get_following_posts(
    response: Response,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    fresh: bool = Query(False)
):
    """Extract posts from following feed"""
    
    # Try cache first if enabled and not requesting fresh data
    if cache_service and not fresh:
        cached_posts = cache_service.get_posts(limit, source_type='following')
        if cached_posts:
            response.headers["X-Cache-Hit"] = "true"
            response.headers["X-Cache-Age"] = "0"
            return cached_posts[offset:offset + limit]
    
    response.headers["X-Cache-Hit"] = "false"
    
    # For now, return empty list since we don't have following scraper yet
    return []

@router.post("/create", response_model=PostActionResponse)
async def create_post(request: CreatePostRequest):
    """Create a new post."""
    if not posts_service:
        raise HTTPException(status_code=503, detail="Posts service not initialized")
    
    result = await posts_service.create_post(
        content=request.content,
        image_paths=request.image_paths,
        privacy=request.privacy
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to create post'))
    
    return PostActionResponse(success=True, message="Post created")

@router.delete("/{post_id}", response_model=PostActionResponse)
async def delete_post(post_id: str):
    """Delete a post."""
    if not posts_service:
        raise HTTPException(status_code=503, detail="Posts service not initialized")
    
    result = await posts_service.delete_post(post_id)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to delete post'))
    
    return PostActionResponse(success=True, message="Post deleted")

@router.post("/{post_id}/like", response_model=PostActionResponse)
async def like_post(post_id: str):
    """Like a post."""
    if not posts_service:
        raise HTTPException(status_code=503, detail="Posts service not initialized")
    
    result = await posts_service.like_post(post_id)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to like post'))
    
    return PostActionResponse(success=True, message="Post liked")

@router.post("/{post_id}/react", response_model=PostActionResponse)
async def react_post(post_id: str, request: ReactionRequest):
    """React to a post."""
    if not posts_service:
        raise HTTPException(status_code=503, detail="Posts service not initialized")
    
    result = await posts_service.react_post(post_id, request.reaction)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to react'))
    
    return PostActionResponse(success=True, message=f"Reacted with {request.reaction}")

@router.post("/{post_id}/comment", response_model=PostActionResponse)
async def comment_post(post_id: str, request: CommentRequest):
    """Comment on a post."""
    if not posts_service:
        raise HTTPException(status_code=503, detail="Posts service not initialized")
    
    result = await posts_service.comment_post(post_id, request.comment)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to comment'))
    
    return PostActionResponse(success=True, message="Comment posted")

@router.post("/{post_id}/share", response_model=PostActionResponse)
async def share_post(post_id: str, request: ShareRequest):
    """Share a post."""
    if not posts_service:
        raise HTTPException(status_code=503, detail="Posts service not initialized")
    
    result = await posts_service.share_post(post_id, request.message)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to share'))
    
    return PostActionResponse(success=True, message="Post shared")
