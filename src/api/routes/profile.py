"""
Profile API routes.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Response
from ..models import ProfileData, ProfileUpdateRequest, ProfilePictureResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profile", tags=["profile"])

# Global service instance (will be set by main app)
profile_service = None
cache_service = None


def set_profile_service(service):
    """Set the profile service instance."""
    global profile_service
    profile_service = service


def set_cache_service(service):
    """Set the cache service instance."""
    global cache_service
    cache_service = service


@router.get("/me", response_model=ProfileData)
async def get_profile(response: Response, fresh: bool = Query(False)):
    """Get current user's profile information."""
    
    # Try cache first
    if cache_service and not fresh:
        cached_profile = cache_service.get_profile()
        if cached_profile:
            response.headers["X-Cache-Hit"] = "true"
            return cached_profile
    
    response.headers["X-Cache-Hit"] = "false"
    
    if not profile_service:
        raise HTTPException(status_code=503, detail="Profile service not initialized")
    
    result = await profile_service.get_profile()
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to get profile'))
    
    return result['data']


@router.put("/me", response_model=ProfileData)
async def update_profile(request: ProfileUpdateRequest):
    """Update profile information."""
    if not profile_service:
        raise HTTPException(status_code=503, detail="Profile service not initialized")
    
    result = await profile_service.update_profile(
        name=request.name,
        bio=request.bio
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to update profile'))
    
    return result['data']


@router.post("/picture", response_model=ProfilePictureResponse)
async def upload_profile_picture(file: UploadFile = File(...)):
    """Upload profile picture."""
    if not profile_service:
        raise HTTPException(status_code=503, detail="Profile service not initialized")
    
    # Save uploaded file temporarily
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        result = await profile_service.upload_profile_picture(tmp_path)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error', 'Failed to upload picture'))
        
        return ProfilePictureResponse(success=True, **result['data'])
    
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/cover", response_model=ProfilePictureResponse)
async def upload_cover_photo(file: UploadFile = File(...)):
    """Upload cover photo."""
    if not profile_service:
        raise HTTPException(status_code=503, detail="Profile service not initialized")
    
    # Save uploaded file temporarily
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        result = await profile_service.upload_cover_photo(tmp_path)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error', 'Failed to upload cover'))
        
        return ProfilePictureResponse(success=True, **result['data'])
    
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
