from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.api.routes import posts, profile, friends, groups, messages, search, events, pages, marketplace, stories, auth, media, graph_api, debug
from src.api.routes import cache as cache_routes
from src.api.models import AuthRequest, AuthResponse, HealthResponse
from src.scraper.session_manager import SessionManager
from src.scraper.preflight_checker import PreflightChecker
from src.scraper.selector_manager import SelectorManager
from src.scraper.profile_service import ProfileService
from src.scraper.friends_service import FriendsService
from src.scraper.posts_service import PostsService
from src.scraper.groups_service import GroupsService
from src.scraper.messages_service import MessagesService
from src.scraper.search_service import SearchService
from src.services.events_service import EventsService
from src.services.pages_service import PagesService
from src.services.marketplace_service import MarketplaceService
from src.services.stories_service import StoriesService
from src.cache.database import init_database
from src.cache.cache_service import CacheService
from src.cache.refresh_tasks import RefreshTasks
from src.cache.scheduler import CacheScheduler
from src.scraper.session_keeper import SessionKeeper
from config.settings import settings

session_manager = SessionManager()
preflight_checker = PreflightChecker()
selector_manager = SelectorManager()

# Initialize cache
cache_engine = init_database(settings.CACHE_DB_PATH)
cache_service = CacheService(cache_engine)
cache_scheduler = None
session_keeper = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global cache_scheduler, session_keeper
    
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
    
    search_service = SearchService(session_manager.page)
    search.set_search_service(search_service)
    
    # Initialize new services
    events_service = EventsService(session_manager.page)
    events.set_events_service(events_service)
    
    pages_service = PagesService(session_manager.page)
    pages.set_pages_service(pages_service)
    
    marketplace_service = MarketplaceService(session_manager.page)
    marketplace.set_marketplace_service(marketplace_service)
    
    stories_service = StoriesService(session_manager.page)
    stories.set_stories_service(stories_service)
    
    # Set session manager for auth
    auth.set_session_manager(session_manager)
    
    # Set cache service for routes
    posts.set_cache_service(cache_service)
    friends.set_cache_service(cache_service)
    profile.set_cache_service(cache_service)
    cache_routes.set_cache_service(cache_service)
    
    # Check if already logged in
    if not await session_manager.is_logged_in():
        if settings.FB_EMAIL and settings.FB_PASSWORD:
            try:
                await session_manager.login()
            except Exception as e:
                print(f"Auto-login failed: {e}")
    
    # Disable cache scheduler to prevent page conflicts
    # Disable cache scheduler to prevent page conflicts
    # if settings.CACHE_ENABLED:
    #     services_dict = {
    #         'posts': posts_service,
    #         'friends': friends_service,
    #         'profile': profile_service
    #     }
    #     refresh_tasks = RefreshTasks(cache_service, session_manager, services_dict)
    #     cache_routes.set_refresh_tasks(refresh_tasks)
    #     cache_scheduler = CacheScheduler(refresh_tasks)
    #     cache_scheduler.start()
    
    # Start session keeper (without navigation)
    session_keeper = SessionKeeper(session_manager, interval_minutes=3)
    session_keeper.start()
    
    yield
    
    # Shutdown
    if session_keeper:
        session_keeper.stop()
    # if cache_scheduler:
    #     cache_scheduler.stop()
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

app.include_router(auth.router)
app.include_router(graph_api.router, prefix="/graph", tags=["Graph API"])
app.include_router(debug.router)
app.include_router(posts.router)

# Direct feed endpoint
from src.api.routes import direct_feed
app.include_router(direct_feed.router, prefix="/posts", tags=["Posts"])

app.include_router(profile.router)
app.include_router(friends.router)
app.include_router(groups.router)
app.include_router(messages.router)
app.include_router(search.router)
app.include_router(events.router)
app.include_router(pages.router)
app.include_router(marketplace.router)
app.include_router(stories.router)
app.include_router(cache_routes.router)
app.include_router(media.router)

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
        # Check if already logged in
        if await session_manager.is_logged_in():
            return {"success": True, "message": "Already authenticated"}
        
        await session_manager.login(auth.email, auth.password)
        return {"success": True, "message": "Authentication successful"}
    except Exception as e:
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
