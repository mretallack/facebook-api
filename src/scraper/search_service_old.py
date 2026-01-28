import asyncio
import re
from typing import List, Dict
from playwright.async_api import Page

class SearchService:
    def __init__(self, page: Page):
        self.page = page
    
    async def get_profile_details(self, profile_url: str) -> Dict:
        """Get detailed profile information by intercepting GraphQL responses"""
        profile_data = []
        all_responses = []
        
        # Set up request interception to capture all responses
        async def handle_response(response):
            try:
                url = response.url
                all_responses.append(url)
                
                if 'graphql' in url.lower():
                    try:
                        data = await response.text()
                        import json
                        parsed = json.loads(data)
                        profile_data.append(parsed)
                        print(f"✓ Captured GraphQL ({len(data)} bytes)")
                    except Exception as parse_err:
                        print(f"✗ Parse failed: {str(parse_err)[:50]}")
            except Exception as e:
                pass
        
        self.page.on('response', handle_response)
        
        try:
            await self.page.goto(profile_url, timeout=10000, wait_until='networkidle')
        except Exception as e:
            print(f"Navigation error: {e}")
            self.page.remove_listener('response', handle_response)
            return {}
        
        await asyncio.sleep(3)
        self.page.remove_listener('response', handle_response)
        
        print(f"Total responses: {len(all_responses)}")
        print(f"GraphQL responses: {len(profile_data)}")
        
        # Save captured data for debugging
        if profile_data:
            import json
            with open('/tmp/fb_profile_graphql.json', 'w') as f:
                json.dump(profile_data, f, indent=2)
            print(f"Saved {len(profile_data)} GraphQL responses")
        
        # Save all URLs for debugging
        with open('/tmp/fb_profile_urls.txt', 'w') as f:
            for url in all_responses:
                if 'graphql' in url.lower() or 'api' in url.lower():
                    f.write(url + '\n')
        print(f"Saved response URLs to /tmp/fb_profile_urls.txt")
        
        profile = {
            "name": "",
            "bio": "",
            "profile_picture": "",
            "cover_photo": "",
            "friends_count": "",
            "followers_count": "",
            "location": "",
            "work": "",
            "education": "",
            "relationship": "",
            "joined": ""
        }
        
        # Extract from GraphQL data
        for data in profile_data:
            try:
                # Navigate through GraphQL response structure
                if isinstance(data, dict):
                    # Look for user/profile data in common GraphQL paths
                    if 'data' in data:
                        self._extract_from_graphql(data['data'], profile)
            except Exception as e:
                print(f"Error parsing GraphQL: {e}")
        
        # Fallback to HTML parsing if GraphQL didn't work
        if not profile["name"]:
            name_selectors = ['h1', 'h2']
            for selector in name_selectors:
                elem = await self.page.query_selector(selector)
                if elem:
                    text = await elem.inner_text()
                    if text and len(text) < 100:
                        profile["name"] = text.strip()
                        break
        
        return profile
    
    def _extract_from_graphql(self, data, profile):
        """Recursively extract profile info from GraphQL response"""
        if isinstance(data, dict):
            # Common GraphQL field names
            if 'name' in data and not profile["name"]:
                profile["name"] = str(data['name'])
            if 'profile_picture' in data and not profile["profile_picture"]:
                if isinstance(data['profile_picture'], dict) and 'uri' in data['profile_picture']:
                    profile["profile_picture"] = data['profile_picture']['uri']
            if 'bio' in data and not profile["bio"]:
                profile["bio"] = str(data['bio'])
            if 'current_city' in data and not profile["location"]:
                if isinstance(data['current_city'], dict) and 'name' in data['current_city']:
                    profile["location"] = data['current_city']['name']
            if 'work' in data and not profile["work"]:
                if isinstance(data['work'], list) and len(data['work']) > 0:
                    work_item = data['work'][0]
                    if isinstance(work_item, dict) and 'employer' in work_item:
                        if isinstance(work_item['employer'], dict) and 'name' in work_item['employer']:
                            profile["work"] = work_item['employer']['name']
            if 'education' in data and not profile["education"]:
                if isinstance(data['education'], list) and len(data['education']) > 0:
                    edu_item = data['education'][0]
                    if isinstance(edu_item, dict) and 'school' in edu_item:
                        if isinstance(edu_item['school'], dict) and 'name' in edu_item['school']:
                            profile["education"] = edu_item['school']['name']
            if 'friends' in data and not profile["friends_count"]:
                if isinstance(data['friends'], dict) and 'count' in data['friends']:
                    profile["friends_count"] = str(data['friends']['count'])
            if 'subscribers' in data and not profile["followers_count"]:
                if isinstance(data['subscribers'], dict) and 'count' in data['subscribers']:
                    profile["followers_count"] = str(data['subscribers']['count'])
            
            # Recurse into nested structures
            for value in data.values():
                if isinstance(value, (dict, list)):
                    self._extract_from_graphql(value, profile)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._extract_from_graphql(item, profile)
    
    async def search_people(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for people on Facebook"""
        try:
            await self.page.goto(f"https://www.facebook.com/search/people/?q={query}", timeout=10000)
        except Exception as e:
            print(f"Navigation error: {e}")
            return []
        
        await asyncio.sleep(5)
        
        # Save debug HTML
        try:
            html = await self.page.content()
            with open('/tmp/fb_search.html', 'w') as f:
                f.write(html)
            print(f"Saved search HTML to /tmp/fb_search.html")
        except:
            pass
        
        results = []
        
        # Try to find any divs with links that might be people
        links = await self.page.query_selector_all('a[href*="/profile.php"], a[href*="facebook.com/"][href*="?"][role="link"]')
        print(f"Found {len(links)} potential profile links")
        
        seen_names = set()
        for link in links[:limit * 2]:  # Get more than needed to filter
            try:
                # Get the link href
                href = await link.get_attribute("href")
                if not href or "facebook.com/search" in href or "facebook.com/hashtag" in href:
                    continue
                
                # Try to find name in the link or nearby
                name = ""
                # Try getting text from the link itself
                text = await link.inner_text()
                if text and len(text) > 0 and len(text) < 100:
                    name = text.strip()
                
                # Skip if no name or duplicate
                if not name or name in seen_names or len(name) < 2:
                    continue
                
                seen_names.add(name)
                
                # Extract ID from URL
                person_id = ""
                if "/profile.php?id=" in href:
                    person_id = href.split("id=")[1].split("&")[0]
                elif "facebook.com/" in href:
                    parts = href.split("facebook.com/")[1].split("?")[0].split("/")
                    person_id = parts[0] if parts else ""
                
                # Try to find profile picture nearby
                profile_pic = ""
                parent = await link.evaluate_handle('el => el.closest("div")')
                if parent:
                    img = await parent.query_selector('img')
                    if img:
                        src = await img.get_attribute("src")
                        if src:
                            profile_pic = src
                
                person_data = {
                    "id": person_id or name,
                    "name": name,
                    "profile_url": href if href.startswith("http") else f"https://www.facebook.com{href}",
                    "profile_picture": profile_pic,
                    "mutual_friends": 0,
                    "location": "",
                    "work": ""
                }
                
                results.append(person_data)
                
                if len(results) >= limit:
                    break
                    
            except Exception as e:
                print(f"Error extracting person: {e}")
                continue
        
        print(f"Returning {len(results)} results")
        return results[:limit]
    
    async def _extract_person_data(self, element) -> Dict:
        """Extract data from a search result"""
        person_data = {
            "id": "",
            "name": "",
            "profile_url": "",
            "profile_picture": "",
            "mutual_friends": 0,
            "location": "",
            "work": ""
        }
        
        # Extract name and profile URL
        name_selectors = ['a[role="link"] span', 'h2 a span', 'h3 a span', 'h4 a span']
        for selector in name_selectors:
            name_elem = await element.query_selector(selector)
            if name_elem:
                name = await name_elem.inner_text()
                if name and len(name) > 0:
                    person_data["name"] = name.strip()
                    # Find parent link
                    parent = await name_elem.evaluate_handle('el => el.closest("a")')
                    if parent:
                        href = await parent.get_property("href")
                        if href:
                            href_value = await href.json_value()
                            if href_value:
                                person_data["profile_url"] = href_value
                                # Extract ID from URL
                                if "/profile.php?id=" in href_value:
                                    person_data["id"] = href_value.split("id=")[1].split("&")[0]
                                elif "facebook.com/" in href_value:
                                    person_data["id"] = href_value.split("facebook.com/")[1].split("?")[0]
                    break
        
        # Extract profile picture
        img = await element.query_selector('img')
        if img:
            src = await img.get_attribute("src")
            if src:
                person_data["profile_picture"] = src
        
        # Extract additional info from text
        text = await element.inner_text()
        if "mutual friend" in text.lower():
            import re
            match = re.search(r'(\d+)\s+mutual friend', text)
            if match:
                person_data["mutual_friends"] = int(match.group(1))
        
        return person_data
