import asyncio
import json
from typing import List, Dict
from playwright.async_api import Page

class PostExtractor:
    def __init__(self, page: Page):
        self.page = page
        
    async def extract_posts(self, limit: int = 20) -> List[Dict]:
        """Extract posts from Facebook feed by parsing JSON data"""
        await self.page.goto("https://www.facebook.com/", wait_until='networkidle')
        await asyncio.sleep(3)
        
        # Extract JSON from script tags
        scripts = await self.page.query_selector_all('script[type="application/json"]')
        posts = []
        
        for script in scripts:
            try:
                content = await script.inner_text()
                data = json.loads(content)
                posts.extend(self._extract_stories(data))
                if len(posts) >= limit:
                    break
            except:
                continue
        
        return posts[:limit]
    
    def _extract_stories(self, obj, posts=None):
        """Recursively find story objects with message text"""
        if posts is None:
            posts = []
        
        if isinstance(obj, dict):
            if 'story' in obj and isinstance(obj.get('story'), dict):
                story = obj['story']
                if 'message' in story and isinstance(story['message'], dict):
                    text = story['message'].get('text', '').strip()
                    if text and not any(p['content'] == text for p in posts):
                        posts.append({
                            'id': story.get('id', ''),
                            'author': {'name': '', 'profile_url': ''},
                            'content': text,
                            'timestamp': '',
                            'post_type': 'text',
                            'is_sponsored': False,
                            'is_suggested': False,
                            'engagement': {'likes': 0, 'comments': 0, 'shares': 0},
                            'media': {'images': [], 'videos': []}
                        })
            
            for value in obj.values():
                self._extract_stories(value, posts)
        
        elif isinstance(obj, list):
            for item in obj:
                self._extract_stories(item, posts)
        
        return posts
