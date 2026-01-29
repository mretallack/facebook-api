import asyncio
from datetime import datetime, timedelta

class SessionKeeper:
    def __init__(self, session_manager, interval_minutes=5):
        self.session_manager = session_manager
        self.interval = interval_minutes * 60
        self.task = None
        self.running = False
        
    async def keep_alive(self):
        """Periodically check and refresh session"""
        while self.running:
            try:
                if not await self.session_manager.is_logged_in():
                    print(f"[{datetime.now()}] Session expired, re-authenticating...")
                    await self.session_manager.login()
                else:
                    # Just check cookies, don't navigate (prevents context destruction)
                    print(f"[{datetime.now()}] Session active")
            except Exception as e:
                print(f"[{datetime.now()}] Session keep-alive error: {e}")
            
            await asyncio.sleep(self.interval)
    
    def start(self):
        """Start keep-alive task"""
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self.keep_alive())
    
    def stop(self):
        """Stop keep-alive task"""
        self.running = False
        if self.task:
            self.task.cancel()
