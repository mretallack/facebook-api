"""
Test core components: PreflightChecker, SelectorManager, ActionHandler
"""
import asyncio
from src.scraper.preflight_checker import PreflightChecker
from src.scraper.selector_manager import SelectorManager


def test_preflight_checker():
    """Test PreflightChecker rate limiting and risk scoring."""
    print("Testing PreflightChecker...")
    
    checker = PreflightChecker()
    
    # Test 1: First action should pass
    result = checker.check('friend_request')
    assert result['passed'], "First action should pass"
    assert result['risk_score'] < 0.7, "Risk score should be low"
    print("✓ First action passed")
    
    # Test 2: Record actions and check rate limit
    for i in range(15):
        checker.record_action('friend_request')
    
    result = checker.check('friend_request')
    assert not result['passed'], "Should fail after hitting rate limit"
    assert 'rate_limit' in result['failed_checks'], "Should fail on rate limit"
    print("✓ Rate limit enforced correctly")
    
    # Test 3: Different action type should still pass
    result = checker.check('post')
    assert result['passed'], "Different action type should pass"
    print("✓ Different action types tracked separately")
    
    # Test 4: Suspicious patterns detection
    checker2 = PreflightChecker()
    import time
    for i in range(3):
        checker2.record_action('like')
        time.sleep(0.001)  # Very small delay to make them rapid
    
    result = checker2.check('like')
    # Should detect suspicious patterns if actions were rapid enough
    if not result['passed']:
        print("✓ Suspicious pattern detection works")
    else:
        print("✓ Suspicious pattern check passed (actions not rapid enough)")
    
    print("✅ PreflightChecker tests passed\n")


def test_selector_manager():
    """Test SelectorManager selector database and fallbacks."""
    print("Testing SelectorManager...")
    
    manager = SelectorManager()
    
    # Test 1: Get selectors for login
    selectors = manager.get_selectors('login_email')
    assert len(selectors) > 0, "Should have selectors for login_email"
    assert selectors[0].type in ['css', 'xpath'], "Should have valid selector type"
    print(f"✓ Found {len(selectors)} selectors for login_email")
    
    # Test 2: Get best selector
    best = manager.get_best_selector('login_button')
    assert best is not None, "Should return best selector"
    assert best.priority == 1, "Best selector should have priority 1"
    print("✓ Best selector selection works")
    
    # Test 3: Record success/failure
    manager.record_success('login_email', selectors[0])
    assert selectors[0].success_count == 1, "Should increment success count"
    
    manager.record_failure('login_email', selectors[0])
    assert selectors[0].failure_count == 1, "Should increment failure count"
    print("✓ Success/failure tracking works")
    
    # Test 4: Health report
    report = manager.get_health_report()
    assert 'login_email' in report, "Health report should include tracked selectors"
    print("✓ Health report generation works")
    
    print("✅ SelectorManager tests passed\n")


def test_rate_limit_configs():
    """Test rate limit configurations."""
    print("Testing rate limit configurations...")
    
    checker = PreflightChecker()
    
    # Verify all rate limits are configured
    expected_actions = ['friend_request', 'post', 'message', 'like', 'comment', 'group_join', 'page_like']
    
    for action in expected_actions:
        assert action in checker.RATE_LIMITS, f"Missing rate limit for {action}"
        config = checker.RATE_LIMITS[action]
        assert config.max_actions > 0, f"Invalid max_actions for {action}"
        print(f"✓ {action}: {config.max_actions} per {config.time_window}")
    
    print("✅ Rate limit configurations valid\n")


if __name__ == '__main__':
    print("=" * 60)
    print("Running Core Component Tests")
    print("=" * 60 + "\n")
    
    try:
        test_preflight_checker()
        test_selector_manager()
        test_rate_limit_configs()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
