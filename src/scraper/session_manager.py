import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from config.settings import settings

class SessionManager:
    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        
    async def start(self):
        """Initialize browser and context"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=settings.HEADLESS,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        # Load cookies if they exist
        cookies_path = Path(settings.COOKIES_FILE)
        if cookies_path.exists():
            with open(cookies_path, 'r') as f:
                cookies = json.load(f)
            self.context = await self.browser.new_context(
                storage_state=cookies,
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
        else:
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
        
        self.page = await self.context.new_page()
        
        # Hide automation flags
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
    async def stop(self):
        """Close browser and cleanup"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def save_cookies(self):
        """Save current session cookies"""
        if self.context:
            storage_state = await self.context.storage_state()
            with open(settings.COOKIES_FILE, 'w') as f:
                json.dump(storage_state, f)
    
    async def login(self, email: str = None, password: str = None):
        """Login to Facebook"""
        email = email or settings.FB_EMAIL
        password = password or settings.FB_PASSWORD
        
        if not email or not password:
            raise ValueError("Email and password required")
        
        await self.page.goto("https://www.facebook.com/")
        await asyncio.sleep(3)
        
        # Try to close cookie dialog - multiple possible selectors
        try:
            # Try common cookie accept buttons
            selectors = [
                'button[data-cookiebanner="accept_button"]',
                'button:has-text("Allow all cookies")',
                'button:has-text("Accept all")',
                '[data-testid="cookie-policy-manage-dialog"] button:has-text("Allow")',
                'button[title="Allow all cookies"]'
            ]
            for selector in selectors:
                try:
                    button = await self.page.wait_for_selector(selector, timeout=2000)
                    if button:
                        await button.click()
                        await asyncio.sleep(1)
                        break
                except:
                    continue
        except:
            pass
        
        # Fill login form
        print(f"Filling email: {email[:10]}...")
        await self.page.fill('input[name="email"]', email)
        await asyncio.sleep(0.5)
        
        print("Filling password...")
        await self.page.fill('input[name="pass"]', password)
        await asyncio.sleep(0.5)
        
        print("Clicking login button...")
        # Use force click to bypass overlays
        await self.page.click('button[name="login"]', force=True)
        
        # Wait for navigation or error
        print("Waiting for response...")
        try:
            await self.page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
        
        await asyncio.sleep(3)
        
        # Save cookies after successful login
        await self.save_cookies()
        
    async def is_logged_in(self) -> bool:
        """Check if currently logged in"""
        try:
            await self.page.goto("https://www.facebook.com/", timeout=10000)
            await asyncio.sleep(2)
            # If we see login form, we're not logged in
            login_form = await self.page.query_selector('input[name="email"]')
            return login_form is None
        except:
            return False
