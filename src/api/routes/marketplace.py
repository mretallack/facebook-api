from fastapi import APIRouter, Query
from typing import List, Dict

router = APIRouter(prefix="/marketplace", tags=["marketplace"])

marketplace_service = None

def set_marketplace_service(service):
    global marketplace_service
    marketplace_service = service

@router.get("/search")
async def search_listings(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50)
) -> List[Dict]:
    """Search marketplace listings"""
    return await marketplace_service.search_listings(q, limit)

@router.get("/{listing_id}")
async def get_listing(listing_id: str) -> Dict:
    """Get listing details"""
    return await marketplace_service.get_listing(listing_id)

@router.post("/create")
async def create_listing(
    title: str = Query(..., description="Listing title"),
    price: str = Query(..., description="Price"),
    description: str = Query(..., description="Description"),
    category: str = Query("other", description="Category")
) -> Dict:
    """Create marketplace listing"""
    success = await marketplace_service.create_listing(title, price, description, category)
    return {"success": success}
