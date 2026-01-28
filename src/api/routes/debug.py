from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/debug", tags=["Debug"])

@router.get("/profile/{username}/html", response_class=HTMLResponse)
async def get_profile_html(username: str):
    """Get raw HTML from a profile page"""
    from src.scraper.session_manager import SessionManager
    
    # Use the global session manager
    from src.api.main import session_manager
    
    url = f"https://www.facebook.com/{username}"
    await session_manager.page.goto(url, wait_until='networkidle')
    
    import asyncio
    await asyncio.sleep(3)
    
    html = await session_manager.page.content()
    return html
