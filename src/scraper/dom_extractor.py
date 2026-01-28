"""DOM-based post extractor for Facebook"""
from typing import List, Dict
import hashlib

class DOMPostExtractor:
    @staticmethod
    async def extract_posts_from_articles(page, author: Dict, limit: int = 10) -> List[Dict]:
        """Extract posts from article elements
        
        On profile timelines, articles can be:
        1. Comments on posts (have comment_id in links)
        2. Actual posts (have /posts/ or /permalink/ links without comment_id)
        
        We extract both but mark them appropriately.
        """
        posts = []
        seen_content = set()
        
        articles = await page.query_selector_all('[role="article"]')
        
        for article in articles:
            try:
                # Check all links in the article
                links = await article.query_selector_all('a[href*="facebook.com"]')
                
                has_comment_id = False
                has_post_link = False
                
                for link in links:
                    href = await link.get_attribute('href')
                    if href:
                        if 'comment_id' in href:
                            has_comment_id = True
                        if '/posts/' in href or '/permalink/' in href:
                            has_post_link = True
                
                # Skip if it's only a comment (has comment_id but no post link)
                # Keep if it's a post (has post link) or unclear
                if has_comment_id and not has_post_link:
                    continue
                
                # Extract text content - try multiple selectors
                text = ""
                
                # Try data-ad-preview first
                text_elem = await article.query_selector('[data-ad-preview="message"]')
                if text_elem:
                    text = await text_elem.inner_text()
                
                # Try dir=auto elements (get longest one)
                if not text:
                    dir_elems = await article.query_selector_all('[dir="auto"]')
                    for elem in dir_elems:
                        t = await elem.inner_text()
                        if len(t) > len(text) and len(t) > 20:  # Get substantial text
                            text = t
                
                text = text.strip()
                
                if not text or text in seen_content or len(text) < 10:
                    continue
                
                seen_content.add(text)
                
                # Extract images
                images = []
                img_elems = await article.query_selector_all('img[src*="scontent"]')
                for img in img_elems[:3]:  # Max 3 images
                    src = await img.get_attribute('src')
                    if src and 'scontent' in src:
                        images.append(src)
                
                post_id = hashlib.md5(f"{author['name']}_{text}".encode()).hexdigest()
                
                posts.append({
                    'id': post_id,
                    'author': {'name': author['name'], 'profile_url': author.get('url', '')},
                    'content': text,
                    'timestamp': '',
                    'post_type': 'image' if images else 'text',
                    'is_sponsored': False,
                    'is_suggested': False,
                    'source_type': 'friend',
                    'engagement': {'likes': 0, 'comments': 0, 'shares': 0},
                    'media': {'images': images, 'videos': []}
                })
                
                if len(posts) >= limit:
                    break
            except Exception as e:
                continue
        
        return posts
