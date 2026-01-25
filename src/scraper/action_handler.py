"""
Base action handler with retry logic and human-like behavior.
All Facebook actions should inherit from this class.
"""
import asyncio
import random
from typing import Optional, Callable, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ActionHandler:
    """Base class for all Facebook actions with anti-detection features."""
    
    def __init__(self, page, preflight_checker, selector_manager):
        self.page = page
        self.preflight_checker = preflight_checker
        self.selector_manager = selector_manager
        self.max_retries = 3
        self.retry_delay_base = 2.0  # seconds
        
    async def execute(
        self,
        action_type: str,
        action_func: Callable,
        *args,
        account_age_days: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute an action with preflight checks, retries, and error handling.
        
        Args:
            action_type: Type of action for rate limiting (e.g., 'post', 'friend_request')
            action_func: Async function to execute
            account_age_days: Age of account in days (for preflight check)
            *args, **kwargs: Arguments to pass to action_func
            
        Returns:
            Dict with success (bool), data (any), error (str)
        """
        # Preflight check
        preflight = self.preflight_checker.check(action_type, account_age_days)
        if not preflight['passed']:
            return {
                'success': False,
                'error': 'Preflight check failed',
                'risk_score': preflight['risk_score'],
                'failed_checks': preflight['failed_checks'],
            }
        
        # Execute with retries
        for attempt in range(self.max_retries):
            try:
                # Human-like delay before action
                await self._human_delay()
                
                # Execute action
                result = await action_func(*args, **kwargs)
                
                # Record success
                self.preflight_checker.record_action(action_type)
                
                logger.info(f"Action {action_type} succeeded on attempt {attempt + 1}")
                
                return {
                    'success': True,
                    'data': result,
                    'attempts': attempt + 1,
                }
                
            except Exception as e:
                logger.warning(f"Action {action_type} failed on attempt {attempt + 1}: {e}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff with jitter
                    delay = self.retry_delay_base * (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                else:
                    return {
                        'success': False,
                        'error': str(e),
                        'attempts': attempt + 1,
                    }
        
        return {
            'success': False,
            'error': 'Max retries exceeded',
            'attempts': self.max_retries,
        }
    
    async def _human_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """Add human-like delay before actions."""
        delay = random.uniform(min_ms, max_ms) / 1000
        await asyncio.sleep(delay)
    
    async def human_type(self, element, text: str):
        """Type text with human-like delays between keystrokes."""
        for char in text:
            await element.type(char)
            # Random delay between 50-150ms per character
            await asyncio.sleep(random.uniform(0.05, 0.15))
    
    async def human_click(self, element):
        """Click with human-like behavior."""
        # Small delay before click
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Move mouse to element (if supported)
        try:
            box = await element.bounding_box()
            if box:
                # Click at random position within element
                x = box['x'] + random.uniform(5, box['width'] - 5)
                y = box['y'] + random.uniform(5, box['height'] - 5)
                await self.page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.05, 0.15))
        except:
            pass
        
        await element.click()
        
        # Small delay after click
        await asyncio.sleep(random.uniform(0.1, 0.3))
    
    async def scroll_slowly(self, distance: int = 300):
        """Scroll page slowly like a human."""
        steps = random.randint(3, 6)
        step_size = distance / steps
        
        for _ in range(steps):
            await self.page.evaluate(f'window.scrollBy(0, {step_size})')
            await asyncio.sleep(random.uniform(0.1, 0.3))
    
    async def wait_for_element(
        self,
        selector_name: str,
        timeout: int = 10000,
        state: str = 'visible'
    ):
        """
        Wait for element using selector manager with fallback.
        
        Args:
            selector_name: Name of selector in selector manager
            timeout: Timeout in milliseconds
            state: Element state to wait for ('visible', 'attached', 'hidden')
            
        Returns:
            Element or None
        """
        selectors = self.selector_manager.get_selectors(selector_name)
        
        for selector in selectors:
            try:
                if selector.type == 'css':
                    element = await self.page.wait_for_selector(
                        selector.value,
                        timeout=timeout,
                        state=state
                    )
                elif selector.type == 'xpath':
                    element = await self.page.wait_for_selector(
                        f'xpath={selector.value}',
                        timeout=timeout,
                        state=state
                    )
                else:
                    continue
                
                if element:
                    self.selector_manager.record_success(selector_name, selector)
                    return element
                    
            except Exception as e:
                logger.debug(f"Wait failed for {selector.value}: {e}")
                self.selector_manager.record_failure(selector_name, selector)
        
        logger.error(f"All selectors failed for {selector_name}")
        return None
    
    async def safe_navigate(self, url: str, wait_until: str = 'networkidle'):
        """Navigate to URL with error handling."""
        try:
            await self.page.goto(url, wait_until=wait_until, timeout=30000)
            await self._human_delay(1000, 3000)
            return True
        except Exception as e:
            logger.error(f"Navigation failed to {url}: {e}")
            return False
