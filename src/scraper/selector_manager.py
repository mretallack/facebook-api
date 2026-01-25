"""
Selector manager with fallback mechanisms and auto-discovery.
Handles Facebook UI changes by maintaining multiple selector strategies.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Selector:
    """A selector with metadata."""
    value: str
    type: str  # 'css', 'xpath', 'text', 'testid'
    priority: int  # Lower = higher priority
    last_success: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    

class SelectorManager:
    """Manages selectors with fallback strategies and auto-discovery."""
    
    # Selector database with primary and fallback options
    SELECTORS = {
        'login_email': [
            Selector('input[name="email"]', 'css', 1),
            Selector('input[id="email"]', 'css', 2),
            Selector('//input[@type="text" or @type="email"]', 'xpath', 3),
        ],
        'login_password': [
            Selector('input[name="pass"]', 'css', 1),
            Selector('input[id="pass"]', 'css', 2),
            Selector('//input[@type="password"]', 'xpath', 3),
        ],
        'login_button': [
            Selector('button[name="login"]', 'css', 1),
            Selector('button[type="submit"]', 'css', 2),
            Selector('//button[contains(text(), "Log in")]', 'xpath', 3),
        ],
        'post_composer': [
            Selector('[role="textbox"][contenteditable="true"]', 'css', 1),
            Selector('div[data-testid="status-attachment-mentions-input"]', 'css', 2),
            Selector('//div[@role="textbox"]', 'xpath', 3),
        ],
        'post_submit': [
            Selector('[aria-label="Post"]', 'css', 1),
            Selector('div[aria-label="Post"][role="button"]', 'css', 2),
            Selector('//div[@role="button" and contains(text(), "Post")]', 'xpath', 3),
        ],
        'friend_request_button': [
            Selector('[aria-label="Add friend"]', 'css', 1),
            Selector('div[aria-label="Add friend"][role="button"]', 'css', 2),
            Selector('//div[contains(text(), "Add friend")]', 'xpath', 3),
        ],
        'message_composer': [
            Selector('[aria-label="Message"]', 'css', 1),
            Selector('div[contenteditable="true"][role="textbox"]', 'css', 2),
            Selector('//div[@role="textbox"]', 'xpath', 3),
        ],
        'like_button': [
            Selector('[aria-label="Like"]', 'css', 1),
            Selector('div[aria-label="Like"][role="button"]', 'css', 2),
            Selector('//div[@aria-label="Like"]', 'xpath', 3),
        ],
        'comment_input': [
            Selector('[aria-label="Write a comment"]', 'css', 1),
            Selector('div[contenteditable="true"][aria-label*="comment"]', 'css', 2),
            Selector('//div[contains(@aria-label, "comment")]', 'xpath', 3),
        ],
        'share_button': [
            Selector('[aria-label="Send this to friends or post it on your timeline."]', 'css', 1),
            Selector('[aria-label*="Share"]', 'css', 2),
            Selector('//div[contains(@aria-label, "Share")]', 'xpath', 3),
        ],
    }
    
    def __init__(self):
        self.custom_selectors: Dict[str, List[Selector]] = {}
        
    def get_selectors(self, name: str) -> List[Selector]:
        """Get all selectors for a given name, sorted by priority."""
        selectors = self.custom_selectors.get(name, self.SELECTORS.get(name, []))
        return sorted(selectors, key=lambda s: (s.priority, -s.success_count))
    
    def get_best_selector(self, name: str) -> Optional[Selector]:
        """Get the best selector based on success rate."""
        selectors = self.get_selectors(name)
        if not selectors:
            return None
        return selectors[0]
    
    def record_success(self, name: str, selector: Selector):
        """Record successful use of a selector."""
        selector.last_success = datetime.now()
        selector.success_count += 1
        logger.debug(f"Selector success: {name} = {selector.value}")
        
    def record_failure(self, name: str, selector: Selector):
        """Record failed use of a selector."""
        selector.failure_count += 1
        logger.warning(f"Selector failure: {name} = {selector.value}")
        
        # If selector fails too often, increase priority (lower in list)
        if selector.failure_count > 5:
            selector.priority += 1
    
    def add_custom_selector(self, name: str, selector: Selector):
        """Add a custom selector (e.g., from auto-discovery)."""
        if name not in self.custom_selectors:
            self.custom_selectors[name] = []
        self.custom_selectors[name].append(selector)
        logger.info(f"Added custom selector: {name} = {selector.value}")
    
    async def find_element(self, page, name: str):
        """
        Find element using fallback strategy.
        Tries all selectors until one works.
        """
        selectors = self.get_selectors(name)
        
        for selector in selectors:
            try:
                if selector.type == 'css':
                    element = await page.query_selector(selector.value)
                elif selector.type == 'xpath':
                    element = await page.query_selector(f'xpath={selector.value}')
                elif selector.type == 'text':
                    element = await page.query_selector(f'text={selector.value}')
                elif selector.type == 'testid':
                    element = await page.query_selector(f'[data-testid="{selector.value}"]')
                else:
                    continue
                
                if element:
                    self.record_success(name, selector)
                    return element
                else:
                    self.record_failure(name, selector)
                    
            except Exception as e:
                logger.debug(f"Selector {selector.value} failed: {e}")
                self.record_failure(name, selector)
        
        # If all selectors failed, try auto-discovery
        logger.warning(f"All selectors failed for {name}, attempting auto-discovery")
        discovered = await self._auto_discover(page, name)
        if discovered:
            return discovered
        
        return None
    
    async def _auto_discover(self, page, name: str):
        """
        Attempt to auto-discover selector based on common patterns.
        """
        # Try common patterns based on element name
        patterns = self._get_discovery_patterns(name)
        
        for pattern in patterns:
            try:
                element = await page.query_selector(pattern)
                if element:
                    # Add as custom selector with low priority
                    new_selector = Selector(pattern, 'css', 10)
                    self.add_custom_selector(name, new_selector)
                    return element
            except:
                continue
        
        return None
    
    def _get_discovery_patterns(self, name: str) -> List[str]:
        """Get discovery patterns based on element name."""
        patterns = []
        
        if 'button' in name:
            patterns.extend([
                'button[type="submit"]',
                '[role="button"]',
                'button',
            ])
        
        if 'input' in name or 'email' in name or 'password' in name:
            patterns.extend([
                'input[type="text"]',
                'input[type="email"]',
                'input[type="password"]',
                'input',
            ])
        
        if 'composer' in name or 'textbox' in name:
            patterns.extend([
                '[role="textbox"]',
                '[contenteditable="true"]',
                'textarea',
            ])
        
        return patterns
    
    def get_health_report(self) -> Dict:
        """Get health report of all selectors."""
        report = {}
        
        for name, selectors in {**self.SELECTORS, **self.custom_selectors}.items():
            selector_stats = []
            for sel in selectors:
                total = sel.success_count + sel.failure_count
                success_rate = sel.success_count / total if total > 0 else 0
                selector_stats.append({
                    'value': sel.value,
                    'type': sel.type,
                    'success_rate': success_rate,
                    'total_uses': total,
                    'last_success': sel.last_success.isoformat() if sel.last_success else None,
                })
            
            report[name] = selector_stats
        
        return report
