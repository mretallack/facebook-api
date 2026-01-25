from fastapi import APIRouter, Query
from typing import Optional, List
from src.api.models import Post
from src.scraper.session_manager import SessionManager
from src.scraper.post_extractor import PostExtractor
from src.scraper.content_classifier import ContentClassifier

router = APIRouter()
session_manager: SessionManager = None

def set_session_manager(sm: SessionManager):
    global session_manager
    session_manager = sm

@router.get("/posts", response_model=List[Post])
async def get_posts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    exclude_ads: bool = Query(False),
    exclude_suggested: bool = Query(False),
    post_type: Optional[str] = Query(None)
):
    """Extract posts from Facebook feed"""
    if not session_manager or not session_manager.page:
        return {"error": "Browser not initialized"}
    
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
