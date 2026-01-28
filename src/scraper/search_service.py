import asyncio
from typing import List, Dict
from playwright.async_api import Page
from src.core.graphql_extractor import GraphQLExtractor


class SearchService:
    def __init__(self, page: Page):
        self.page = page
    
    async def get_profile_details(self, profile_url: str) -> Dict:
        """Get detailed profile information using GraphQL interception + HTML fallback"""
        
        # Set up GraphQL interception
        extractor = GraphQLExtractor()
        await extractor.intercept_responses(self.page)
        
        try:
            await self.page.goto(profile_url, timeout=10000, wait_until='networkidle')
        except Exception as e:
            print(f"Navigation error: {e}")
            return self._empty_profile()
        
        # Wait for GraphQL requests to complete
        await asyncio.sleep(3)
        
        # Extract from GraphQL
        profile = extractor.extract_profile()
        
        # Save responses for debugging
        extractor.save_responses('/tmp/fb_profile_graphql.json')
        
        print(f"GraphQL responses captured: {len(extractor.responses)}")
        print(f"Extracted fields: {list(profile.keys())}")
        
        # Fallback to HTML if GraphQL didn't provide name
        if not profile.get('name'):
            name_selectors = ['h1', 'h2']
            for selector in name_selectors:
                elem = await self.page.query_selector(selector)
                if elem:
                    text = await elem.inner_text()
                    if text and len(text) < 100:
                        profile['name'] = text.strip()
                        print(f"Extracted name from HTML: {profile['name']}")
                        break
        
        # Ensure all fields exist
        return {
            'name': profile.get('name', ''),
            'bio': profile.get('bio', ''),
            'profile_picture': profile.get('profile_picture', ''),
            'cover_photo': profile.get('cover_photo', ''),
            'friends_count': profile.get('friends_count', ''),
            'followers_count': profile.get('followers_count', ''),
            'location': profile.get('location', ''),
            'work': profile.get('work', ''),
            'education': profile.get('education', ''),
            'relationship': profile.get('relationship', ''),
            'joined': profile.get('joined', '')
        }
    
    def _empty_profile(self) -> Dict:
        """Return empty profile structure"""
        return {
            'name': '',
            'bio': '',
            'profile_picture': '',
            'cover_photo': '',
            'friends_count': '',
            'followers_count': '',
            'location': '',
            'work': '',
            'education': '',
            'relationship': '',
            'joined': ''
        }
    
    async def search_people(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for people on Facebook"""
        try:
            search_url = f"https://www.facebook.com/search/people/?q={query}"
            await self.page.goto(search_url, timeout=30000, wait_until='networkidle')
            await asyncio.sleep(3)
            
            results = []
            result_cards = await self.page.query_selector_all('[role="article"]')
            
            print(f"Found {len(result_cards)} result cards")
            
            for card in result_cards[:limit]:
                try:
                    # Try multiple selectors for name
                    name = ""
                    profile_url = ""
                    
                    # Try to find profile link
                    link_selectors = [
                        'a[href*="/profile.php"]',
                        'a[href*="facebook.com/"]',
                        'a[role="link"]'
                    ]
                    
                    link_elem = None
                    for selector in link_selectors:
                        link_elem = await card.query_selector(selector)
                        if link_elem:
                            profile_url = await link_elem.get_attribute('href')
                            if profile_url and ('facebook.com' in profile_url or profile_url.startswith('/')):
                                break
                    
                    if not profile_url:
                        continue
                    
                    # Extract name from link text or nearby span
                    if link_elem:
                        name = await link_elem.inner_text()
                    
                    # If name is empty, try to find it in spans
                    if not name or len(name) < 2:
                        spans = await card.query_selector_all('span')
                        for span in spans:
                            text = await span.inner_text()
                            if text and len(text) > 2 and len(text) < 100:
                                name = text
                                break
                    
                    if not name:
                        continue
                    
                    # Clean up profile URL
                    if not profile_url.startswith('http'):
                        profile_url = f"https://www.facebook.com{profile_url}"
                    
                    profile_id = profile_url.split('/')[-1] if '/' in profile_url else ''
                    
                    results.append({
                        'id': profile_id,
                        'name': name.strip(),
                        'profile_url': profile_url,
                        'profile_picture': '',
                        'mutual_friends': 0,
                        'location': '',
                        'work': ''
                    })
                    
                    print(f"Extracted: {name.strip()}")
                except Exception as e:
                    print(f"Error extracting card: {e}")
                    continue
            
            print(f"Returning {len(results)} results")
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
