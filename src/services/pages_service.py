"""Pages service for Facebook pages management"""
import asyncio
from typing import List, Dict
from playwright.async_api import Page


class PagesService:
    def __init__(self, page: Page):
        self.page = page
    
    async def search_pages(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for pages"""
        try:
            search_url = f"https://www.facebook.com/search/pages/?q={query}"
            await self.page.goto(search_url, timeout=30000, wait_until='networkidle')
            await asyncio.sleep(2)
            
            pages = []
            page_cards = await self.page.query_selector_all('[role="article"]')
            
            for card in page_cards[:limit]:
                try:
                    name_elem = await card.query_selector('a')
                    if not name_elem:
                        continue
                    
                    name = await name_elem.inner_text()
                    url = await name_elem.get_attribute('href')
                    
                    pages.append({
                        'name': name.strip(),
                        'url': url if url.startswith('http') else f"https://www.facebook.com{url}",
                        'category': '',
                        'likes': 0
                    })
                except:
                    continue
            
            return pages
        except Exception as e:
            print(f"Search pages error: {e}")
            return []
    
    async def get_page(self, page_id: str) -> Dict:
        """Get page details"""
        try:
            page_url = f"https://www.facebook.com/{page_id}"
            await self.page.goto(page_url, timeout=30000, wait_until='networkidle')
            await asyncio.sleep(2)
            
            name = ""
            name_elem = await self.page.query_selector('h1')
            if name_elem:
                name = await name_elem.inner_text()
            
            return {
                'id': page_id,
                'name': name.strip(),
                'category': '',
                'likes': 0,
                'description': ''
            }
        except Exception as e:
            print(f"Get page error: {e}")
            return {}
    
    async def like_page(self, page_id: str) -> bool:
        """Like a page"""
        try:
            page_url = f"https://www.facebook.com/{page_id}"
            await self.page.goto(page_url, timeout=30000, wait_until='networkidle')
            await asyncio.sleep(2)
            
            like_button = await self.page.query_selector('text="Like"')
            if like_button:
                await like_button.click()
                await asyncio.sleep(1)
                return True
            
            return False
        except Exception as e:
            print(f"Like page error: {e}")
            return False
    
    async def post_to_page(self, page_id: str, content: str) -> bool:
        """Post to a page (requires admin access)"""
        try:
            page_url = f"https://www.facebook.com/{page_id}"
            await self.page.goto(page_url, timeout=30000, wait_until='networkidle')
            await asyncio.sleep(2)
            
            # Find post composer
            composer = await self.page.query_selector('[role="textbox"]')
            if composer:
                await composer.click()
                await asyncio.sleep(1)
                await composer.type(content)
                await asyncio.sleep(1)
                
                # Find and click post button
                post_button = await self.page.query_selector('text="Post"')
                if post_button:
                    await post_button.click()
                    await asyncio.sleep(2)
                    return True
            
            return False
        except Exception as e:
            print(f"Post to page error: {e}")
            return False
