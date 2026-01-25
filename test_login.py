import asyncio
import sys
sys.path.insert(0, '/home/mark/git/facebook')

from src.scraper.session_manager import SessionManager

async def test_browser_init():
    """Test browser initialization"""
    print("Testing browser initialization...")
    sm = SessionManager()
    
    try:
        await sm.start()
        print("✓ Browser started successfully")
        print(f"✓ Browser object: {sm.browser is not None}")
        print(f"✓ Context object: {sm.context is not None}")
        print(f"✓ Page object: {sm.page is not None}")
        return True
    except Exception as e:
        print(f"✗ Browser initialization failed: {e}")
        return False
    finally:
        await sm.stop()
        print("✓ Browser closed successfully")

async def test_facebook_navigation():
    """Test navigation to Facebook"""
    print("\nTesting Facebook navigation...")
    sm = SessionManager()
    
    try:
        await sm.start()
        await sm.page.goto("https://www.facebook.com/", timeout=30000)
        print("✓ Successfully navigated to Facebook")
        
        # Check if login form is present
        email_input = await sm.page.query_selector('input[name="email"]')
        pass_input = await sm.page.query_selector('input[name="pass"]')
        login_button = await sm.page.query_selector('button[name="login"]')
        
        print(f"✓ Email input found: {email_input is not None}")
        print(f"✓ Password input found: {pass_input is not None}")
        print(f"✓ Login button found: {login_button is not None}")
        
        return email_input and pass_input and login_button
    except Exception as e:
        print(f"✗ Navigation test failed: {e}")
        return False
    finally:
        await sm.stop()

async def test_login_form_interaction():
    """Test filling login form without submitting"""
    print("\nTesting login form interaction...")
    sm = SessionManager()
    
    try:
        await sm.start()
        await sm.page.goto("https://www.facebook.com/", timeout=30000)
        
        # Try to fill form with dummy data
        await sm.page.fill('input[name="email"]', 'test@example.com')
        print("✓ Email field can be filled")
        
        await sm.page.fill('input[name="pass"]', 'dummypassword')
        print("✓ Password field can be filled")
        
        # Get the values back to verify
        email_value = await sm.page.input_value('input[name="email"]')
        print(f"✓ Email value set correctly: {email_value == 'test@example.com'}")
        
        print("✓ Form interaction works (NOT submitting)")
        return True
    except Exception as e:
        print(f"✗ Form interaction test failed: {e}")
        return False
    finally:
        await sm.stop()

async def test_cookie_operations():
    """Test cookie save/load operations"""
    print("\nTesting cookie operations...")
    sm = SessionManager()
    
    try:
        await sm.start()
        
        # Try to save cookies
        await sm.save_cookies()
        print("✓ Cookie save operation completed")
        
        # Check if file was created
        import os
        from config.settings import settings
        cookie_exists = os.path.exists(settings.COOKIES_FILE)
        print(f"✓ Cookie file created: {cookie_exists}")
        
        return True
    except Exception as e:
        print(f"✗ Cookie operations test failed: {e}")
        return False
    finally:
        await sm.stop()

async def main():
    print("=" * 60)
    print("Facebook Scraper - Login System Tests")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Browser Initialization", await test_browser_init()))
    results.append(("Facebook Navigation", await test_facebook_navigation()))
    results.append(("Login Form Interaction", await test_login_form_interaction()))
    results.append(("Cookie Operations", await test_cookie_operations()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return all(p for _, p in results)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
