from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.api.routes import posts, profile, friends, groups, messages
from src.api.models import AuthRequest, AuthResponse, HealthResponse
from src.scraper.session_manager import SessionManager
from src.scraper.preflight_checker import PreflightChecker
from src.scraper.selector_manager import SelectorManager
from src.scraper.profile_service import ProfileService
from src.scraper.friends_service import FriendsService
from src.scraper.posts_service import PostsService
from src.scraper.groups_service import GroupsService
from src.scraper.messages_service import MessagesService
from config.settings import settings

session_manager = SessionManager()
preflight_checker = PreflightChecker()
selector_manager = SelectorManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await session_manager.start()
    posts.set_session_manager(session_manager)
    
    # Initialize services
    profile_service = ProfileService(session_manager.page, preflight_checker, selector_manager)
    profile.set_profile_service(profile_service)
    
    friends_service = FriendsService(session_manager.page, preflight_checker, selector_manager)
    friends.set_friends_service(friends_service)
    
    posts_service = PostsService(session_manager.page, preflight_checker, selector_manager)
    posts.set_posts_service(posts_service)
    
    groups_service = GroupsService(session_manager.page, preflight_checker, selector_manager)
    groups.set_groups_service(groups_service)
    
    messages_service = MessagesService(session_manager.page, preflight_checker, selector_manager)
    messages.set_messages_service(messages_service)
    
    # Check if already logged in
    if not await session_manager.is_logged_in():
        if settings.FB_EMAIL and settings.FB_PASSWORD:
            try:
                await session_manager.login()
            except Exception as e:
                print(f"Auto-login failed: {e}")
    
    yield
    
    # Shutdown
    await session_manager.stop()

app = FastAPI(
    title="Facebook API",
    description="Full Facebook automation API",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(profile.router)
app.include_router(friends.router)
app.include_router(groups.router)
app.include_router(messages.router)

@app.get("/health", response_model=HealthResponse)
async def health():
    """Check API and browser status"""
    return {
        "status": "ok",
        "browser_ready": session_manager.browser is not None
    }

@app.post("/auth", response_model=AuthResponse)
async def authenticate(auth: AuthRequest):
    """Authenticate with Facebook"""
    try:
        await session_manager.login(auth.email, auth.password)
        return {"success": True, "message": "Authentication successful"}
    except Exception as e:
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
