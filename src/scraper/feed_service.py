import json
import re
from playwright.sync_api import Page

def extract_feed_posts(page: Page, limit: int = 10) -> list:
    """Extract posts from news feed by parsing JSON data in script tags"""
    
    # Get all script tags with JSON data
    scripts = page.locator('script[type="application/json"]').all()
    
    posts = []
    for script in scripts:
        try:
            content = script.inner_text()
            data = json.loads(content)
            
            # Recursively search for story objects with message text
            posts.extend(_extract_stories(data))
            
            if len(posts) >= limit:
                break
        except:
            continue
    
    return posts[:limit]

def _extract_stories(obj, posts=None):
    """Recursively find story objects with message text"""
    if posts is None:
        posts = []
    
    if isinstance(obj, dict):
        # Check if this is a story with message
        if 'story' in obj and isinstance(obj.get('story'), dict):
            story = obj['story']
            if 'message' in story and isinstance(story['message'], dict):
                text = story['message'].get('text', '').strip()
                if text:
                    posts.append({'text': text})
        
        # Recurse into dict values
        for value in obj.values():
            _extract_stories(value, posts)
    
    elif isinstance(obj, list):
        # Recurse into list items
        for item in obj:
            _extract_stories(item, posts)
    
    return posts
