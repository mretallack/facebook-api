from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import httpx
import hashlib
from pathlib import Path

router = APIRouter(prefix="/media", tags=["media"])

# Image cache directory
CACHE_DIR = Path("image_cache")
CACHE_DIR.mkdir(exist_ok=True)

async def fetch_and_cache_image(url: str) -> str:
    """Fetch image from URL and cache it locally. Returns cache key."""
    cache_key = hashlib.md5(url.encode()).hexdigest()
    cache_path = CACHE_DIR / f"{cache_key}.jpg"
    
    # If already cached, return key
    if cache_path.exists():
        return cache_key
    
    # Fetch and cache
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True, timeout=10.0)
            if response.status_code == 200:
                cache_path.write_bytes(response.content)
                return cache_key
    except:
        pass
    
    return None

@router.get("/image/{cache_key}")
async def get_cached_image(cache_key: str):
    """Serve cached image"""
    cache_path = CACHE_DIR / f"{cache_key}.jpg"
    
    if not cache_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return Response(content=cache_path.read_bytes(), media_type="image/jpeg")
