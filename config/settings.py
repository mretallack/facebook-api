import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    FB_EMAIL: str = os.getenv("FB_EMAIL", "")
    FB_PASSWORD: str = os.getenv("FB_PASSWORD", "")
    
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    BROWSER_TIMEOUT: int = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    
    COOKIES_FILE: str = "cookies.json"
    
    # Cache settings
    CACHE_DB_PATH: str = os.getenv("CACHE_DB_PATH", "cache.db")
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    
    # Refresh intervals (minutes)
    CACHE_REFRESH_POSTS: int = int(os.getenv("CACHE_REFRESH_POSTS", "5"))
    CACHE_REFRESH_FRIENDS: int = int(os.getenv("CACHE_REFRESH_FRIENDS", "15"))
    CACHE_REFRESH_PROFILE: int = int(os.getenv("CACHE_REFRESH_PROFILE", "30"))
    CACHE_REFRESH_REQUESTS: int = int(os.getenv("CACHE_REFRESH_REQUESTS", "10"))
    
    # Cache expiry (hours)
    CACHE_EXPIRY_POSTS: int = int(os.getenv("CACHE_EXPIRY_POSTS", "1"))
    CACHE_EXPIRY_FRIENDS: int = int(os.getenv("CACHE_EXPIRY_FRIENDS", "4"))
    CACHE_EXPIRY_PROFILE: int = int(os.getenv("CACHE_EXPIRY_PROFILE", "8"))
    CACHE_EXPIRY_REQUESTS: int = int(os.getenv("CACHE_EXPIRY_REQUESTS", "2"))
    
    # Rate limiting
    CACHE_MIN_SCRAPE_INTERVAL: int = int(os.getenv("CACHE_MIN_SCRAPE_INTERVAL", "60"))  # seconds
    CACHE_MAX_ERROR_COUNT: int = int(os.getenv("CACHE_MAX_ERROR_COUNT", "3"))

settings = Settings()
