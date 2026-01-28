import json
import asyncio
import random
from pathlib import Path
from typing import Dict, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from config.settings import settings

class SessionManager:
    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}
        self.current_account: Optional[str] = None
        
        # Legacy single-account support
        self.context: BrowserContext = None
        self.page: Page = None
        
    async def start(self, account_id: str = "default"):
        """Initialize browser and context for account"""
        if not self.playwright:
            self.playwright = await async_playwright().start()
        
        if not self.browser:
            self.browser = await self.playwright.chromium.launch(
                headless=settings.HEADLESS,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
        
        # Load cookies for this account
        cookies_path = Path(f"cookies/{account_id}.json")
        if cookies_path.exists():
            with open(cookies_path, 'r') as f:
                cookies = json.load(f)
            context = await self.browser.new_context(
                storage_state=cookies,
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
        else:
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
        
        page = await context.new_page()
        
        # Hide automation flags
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.contexts[account_id] = context
        self.pages[account_id] = page
        self.current_account = account_id
        
        # Legacy support
        self.context = context
        self.page = page
        
        return page
        
    async def stop(self, account_id: Optional[str] = None):
        """Close browser and cleanup"""
        if account_id:
            # Close specific account
            if account_id in self.pages:
                try:
                    await self.pages[account_id].close()
                    del self.pages[account_id]
                except:
                    pass
            if account_id in self.contexts:
                try:
                    await self.contexts[account_id].close()
                    del self.contexts[account_id]
                except:
                    pass
        else:
            # Close all
            for page in self.pages.values():
                try:
                    await page.close()
                except:
                    pass
            self.pages.clear()
            
            for context in self.contexts.values():
                try:
                    await context.close()
                except:
                    pass
            self.contexts.clear()
            
            if self.browser:
                try:
                    await self.browser.close()
                except:
                    pass
            if self.playwright:
                try:
                    await self.playwright.stop()
                except:
                    pass
    
    def get_page(self, account_id: str = "default") -> Optional[Page]:
        """Get page for account"""
        return self.pages.get(account_id)
    
    def get_context(self, account_id: str = "default") -> Optional[BrowserContext]:
        """Get context for account"""
        return self.contexts.get(account_id)
    
    async def switch_account(self, account_id: str) -> Page:
        """Switch to different account"""
        if account_id not in self.pages:
            return await self.start(account_id)
        
        self.current_account = account_id
        self.page = self.pages[account_id]
        self.context = self.contexts[account_id]
        return self.page
    
    async def save_cookies(self, account_id: str = "default"):
        """Save current session cookies for account"""
        context = self.contexts.get(account_id)
        if context:
            storage_state = await context.storage_state()
            cookies_dir = Path("cookies")
            cookies_dir.mkdir(exist_ok=True)
            with open(cookies_dir / f"{account_id}.json", 'w') as f:
                json.dump(storage_state, f)
    
    async def login(self, email: str = None, password: str = None, account_id: str = "default"):
        """Login to Facebook for account"""
        email = email or settings.FB_EMAIL
        password = password or settings.FB_PASSWORD
        
        if not email or not password:
            raise ValueError("Email and password required")
        
        page = self.pages.get(account_id) or self.page
        if not page:
            raise ValueError(f"No page for account {account_id}")
        
        await page.goto("https://www.facebook.com/")
        await asyncio.sleep(random.uniform(2, 4))
        
        # Try to dismiss cookie dialog
        try:
            await page.evaluate("""
                const dialog = document.querySelector('[data-testid="cookie-policy-manage-dialog"]');
                if (dialog) dialog.remove();
            """)
            await asyncio.sleep(0.5)
        except:
            pass
        
        # Fill login form
        print(f"Logging in account {account_id}...")
        email_input = await page.wait_for_selector('input[name="email"]')
        await email_input.click()
        await asyncio.sleep(random.uniform(0.3, 0.7))
        await email_input.type(email, delay=random.uniform(50, 150))
        await asyncio.sleep(random.uniform(0.5, 1))
        
        pass_input = await page.wait_for_selector('input[name="pass"]')
        await pass_input.click()
        await asyncio.sleep(random.uniform(0.3, 0.7))
        await pass_input.type(password, delay=random.uniform(50, 150))
        await asyncio.sleep(random.uniform(0.5, 1))
        
        await page.evaluate("""
            document.querySelector('button[name="login"]').click();
        """)
        
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except:
            pass
        
        await asyncio.sleep(3)
        await self.save_cookies(account_id)
        
    async def is_logged_in(self, account_id: str = "default") -> bool:
        """Check if account is logged in"""
        page = self.pages.get(account_id) or self.page
        if not page:
            return False
        
        try:
            await page.goto("https://www.facebook.com/", timeout=10000)
            await asyncio.sleep(2)
            login_form = await page.query_selector('input[name="email"]')
            return login_form is None
        except:
            return False
