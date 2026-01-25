"""
Groups API routes.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from ..models import GroupData, GroupPostRequest, GroupActionResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/groups", tags=["groups"])

groups_service = None


def set_groups_service(service):
    """Set the groups service instance."""
    global groups_service
    groups_service = service


@router.get("/search", response_model=List[GroupData])
async def search_groups(q: str = Query(..., description="Search query"), limit: int = 20):
    """Search for groups."""
    if not groups_service:
        raise HTTPException(status_code=503, detail="Groups service not initialized")
    
    result = await groups_service.search_groups(q, limit)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Search failed'))
    
    return result['data']


@router.get("/{group_id}", response_model=GroupData)
async def get_group(group_id: str):
    """Get group information."""
    if not groups_service:
        raise HTTPException(status_code=503, detail="Groups service not initialized")
    
    result = await groups_service.get_group(group_id)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to get group'))
    
    return result['data']


@router.post("/{group_id}/join", response_model=GroupActionResponse)
async def join_group(group_id: str):
    """Join a group."""
    if not groups_service:
        raise HTTPException(status_code=503, detail="Groups service not initialized")
    
    result = await groups_service.join_group(group_id)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to join group'))
    
    return GroupActionResponse(success=True, message="Joined group")


@router.post("/{group_id}/leave", response_model=GroupActionResponse)
async def leave_group(group_id: str):
    """Leave a group."""
    if not groups_service:
        raise HTTPException(status_code=503, detail="Groups service not initialized")
    
    result = await groups_service.leave_group(group_id)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to leave group'))
    
    return GroupActionResponse(success=True, message="Left group")


@router.post("/{group_id}/post", response_model=GroupActionResponse)
async def post_to_group(group_id: str, request: GroupPostRequest):
    """Post to a group."""
    if not groups_service:
        raise HTTPException(status_code=503, detail="Groups service not initialized")
    
    result = await groups_service.post_to_group(
        group_id,
        request.content,
        request.image_paths
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to post'))
    
    return GroupActionResponse(success=True, message="Posted to group")


@router.get("/{group_id}/posts")
async def get_group_posts(group_id: str, limit: int = 20):
    """Get posts from a group."""
    if not groups_service:
        raise HTTPException(status_code=503, detail="Groups service not initialized")
    
    result = await groups_service.get_group_posts(group_id, limit)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to get posts'))
    
    return result['data']
