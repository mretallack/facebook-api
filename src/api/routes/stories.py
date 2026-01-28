from fastapi import APIRouter, Query, UploadFile, File
from typing import List, Dict, Optional

router = APIRouter(prefix="/stories", tags=["stories"])

stories_service = None

def set_stories_service(service):
    global stories_service
    stories_service = service

@router.get("/feed")
async def get_stories() -> List[Dict]:
    """Get available stories"""
    return await stories_service.get_stories()

@router.post("/create")
async def create_story(
    text: Optional[str] = Query(None, description="Text for story"),
    image: Optional[UploadFile] = File(None)
) -> Dict:
    """Create a story"""
    image_path = None
    if image:
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await image.read()
            tmp.write(content)
            image_path = tmp.name
    
    success = await stories_service.create_story(image_path, text)
    return {"success": success}

@router.delete("/{story_id}")
async def delete_story(story_id: str) -> Dict:
    """Delete a story"""
    success = await stories_service.delete_story(story_id)
    return {"success": success, "story_id": story_id}
