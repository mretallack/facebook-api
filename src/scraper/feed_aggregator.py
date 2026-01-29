"""Feed aggregator that scrapes posts from friends' profiles"""
import asyncio
import json
import logging
import re
from typing import List, Dict
from playwright.async_api import Page
from src.scraper.retry_decorator import retry_on_session_loss
from src.scraper.dom_extractor import DOMPostExtractor

logger = logging.getLogger(__name__)

class FeedAggregator:
    def __init__(self, page: Page, session_manager=None):
        self.page = page
        self.session_manager = session_manager
        self.post_urls = []  # Changed from set to list to preserve order
    
    @retry_on_session_loss(max_retries=2)
    async def get_feed(self, friends: List[Dict], following: List[Dict], limit: int = 20, include_own_profile: bool = True) -> List[Dict]:
        """Get posts by scraping each friend's profile"""
        all_posts = []
        
        logger.info(f"[FEED] Starting feed aggregation: {len(friends)} friends, limit={limit}")
        
        # First, scrape your own profile posts
        if include_own_profile:
            try:
                logger.info(f"[FEED] Scraping own profile...")
                own_posts = await self._scrape_own_profile(posts_limit=10)
                logger.info(f"[FEED] Got {len(own_posts)} posts from own profile")
                all_posts.extend(own_posts)
            except Exception as e:
                logger.error(f"[FEED] Error scraping own profile: {e}")
        
        # Scrape posts from each friend's profile
        for friend in friends[:2]:  # Limit to 2 friends max
            try:
                logger.info(f"[FEED] Scraping friend: {friend['name']}")
                posts = await self._scrape_friend_profile(friend, posts_per_friend=10)
                logger.info(f"[FEED] Got {len(posts)} posts from {friend['name']}")
                all_posts.extend(posts)
                if len(all_posts) >= limit:
                    break
            except Exception as e:
                logger.error(f"[FEED] Error scraping {friend['name']}: {e}")
                continue
        
        # Don't scrape following feed - only show friends' posts
        # following_posts = await self._scrape_following_feed(following, limit=10)
        # all_posts.extend(following_posts)
        
        # Sort by timestamp and deduplicate
        seen = set()
        unique_posts = []
        for post in all_posts:
            if post['content'] not in seen:
                seen.add(post['content'])
                unique_posts.append(post)
        
        unique_posts.sort(key=lambda p: p.get('timestamp', ''), reverse=True)
        return unique_posts[:limit]
    
    async def _handle_cookie_consent(self, page):
        """Handle cookie consent dialog if present"""
        try:
            await asyncio.sleep(1)
            
            # Look for elements with role="button" that contain "Allow all cookies"
            button_elements = await page.query_selector_all('[role="button"]')
            
            for elem in button_elements:
                try:
                    text = await elem.inner_text()
                    if "Allow all cookies" in text:
                        print("[DEBUG] Clicking cookie consent button")
                        await elem.click()
                        await asyncio.sleep(2)
                        return True
                except:
                    continue
        except:
            pass
        return False
    
    async def _scrape_own_profile(self, posts_limit: int) -> List[Dict]:
        """Scrape posts from your own profile using GraphQL interception"""
        author = {'name': 'Mark Retallack', 'url': 'https://www.facebook.com/me'}
        
        self.post_urls.clear()
        
        # Intercept GraphQL responses
        async def handle_response(response):
            if '/api/graphql/' in response.url and response.status == 200:
                try:
                    text = await response.text()
                    for line in text.split('\n'):
                        if line.strip():
                            data = json.loads(line)
                            self._extract_urls(data)
                except:
                    pass
        
        self.page.on('response', handle_response)
        
        await self.page.goto("https://www.facebook.com/me", wait_until='networkidle')
        await asyncio.sleep(3)
        
        # Scroll to trigger GraphQL requests
        for _ in range(5):
            await self.page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
            await asyncio.sleep(2)
        
        # Remove handler before fetching posts
        self.page.remove_listener('response', handle_response)
        
        # Fetch posts from collected URLs
        posts = []
        for url in list(self.post_urls)[:posts_limit]:
            try:
                logger.info(f"[DEBUG] Fetching post: {url}")
                content = await self._fetch_post(url)
                if content and content.get('text'):
                    posts.append({
                        'id': url,  # Use URL as ID
                        'author': {'name': author['name'], 'profile_url': author['url']},
                        'content': content['text'],
                        'url': url,
                        'timestamp': '',
                        'image_url': content.get('image')
                    })
                    logger.info(f"[DEBUG] ✓ Fetched post successfully")
            except Exception as e:
                logger.warning(f"Skipping post {url}: {e}")
                continue
        
        logger.info(f"[DEBUG] Scraped own profile: {len(posts)} posts")
        return posts
    
    async def _scrape_friend_profile(self, friend: Dict, posts_per_friend: int) -> List[Dict]:
        """Scrape posts from a single friend's profile using GraphQL interception"""
        logger.info(f"[DEBUG] Scraping profile: {friend['name']} at {friend['url']}")
        
        self.post_urls.clear()
        
        # Intercept GraphQL responses
        async def handle_response(response):
            if '/api/graphql/' in response.url and response.status == 200:
                try:
                    text = await response.text()
                    for line in text.split('\n'):
                        if line.strip():
                            data = json.loads(line)
                            self._extract_urls(data)
                except:
                    pass
        
        self.page.on('response', handle_response)
        
        await self.page.goto(friend['url'], wait_until='networkidle')
        await asyncio.sleep(3)
        
        # FIRST: Extract posts from initial DOM
        dom_links = await self.page.query_selector_all('a[href*="/posts/"], a[href*="/photo/"]')
        for link in dom_links:
            href = await link.get_attribute('href')
            if href:
                # Make absolute URL
                if href.startswith('/'):
                    href = f"https://www.facebook.com{href}"
                # Apply same filters
                if 'comment_id=' not in href and 'reply_comment_id=' not in href:
                    if 'set=gm.' not in href:
                        if '/posts/' in href or ('/photo/' in href and 'set=a.' in href):
                            if href not in self.post_urls:
                                self.post_urls.append(href)
        
        # SECOND: Scroll to trigger GraphQL requests for older posts
        for _ in range(15):  # Increased from 10 to 15 for more posts
            await self.page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
            await asyncio.sleep(2)
        
        # Remove handler before fetching posts
        self.page.remove_listener('response', handle_response)
        
        # Fetch posts from collected URLs (limit to 6 per friend)
        posts = []
        unique_urls = []
        for url in self.post_urls:
            if url not in unique_urls:
                unique_urls.append(url)
        
        # Filter to only photo posts
        photo_urls = [url for url in unique_urls if '/photo/' in url]
        
        for url in photo_urls[:6]:  # Limit to 6 photos
            try:
                logger.info(f"[DEBUG] Fetching post: {url}")
                content = await self._fetch_post(url)
                if content and content.get('text'):
                    posts.append({
                        'id': url,  # Use URL as ID
                        'author': {'name': friend['name'], 'profile_url': friend['url']},
                        'content': content['text'],
                        'url': url,
                        'timestamp': content.get('timestamp', ''),
                        'image_url': content.get('image')
                    })
                    logger.info(f"[DEBUG] ✓ Fetched post successfully")
            except Exception as e:
                logger.warning(f"Skipping post {url}: {e}")
                continue
        
        logger.info(f"[DEBUG] Finished scraping {friend['name']}: {len(posts)} posts")
        return posts
    
    def _extract_urls(self, data):
        """Extract post URLs from GraphQL response"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ['permalink_url', 'wwwURL', 'url'] and isinstance(value, str):
                    # Skip comment URLs
                    if 'comment_id=' in value or 'reply_comment_id=' in value:
                        continue
                    # Skip group posts (contain set=gm.)
                    if 'set=gm.' in value:
                        continue
                    # Only include profile posts and photos
                    if '/posts/' in value or ('/photo/' in value and 'set=a.' in value):
                        if value not in self.post_urls:  # Avoid duplicates while preserving order
                            self.post_urls.append(value)
                elif isinstance(value, (dict, list)):
                    self._extract_urls(value)
        elif isinstance(data, list):
            for item in data:
                self._extract_urls(item)
    
    async def _fetch_post(self, url):
        """Fetch content from a single post"""
        try:
            await self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(2)
            
            # Try to extract timestamp
            timestamp = ""
            try:
                # Look for timestamp - try multiple selectors
                time_elem = await self.page.query_selector('abbr[data-utime], abbr[data-shorten], span[id*="jsc"] abbr')
                if not time_elem:
                    # Try finding any abbr near the post
                    time_elem = await self.page.query_selector('abbr')
                
                if time_elem:
                    # Try data-utime attribute first (Unix timestamp)
                    utime = await time_elem.get_attribute('data-utime')
                    if utime:
                        from datetime import datetime
                        timestamp = datetime.fromtimestamp(int(utime)).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        # Try title or text
                        timestamp = await time_elem.get_attribute('title') or await time_elem.inner_text()
            except:
                pass
            
            if '/photo/' in url:
                text = await self.page.get_attribute('meta[name="description"]', 'content') or ""
                main = await self.page.query_selector('[role="main"]')
                img = await main.query_selector('img[src*="scontent"]') if main else None
                image_url = await img.get_attribute('src') if img else None
                return {'text': text, 'image': image_url, 'timestamp': timestamp}
            else:
                # Text post - try multiple methods
                article = await self.page.query_selector('[role="article"]')
                if not article:
                    return None
                
                # Try specific text elements first
                text_elems = await article.query_selector_all('[dir="auto"]')
                texts = []
                for elem in text_elems[:3]:
                    t = await elem.inner_text()
                    if t.strip() and len(t.strip()) > 5:
                        texts.append(t.strip())
                
                # If no text found, get all article text
                if not texts:
                    all_text = await article.inner_text()
                    lines = [l.strip() for l in all_text.split('\n') if l.strip() and len(l.strip()) > 10]
                    # Skip common UI elements
                    filtered = [l for l in lines if not any(skip in l.lower() for skip in ['like', 'comment', 'share', 'send', 'more'])]
                    texts = filtered[:3]
                
                return {'text': '\n'.join(texts) if texts else "", 'timestamp': timestamp}
        except Exception as e:
            logger.warning(f"Fetch error for {url}: {e}")
            return None
    
    async def _scrape_following_feed(self, following: List[Dict], limit: int) -> List[Dict]:
        """Scrape following posts from main feed"""
        await self.page.goto("https://www.facebook.com/", wait_until='networkidle')
        await asyncio.sleep(2)
        
        # Scroll to load more posts
        for _ in range(3):
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1)
        
        scripts = await self.page.query_selector_all('script[type="application/json"]')
        posts = []
        following_map = {f['name'].lower(): f for f in following}
        
        for script in scripts:
            try:
                content = await script.inner_text()
                data = json.loads(content)
                extracted = self._extract_following_posts(data, following_map)
                posts.extend(extracted)
                if len(posts) >= limit:
                    break
            except:
                continue
        
        return posts[:limit]
    
    def _extract_images_from_object(self, obj, images=None, depth=0) -> List[str]:
        """Recursively extract all image URLs from any object"""
        if images is None:
            images = []
        
        if depth > 20:  # Prevent infinite recursion
            return images
        
        if isinstance(obj, dict):
            # Check for direct image URL fields
            for key in ['uri', 'src', 'url', 'image', 'photo']:
                if key in obj and isinstance(obj[key], str):
                    url = obj[key]
                    if ('fbcdn.net' in url or 'facebook.com' in url) and url.startswith('http'):
                        if url not in images:
                            images.append(url)
            
            # Recurse into all values
            for value in obj.values():
                if isinstance(value, (dict, list)):
                    self._extract_images_from_object(value, images, depth + 1)
        
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    self._extract_images_from_object(item, images, depth + 1)
        
        return images
        """Extract posts from JSON and assign to author"""
        if posts is None:
            posts = []
        
        if isinstance(obj, dict):
            if 'story' in obj and isinstance(obj.get('story'), dict):
                story = obj['story']
                
                # Extract text from message
                text = ''
                if 'message' in story and isinstance(story['message'], dict):
                    text = story['message'].get('text', '').strip()
                
                # Also check for comet_sections which might have the message
                if not text and 'comet_sections' in story:
                    sections = story['comet_sections']
                    if isinstance(sections, dict):
                        # Look for message in various sections
                        for section_key, section_val in sections.items():
                            if isinstance(section_val, dict):
                                if 'story' in section_val:
                                    sub_story = section_val['story']
                                    if isinstance(sub_story, dict) and 'message' in sub_story:
                                        msg = sub_story['message']
                                        if isinstance(msg, dict):
                                            text = msg.get('text', '').strip()
                                            if text:
                                                break
                
                # If we have text or this is a photo post, include it
                if text or 'attachments' in story:
                    # Extract images - try multiple strategies
                    images = []
                    
                    # Strategy 1: Look in attachments
                    if 'attachments' in story:
                        attachments = story['attachments']
                        if isinstance(attachments, list):
                            for att in attachments:
                                if isinstance(att, dict):
                                    # Look for image in styles.attachment.media.photo_image.uri
                                    if 'styles' in att:
                                        styles = att['styles']
                                        if isinstance(styles, dict) and 'attachment' in styles:
                                            att_data = styles['attachment']
                                            if isinstance(att_data, dict) and 'media' in att_data:
                                                media = att_data['media']
                                                if isinstance(media, dict) and 'photo_image' in media:
                                                    photo_img = media['photo_image']
                                                    if isinstance(photo_img, dict) and 'uri' in photo_img:
                                                        images.append(photo_img['uri'])
                                    
                                    # Strategy 2: Recursively search the entire attachment for image URLs
                                    att_images = self._extract_images_from_object(att)
                                    images.extend([img for img in att_images if img not in images])
                    
                    # Strategy 3: Search the entire story object for images
                    if not images:
                        story_images = self._extract_images_from_object(story)
                        images.extend([img for img in story_images if img not in images])
                    
                    if not text:
                        text = '[Photo post]'
                    
                    # Generate unique ID for photo posts without IDs
                    post_id = story.get('id', '')
                    if not post_id or text == '[Photo post]':
                        import hashlib
                        post_id = hashlib.md5(f"{author['name']}_{text}_{story.get('created_time', '')}".encode()).hexdigest()
                    
                    posts.append({
                        'id': post_id,
                        'author': {'name': author['name'], 'profile_url': author['url']},
                        'content': text,
                        'timestamp': story.get('created_time', ''),
                        'post_type': 'text',
                        'is_sponsored': False,
                        'is_suggested': False,
                        'source_type': source_type,
                        'engagement': {'likes': 0, 'comments': 0, 'shares': 0},
                        'media': {'images': images, 'videos': []}
                    })
            
            for value in obj.values():
                if isinstance(value, (dict, list)):
                    self._extract_posts_from_json(value, author, source_type, posts)
        
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    self._extract_posts_from_json(item, author, source_type, posts)
        
        return posts
    
    def _extract_following_posts(self, obj, following_map: Dict, posts=None) -> List[Dict]:
        """Extract posts from following accounts"""
        if posts is None:
            posts = []
        
        if isinstance(obj, dict):
            if 'story' in obj and isinstance(obj.get('story'), dict):
                story = obj['story']
                
                # Extract text from message
                text = ''
                if 'message' in story and isinstance(story['message'], dict):
                    text = story['message'].get('text', '').strip()
                
                # Extract author
                author_name = ''
                author_url = ''
                
                if 'actors' in story and isinstance(story['actors'], list) and story['actors']:
                    actor = story['actors'][0]
                    if isinstance(actor, dict):
                        author_name = actor.get('name', '')
                        author_url = actor.get('url', '')
                
                # Extract images from attachments
                images = []
                if 'attachments' in story:
                    attachments = story['attachments']
                    if isinstance(attachments, list):
                        for att in attachments:
                            if isinstance(att, dict):
                                # Look for image in styles.attachment.media.photo_image.uri
                                if 'styles' in att:
                                    styles = att['styles']
                                    if isinstance(styles, dict) and 'attachment' in styles:
                                        att_data = styles['attachment']
                                        if isinstance(att_data, dict) and 'media' in att_data:
                                            media = att_data['media']
                                            if isinstance(media, dict) and 'photo_image' in media:
                                                photo_img = media['photo_image']
                                                if isinstance(photo_img, dict) and 'uri' in photo_img:
                                                    images.append(photo_img['uri'])
                                
                                # Recursively search the entire attachment for image URLs
                                att_images = self._extract_images_from_object(att)
                                images.extend([img for img in att_images if img not in images])
                
                # Search the entire story object for images if none found
                if not images:
                    story_images = self._extract_images_from_object(story)
                    images.extend([img for img in story_images if img not in images])
                
                # If we have text or images, include the post
                if (text or images) and author_name:
                    if not text:
                        text = '[Photo post]'
                    
                    # Check if author is in following or unknown (treat unknown as following)
                    author_lower = author_name.lower()
                    if author_lower not in following_map:
                        # Generate unique ID for photo posts without IDs
                        post_id = story.get('id', '')
                        if not post_id or text == '[Photo post]':
                            import hashlib
                            post_id = hashlib.md5(f"{author_name}_{text}_{story.get('created_time', '')}".encode()).hexdigest()
                        
                        posts.append({
                            'id': post_id,
                            'author': {'name': author_name, 'profile_url': author_url},
                            'content': text,
                            'timestamp': story.get('created_time', ''),
                            'post_type': 'text',
                            'is_sponsored': False,
                            'is_suggested': False,
                            'source_type': 'following',
                            'engagement': {'likes': 0, 'comments': 0, 'shares': 0},
                            'media': {'images': images, 'videos': []}
                        })
            
            for value in obj.values():
                if isinstance(value, (dict, list)):
                    self._extract_following_posts(value, following_map, posts)
        
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    self._extract_following_posts(item, following_map, posts)
        
        return posts
