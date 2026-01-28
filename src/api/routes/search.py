from fastapi import APIRouter, Query
from typing import List
from src.api.models import Person, ProfileDetails

router = APIRouter(prefix="/search", tags=["search"])

search_service = None

def set_search_service(service):
    global search_service
    search_service = service

@router.get("/people", response_model=List[Person])
async def search_people(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=50)
):
    """Search for people on Facebook"""
    results = await search_service.search_people(q, limit)
    return results

@router.get("/profile", response_model=ProfileDetails)
async def get_profile_details(
    url: str = Query(..., description="Profile URL")
):
    """Get detailed profile information"""
    details = await search_service.get_profile_details(url)
    return details
