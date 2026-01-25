import asyncio
import random
from typing import List, Dict
from playwright.async_api import Page

class PostExtractor:
    def __init__(self, page: Page):
        self.page = page
        
    async def extract_posts(self, limit: int = 20) -> List[Dict]:
        """Extract posts from Facebook feed"""
        await self.page.goto("https://www.facebook.com/")
        await asyncio.sleep(3)
        
        posts = []
        scroll_attempts = 0
        max_scrolls = 10
        
        while len(posts) < limit and scroll_attempts < max_scrolls:
            # Scroll to load more posts
            await self.page.evaluate("window.scrollBy(0, window.innerHeight)")
            await asyncio.sleep(random.uniform(1.5, 3.0))
            
            # Extract post elements
            post_elements = await self.page.query_selector_all('[role="article"]')
            
            for element in post_elements[len(posts):]:
                if len(posts) >= limit:
                    break
                    
                try:
                    post_data = await self._extract_post_data(element)
                    if post_data:
                        posts.append(post_data)
                except Exception as e:
                    print(f"Error extracting post: {e}")
                    continue
            
            scroll_attempts += 1
        
        return posts[:limit]
    
    async def _extract_post_data(self, element) -> Dict:
        """Extract data from a single post element"""
        post_data = {
            "id": "",
            "author": {"name": "", "profile_url": ""},
            "content": "",
            "timestamp": "",
            "post_type": "text",
            "is_sponsored": False,
            "is_suggested": False,
            "engagement": {"likes": 0, "comments": 0, "shares": 0},
            "media": {"images": [], "videos": []}
        }
        
        # Extract author name
        author_elem = await element.query_selector('a[role="link"] strong, h2 a, h3 a, h4 a')
        if author_elem:
            post_data["author"]["name"] = await author_elem.inner_text()
            post_data["author"]["profile_url"] = await author_elem.get_attribute("href") or ""
        
        # Extract content
        content_elem = await element.query_selector('[data-ad-preview="message"], [data-ad-comet-preview="message"]')
        if content_elem:
            post_data["content"] = await content_elem.inner_text()
        
        # Check if sponsored
        sponsored_text = await element.inner_text()
        post_data["is_sponsored"] = "Sponsored" in sponsored_text
        post_data["is_suggested"] = "Suggested for you" in sponsored_text
        
        # Extract images
        images = await element.query_selector_all('img[src*="scontent"]')
        post_data["media"]["images"] = [await img.get_attribute("src") for img in images if await img.get_attribute("src")]
        
        # Determine post type
        if post_data["media"]["images"]:
            post_data["post_type"] = "photo"
        elif await element.query_selector('video'):
            post_data["post_type"] = "video"
        elif "http" in post_data["content"]:
            post_data["post_type"] = "link"
        
        # Generate simple ID
        post_data["id"] = f"{hash(post_data['author']['name'] + post_data['content'][:50])}"
        
        return post_data
