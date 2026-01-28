import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config.settings import settings
from src.cache.refresh_tasks import RefreshTasks

logger = logging.getLogger(__name__)

class CacheScheduler:
    def __init__(self, refresh_tasks: RefreshTasks):
        self.scheduler = AsyncIOScheduler()
        self.refresh_tasks = refresh_tasks
        self.running = False
    
    def start(self):
        """Start the scheduler"""
        if not settings.CACHE_ENABLED:
            logger.info("Cache disabled, scheduler not started")
            return
        
        logger.info("Starting cache scheduler...")
        
        # Schedule refresh tasks with datetime objects
        now = datetime.now()
        
        self.scheduler.add_job(
            self.refresh_tasks.refresh_posts,
            'interval',
            minutes=settings.CACHE_REFRESH_POSTS,
            id='refresh_posts',
            next_run_time=now + timedelta(seconds=10)
        )
        
        self.scheduler.add_job(
            self.refresh_tasks.refresh_friends,
            'interval',
            minutes=settings.CACHE_REFRESH_FRIENDS,
            id='refresh_friends',
            next_run_time=now + timedelta(seconds=30)
        )
        
        self.scheduler.add_job(
            self.refresh_tasks.refresh_profile,
            'interval',
            minutes=settings.CACHE_REFRESH_PROFILE,
            id='refresh_profile',
            next_run_time=now + timedelta(seconds=50)
        )
        
        self.scheduler.add_job(
            self.refresh_tasks.refresh_friend_requests,
            'interval',
            minutes=settings.CACHE_REFRESH_REQUESTS,
            id='refresh_requests',
            next_run_time=now + timedelta(seconds=70)
        )
        
        self.scheduler.start()
        self.running = True
        logger.info("Cache scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.running:
            logger.info("Stopping cache scheduler...")
            self.scheduler.shutdown()
            self.running = False
            logger.info("Cache scheduler stopped")
