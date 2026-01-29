import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from config.settings import settings
from src.cache.cache_service import CacheService

logger = logging.getLogger(__name__)

class RefreshTasks:
    def __init__(self, cache_service: CacheService, session_manager, services: dict):
        self.cache = cache_service
        self.session_manager = session_manager
        self.services = services
        self.last_scrape_time: Optional[datetime] = None
        self.scrape_lock = asyncio.Lock()
    
    async def _can_scrape(self) -> bool:
        """Check if enough time has passed since last scrape"""
        if self.last_scrape_time is None:
            return True
        
        elapsed = (datetime.utcnow() - self.last_scrape_time).total_seconds()
        return elapsed >= settings.CACHE_MIN_SCRAPE_INTERVAL
    
    async def _wait_for_rate_limit(self):
        """Wait until rate limit allows scraping"""
        while not await self._can_scrape():
            wait_time = settings.CACHE_MIN_SCRAPE_INTERVAL - (datetime.utcnow() - self.last_scrape_time).total_seconds()
            if wait_time > 0:
                logger.info(f"Rate limit: waiting {wait_time:.0f}s before next scrape")
                await asyncio.sleep(wait_time)
    
    async def refresh_posts(self):
        """Refresh posts cache by aggregating from news feed"""
        async with self.scrape_lock:
            try:
                meta = self.cache.get_metadata('posts')
                if meta and meta['error_count'] >= settings.CACHE_MAX_ERROR_COUNT:
                    logger.warning(f"Skipping posts refresh due to {meta['error_count']} consecutive errors")
                    return
                
                await self._wait_for_rate_limit()
                
                logger.info("Refreshing posts cache from news feed...")
                
                # Hardcode friends for now since friends scraper is broken
                friends = [{'name': 'Mark Retallack', 'url': 'https://www.facebook.com/mark.retallack'}]
                logger.info(f"Using {len(friends)} hardcoded friends for feed aggregation")
                
                # Get following list (TODO: implement following scraper)
                following = []  # Empty for now
                
                # Use FeedAggregator to scrape news feed
                from src.scraper.feed_aggregator import FeedAggregator
                aggregator = FeedAggregator(self.session_manager.page)
                posts = await aggregator.get_feed(friends, following, limit=10, include_own_profile=False)
                
                # Pre-fetch and cache images
                from src.api.routes.media import fetch_and_cache_image
                for post in posts:
                    if post.get('media', {}).get('images'):
                        for img_url in post['media']['images']:
                            try:
                                await fetch_and_cache_image(img_url)
                            except:
                                pass
                
                if posts:
                    self.cache.set_posts(posts, settings.CACHE_EXPIRY_POSTS)
                    self.last_scrape_time = datetime.utcnow()
                    
                    next_fetch = datetime.utcnow() + timedelta(minutes=settings.CACHE_REFRESH_POSTS)
                    self.cache.update_metadata('posts', True, next_fetch)
                    logger.info(f"Cached {len(posts)} posts from news feed")
                else:
                    raise Exception("No posts returned from news feed")
                    
            except Exception as e:
                logger.error(f"Error refreshing posts: {e}")
                next_fetch = datetime.utcnow() + timedelta(minutes=settings.CACHE_REFRESH_POSTS * 2)
                self.cache.update_metadata('posts', False, next_fetch)
    
    async def refresh_friends(self):
        """Refresh friends cache"""
        async with self.scrape_lock:
            try:
                meta = self.cache.get_metadata('friends')
                if meta and meta['error_count'] >= settings.CACHE_MAX_ERROR_COUNT:
                    logger.warning(f"Skipping friends refresh due to {meta['error_count']} consecutive errors")
                    return
                
                await self._wait_for_rate_limit()
                
                logger.info("Refreshing friends cache...")
                friends_service = self.services.get('friends')
                if not friends_service:
                    logger.error("Friends service not available")
                    return
                
                result = await friends_service.get_friends_list(limit=50)
                if result['success']:
                    friends = result['data']
                    self.cache.set_friends(friends, settings.CACHE_EXPIRY_FRIENDS)
                    self.last_scrape_time = datetime.utcnow()
                    
                    next_fetch = datetime.utcnow() + timedelta(minutes=settings.CACHE_REFRESH_FRIENDS)
                    self.cache.update_metadata('friends', True, next_fetch)
                    logger.info(f"Cached {len(friends)} friends")
                else:
                    raise Exception(result.get('error', 'Unknown error'))
                    
            except Exception as e:
                logger.error(f"Error refreshing friends: {e}")
                next_fetch = datetime.utcnow() + timedelta(minutes=settings.CACHE_REFRESH_FRIENDS * 2)
                self.cache.update_metadata('friends', False, next_fetch)
    
    async def refresh_profile(self):
        """Refresh profile cache"""
        async with self.scrape_lock:
            try:
                meta = self.cache.get_metadata('profile')
                if meta and meta['error_count'] >= settings.CACHE_MAX_ERROR_COUNT:
                    logger.warning(f"Skipping profile refresh due to {meta['error_count']} consecutive errors")
                    return
                
                await self._wait_for_rate_limit()
                
                logger.info("Refreshing profile cache...")
                profile_service = self.services.get('profile')
                if not profile_service:
                    logger.error("Profile service not available")
                    return
                
                result = await profile_service.get_profile()
                if result['success']:
                    profile = result['data']
                    self.cache.set_profile(profile, settings.CACHE_EXPIRY_PROFILE)
                    self.last_scrape_time = datetime.utcnow()
                    
                    next_fetch = datetime.utcnow() + timedelta(minutes=settings.CACHE_REFRESH_PROFILE)
                    self.cache.update_metadata('profile', True, next_fetch)
                    logger.info("Cached profile")
                else:
                    raise Exception(result.get('error', 'Unknown error'))
                    
            except Exception as e:
                logger.error(f"Error refreshing profile: {e}")
                next_fetch = datetime.utcnow() + timedelta(minutes=settings.CACHE_REFRESH_PROFILE * 2)
                self.cache.update_metadata('profile', False, next_fetch)
    
    async def refresh_friend_requests(self):
        """Refresh friend requests cache"""
        async with self.scrape_lock:
            try:
                meta = self.cache.get_metadata('requests')
                if meta and meta['error_count'] >= settings.CACHE_MAX_ERROR_COUNT:
                    logger.warning(f"Skipping requests refresh due to {meta['error_count']} consecutive errors")
                    return
                
                await self._wait_for_rate_limit()
                
                logger.info("Refreshing friend requests cache...")
                friends_service = self.services.get('friends')
                if not friends_service:
                    logger.error("Friends service not available")
                    return
                
                result = await friends_service.get_friend_requests()
                if result['success']:
                    requests = result['data']
                    self.cache.set_friend_requests(requests, settings.CACHE_EXPIRY_REQUESTS)
                    self.last_scrape_time = datetime.utcnow()
                    
                    next_fetch = datetime.utcnow() + timedelta(minutes=settings.CACHE_REFRESH_REQUESTS)
                    self.cache.update_metadata('requests', True, next_fetch)
                    logger.info(f"Cached {len(requests)} friend requests")
                else:
                    raise Exception(result.get('error', 'Unknown error'))
                    
            except Exception as e:
                logger.error(f"Error refreshing friend requests: {e}")
                next_fetch = datetime.utcnow() + timedelta(minutes=settings.CACHE_REFRESH_REQUESTS * 2)
                self.cache.update_metadata('requests', False, next_fetch)
