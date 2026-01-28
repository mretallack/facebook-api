"""Events service for Facebook events management"""
import asyncio
from typing import List, Dict
from playwright.async_api import Page


class EventsService:
    def __init__(self, page: Page):
        self.page = page
    
    async def search_events(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for events"""
        try:
            search_url = f"https://www.facebook.com/events/search/?q={query}"
            await self.page.goto(search_url, timeout=30000, wait_until='networkidle')
            await asyncio.sleep(2)
            
            events = []
            event_cards = await self.page.query_selector_all('[role="article"]')
            
            for card in event_cards[:limit]:
                try:
                    name_elem = await card.query_selector('a[href*="/events/"]')
                    if not name_elem:
                        continue
                    
                    name = await name_elem.inner_text()
                    url = await name_elem.get_attribute('href')
                    
                    events.append({
                        'name': name.strip(),
                        'url': url if url.startswith('http') else f"https://www.facebook.com{url}",
                        'description': '',
                        'start_time': '',
                        'location': ''
                    })
                except:
                    continue
            
            return events
        except Exception as e:
            print(f"Search events error: {e}")
            return []
    
    async def get_event(self, event_id: str) -> Dict:
        """Get event details"""
        try:
            event_url = f"https://www.facebook.com/events/{event_id}"
            await self.page.goto(event_url, timeout=30000, wait_until='networkidle')
            await asyncio.sleep(2)
            
            # Extract event details
            name = ""
            name_elem = await self.page.query_selector('h1')
            if name_elem:
                name = await name_elem.inner_text()
            
            return {
                'id': event_id,
                'name': name.strip(),
                'description': '',
                'start_time': '',
                'end_time': '',
                'location': '',
                'host': ''
            }
        except Exception as e:
            print(f"Get event error: {e}")
            return {}
    
    async def respond_to_event(self, event_id: str, response: str = "interested") -> bool:
        """Respond to event (interested/going/not_going)"""
        try:
            event_url = f"https://www.facebook.com/events/{event_id}"
            await self.page.goto(event_url, timeout=30000, wait_until='networkidle')
            await asyncio.sleep(2)
            
            # Find and click response button
            button_text = {
                'interested': 'Interested',
                'going': 'Going',
                'not_going': 'Can\'t Go'
            }.get(response, 'Interested')
            
            button = await self.page.query_selector(f'text="{button_text}"')
            if button:
                await button.click()
                await asyncio.sleep(1)
                return True
            
            return False
        except Exception as e:
            print(f"Respond to event error: {e}")
            return False
