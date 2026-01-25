"""
Friends API routes.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from ..models import FriendData, FriendRequestData, FriendActionResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/friends", tags=["friends"])

friends_service = None


def set_friends_service(service):
    """Set the friends service instance."""
    global friends_service
    friends_service = service


@router.get("/search", response_model=List[FriendData])
async def search_friends(q: str = Query(..., description="Search query"), limit: int = 20):
    """Search for people."""
    if not friends_service:
        raise HTTPException(status_code=503, detail="Friends service not initialized")
    
    result = await friends_service.search_friends(q, limit)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Search failed'))
    
    return result['data']


@router.get("/list", response_model=List[FriendData])
async def get_friends_list(limit: int = 50):
    """Get list of friends."""
    if not friends_service:
        raise HTTPException(status_code=503, detail="Friends service not initialized")
    
    result = await friends_service.get_friends_list(limit)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to get friends'))
    
    return result['data']


@router.get("/requests", response_model=List[FriendData])
async def get_friend_requests():
    """Get pending friend requests."""
    if not friends_service:
        raise HTTPException(status_code=503, detail="Friends service not initialized")
    
    result = await friends_service.get_friend_requests()
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to get requests'))
    
    return result['data']


@router.post("/request", response_model=FriendActionResponse)
async def send_friend_request(request: FriendRequestData):
    """Send friend request."""
    if not friends_service:
        raise HTTPException(status_code=503, detail="Friends service not initialized")
    
    result = await friends_service.send_friend_request(request.profile_url)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to send request'))
    
    return FriendActionResponse(success=True, message="Friend request sent")


@router.post("/accept/{request_id}", response_model=FriendActionResponse)
async def accept_friend_request(request_id: str):
    """Accept friend request."""
    if not friends_service:
        raise HTTPException(status_code=503, detail="Friends service not initialized")
    
    result = await friends_service.accept_friend_request(request_id)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to accept'))
    
    return FriendActionResponse(success=True, message="Friend request accepted")


@router.post("/reject/{request_id}", response_model=FriendActionResponse)
async def reject_friend_request(request_id: str):
    """Reject friend request."""
    if not friends_service:
        raise HTTPException(status_code=503, detail="Friends service not initialized")
    
    result = await friends_service.reject_friend_request(request_id)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to reject'))
    
    return FriendActionResponse(success=True, message="Friend request rejected")


@router.delete("/{profile_url:path}", response_model=FriendActionResponse)
async def unfriend(profile_url: str):
    """Remove a friend."""
    if not friends_service:
        raise HTTPException(status_code=503, detail="Friends service not initialized")
    
    result = await friends_service.unfriend(profile_url)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to unfriend'))
    
    return FriendActionResponse(success=True, message="Friend removed")


@router.post("/block", response_model=FriendActionResponse)
async def block_user(request: FriendRequestData):
    """Block a user."""
    if not friends_service:
        raise HTTPException(status_code=503, detail="Friends service not initialized")
    
    result = await friends_service.block_user(request.profile_url)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to block'))
    
    return FriendActionResponse(success=True, message="User blocked")
