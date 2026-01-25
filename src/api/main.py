from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.api.routes import posts
from src.api.models import AuthRequest, AuthResponse, HealthResponse
from src.scraper.session_manager import SessionManager
from config.settings import settings

session_manager = SessionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await session_manager.start()
    posts.set_session_manager(session_manager)
    
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
    title="Facebook Scraper API",
    description="Extract and filter Facebook posts",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router, tags=["posts"])

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
