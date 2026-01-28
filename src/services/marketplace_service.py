"""Marketplace service for Facebook marketplace"""
import asyncio
from typing import List, Dict
from playwright.async_api import Page


class MarketplaceService:
    def __init__(self, page: Page):
        self.page = page
    
    async def search_listings(self, query: str, limit: int = 10) -> List[Dict]:
        """Search marketplace listings"""
        try:
            search_url = f"https://www.facebook.com/marketplace/search/?query={query}"
            await self.page.goto(search_url, timeout=30000, wait_until='networkidle')
            await asyncio.sleep(3)
            
            listings = []
            listing_cards = await self.page.query_selector_all('[role="article"]')
            
            for card in listing_cards[:limit]:
                try:
                    link = await card.query_selector('a[href*="/marketplace/item/"]')
                    if not link:
                        continue
                    
                    title_elem = await card.query_selector('span')
                    title = await title_elem.inner_text() if title_elem else ""
                    
                    url = await link.get_attribute('href')
                    
                    listings.append({
                        'title': title.strip(),
                        'url': url if url.startswith('http') else f"https://www.facebook.com{url}",
                        'price': '',
                        'location': '',
                        'seller': ''
                    })
                except:
                    continue
            
            return listings
        except Exception as e:
            print(f"Search listings error: {e}")
            return []
    
    async def get_listing(self, listing_id: str) -> Dict:
        """Get listing details"""
        try:
            listing_url = f"https://www.facebook.com/marketplace/item/{listing_id}"
            await self.page.goto(listing_url, timeout=30000, wait_until='networkidle')
            await asyncio.sleep(2)
            
            title = ""
            title_elem = await self.page.query_selector('h1')
            if title_elem:
                title = await title_elem.inner_text()
            
            return {
                'id': listing_id,
                'title': title.strip(),
                'description': '',
                'price': '',
                'location': '',
                'seller': '',
                'condition': ''
            }
        except Exception as e:
            print(f"Get listing error: {e}")
            return {}
    
    async def create_listing(self, title: str, price: str, description: str, 
                           category: str = "other") -> bool:
        """Create marketplace listing"""
        try:
            await self.page.goto("https://www.facebook.com/marketplace/create", 
                               timeout=30000, wait_until='networkidle')
            await asyncio.sleep(2)
            
            # Fill listing form
            title_input = await self.page.query_selector('input[placeholder*="title"]')
            if title_input:
                await title_input.type(title)
            
            price_input = await self.page.query_selector('input[placeholder*="price"]')
            if price_input:
                await price_input.type(price)
            
            desc_input = await self.page.query_selector('textarea')
            if desc_input:
                await desc_input.type(description)
            
            await asyncio.sleep(1)
            
            # Submit
            next_button = await self.page.query_selector('text="Next"')
            if next_button:
                await next_button.click()
                await asyncio.sleep(2)
                return True
            
            return False
        except Exception as e:
            print(f"Create listing error: {e}")
            return False
