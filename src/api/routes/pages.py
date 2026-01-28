from fastapi import APIRouter, Query
from typing import List, Dict

router = APIRouter(prefix="/pages", tags=["pages"])

pages_service = None

def set_pages_service(service):
    global pages_service
    pages_service = service

@router.get("/search")
async def search_pages(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50)
) -> List[Dict]:
    """Search for pages"""
    return await pages_service.search_pages(q, limit)

@router.get("/{page_id}")
async def get_page(page_id: str) -> Dict:
    """Get page details"""
    return await pages_service.get_page(page_id)

@router.post("/{page_id}/like")
async def like_page(page_id: str) -> Dict:
    """Like a page"""
    success = await pages_service.like_page(page_id)
    return {"success": success, "page_id": page_id}

@router.post("/{page_id}/post")
async def post_to_page(
    page_id: str,
    content: str = Query(..., description="Post content")
) -> Dict:
    """Post to a page"""
    success = await pages_service.post_to_page(page_id, content)
    return {"success": success, "page_id": page_id}
