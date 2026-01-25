import asyncio
import sys
sys.path.insert(0, '/home/mark/git/facebook')

from src.scraper.session_manager import SessionManager
from config.settings import settings

async def test_real_login():
    print("Testing real Facebook login...")
    print(f"Email: {settings.FB_EMAIL}")
    
    sm = SessionManager()
    
    try:
        await sm.start()
        print("✓ Browser started")
        
        # Try to login
        await sm.login()
        print("✓ Login attempt completed")
        
        # Wait a bit for any redirects
        await asyncio.sleep(5)
        
        # Check if logged in
        is_logged_in = await sm.is_logged_in()
        print(f"Login status: {is_logged_in}")
        print(f"Current URL: {sm.page.url}")
        
        # Check page title
        title = await sm.page.title()
        print(f"Page title: {title}")
        
        # Check for error messages
        try:
            error_elem = await sm.page.query_selector('[data-testid="royal_login_error"]')
            if error_elem:
                error_text = await error_elem.inner_text()
                print(f"Error message: {error_text}")
        except:
            pass
        
        if is_logged_in:
            print("✓ Successfully logged in!")
            return True
        else:
            print("✗ Login failed - possible reasons:")
            print("  - Incorrect credentials")
            print("  - Account needs verification")
            print("  - Facebook detected automation")
            print("  - 2FA required")
            # Take screenshot for debugging
            await sm.page.screenshot(path="login_failed.png")
            print("Screenshot saved to login_failed.png")
            return False
        
        return is_logged_in
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await sm.stop()

if __name__ == "__main__":
    success = asyncio.run(test_real_login())
    sys.exit(0 if success else 1)
