"""
UI change detector for monitoring Facebook interface changes.
Provides early warning when selectors may break.
"""
from typing import Dict, Optional
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)


class UIChangeDetector:
    """Detects UI changes through DOM structure and screenshot analysis."""
    
    def __init__(self):
        self.dom_signatures: Dict[str, str] = {}
        self.screenshot_hashes: Dict[str, str] = {}
        self.last_check: Dict[str, datetime] = {}
        
    async def capture_baseline(self, page, page_name: str):
        """Capture baseline DOM structure and screenshot for a page."""
        try:
            # Capture DOM structure signature
            dom_sig = await self._get_dom_signature(page)
            self.dom_signatures[page_name] = dom_sig
            
            # Capture screenshot hash
            screenshot = await page.screenshot()
            screenshot_hash = hashlib.md5(screenshot).hexdigest()
            self.screenshot_hashes[page_name] = screenshot_hash
            
            self.last_check[page_name] = datetime.now()
            
            logger.info(f"Captured baseline for {page_name}")
            
        except Exception as e:
            logger.error(f"Failed to capture baseline for {page_name}: {e}")
    
    async def detect_changes(self, page, page_name: str) -> Dict:
        """
        Detect if UI has changed since baseline.
        
        Returns:
            Dict with changed (bool), dom_changed (bool), visual_changed (bool), details
        """
        if page_name not in self.dom_signatures:
            logger.warning(f"No baseline for {page_name}, capturing now")
            await self.capture_baseline(page, page_name)
            return {'changed': False, 'dom_changed': False, 'visual_changed': False}
        
        try:
            # Check DOM structure
            current_dom = await self._get_dom_signature(page)
            dom_changed = current_dom != self.dom_signatures[page_name]
            
            # Check visual appearance (screenshot)
            screenshot = await page.screenshot()
            current_hash = hashlib.md5(screenshot).hexdigest()
            visual_changed = current_hash != self.screenshot_hashes[page_name]
            
            result = {
                'changed': dom_changed or visual_changed,
                'dom_changed': dom_changed,
                'visual_changed': visual_changed,
                'page_name': page_name,
                'checked_at': datetime.now().isoformat(),
            }
            
            if result['changed']:
                logger.warning(f"UI change detected on {page_name}: {result}")
                await self._save_diagnostics(page, page_name)
            
            self.last_check[page_name] = datetime.now()
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to detect changes for {page_name}: {e}")
            return {'changed': False, 'error': str(e)}
    
    async def _get_dom_signature(self, page) -> str:
        """
        Get a signature of the DOM structure.
        Uses key structural elements to detect layout changes.
        """
        try:
            # Get structure of key elements
            structure = await page.evaluate("""
                () => {
                    const getStructure = (el, depth = 0) => {
                        if (depth > 3) return '';
                        
                        let sig = el.tagName;
                        if (el.role) sig += `[${el.role}]`;
                        if (el.getAttribute('data-testid')) sig += `#${el.getAttribute('data-testid')}`;
                        
                        const children = Array.from(el.children)
                            .map(child => getStructure(child, depth + 1))
                            .join(',');
                        
                        return sig + (children ? `(${children})` : '');
                    };
                    
                    return getStructure(document.body);
                }
            """)
            
            # Hash the structure for comparison
            return hashlib.md5(structure.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to get DOM signature: {e}")
            return ""
    
    async def _save_diagnostics(self, page, page_name: str):
        """Save diagnostic information when UI change is detected."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save screenshot
            screenshot_path = f"ui_change_{page_name}_{timestamp}.png"
            await page.screenshot(path=screenshot_path)
            logger.info(f"Saved screenshot: {screenshot_path}")
            
            # Save HTML
            html = await page.content()
            html_path = f"ui_change_{page_name}_{timestamp}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Saved HTML: {html_path}")
            
            # Save DOM structure
            dom_structure = await page.evaluate("""
                () => {
                    const getTree = (el, depth = 0) => {
                        if (depth > 5) return null;
                        
                        const info = {
                            tag: el.tagName,
                            role: el.getAttribute('role'),
                            testid: el.getAttribute('data-testid'),
                            ariaLabel: el.getAttribute('aria-label'),
                            classes: el.className,
                        };
                        
                        info.children = Array.from(el.children)
                            .map(child => getTree(child, depth + 1))
                            .filter(c => c !== null);
                        
                        return info;
                    };
                    
                    return getTree(document.body);
                }
            """)
            
            import json
            dom_path = f"ui_change_{page_name}_{timestamp}.json"
            with open(dom_path, 'w') as f:
                json.dump(dom_structure, f, indent=2)
            logger.info(f"Saved DOM structure: {dom_path}")
            
        except Exception as e:
            logger.error(f"Failed to save diagnostics: {e}")
    
    def get_status(self) -> Dict:
        """Get status of all monitored pages."""
        status = {}
        
        for page_name in self.dom_signatures.keys():
            status[page_name] = {
                'has_baseline': True,
                'last_check': self.last_check.get(page_name).isoformat() if page_name in self.last_check else None,
            }
        
        return status
