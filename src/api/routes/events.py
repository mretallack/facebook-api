from fastapi import APIRouter, Query
from typing import List, Dict

router = APIRouter(prefix="/events", tags=["events"])

events_service = None

def set_events_service(service):
    global events_service
    events_service = service

@router.get("/search")
async def search_events(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50)
) -> List[Dict]:
    """Search for events"""
    return await events_service.search_events(q, limit)

@router.get("/{event_id}")
async def get_event(event_id: str) -> Dict:
    """Get event details"""
    return await events_service.get_event(event_id)

@router.post("/{event_id}/rsvp")
async def rsvp_event(
    event_id: str,
    response: str = Query("interested", description="interested, going, or not_going")
) -> Dict:
    """RSVP to event"""
    success = await events_service.respond_to_event(event_id, response)
    return {"success": success, "event_id": event_id, "response": response}
