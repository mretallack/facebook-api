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

settings = Settings()
