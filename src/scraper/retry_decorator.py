from functools import wraps
import asyncio

def retry_on_session_loss(max_retries=2):
    """Decorator to retry scraping operations if session is lost"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    error_msg = str(e).lower()
                    # Check if error indicates session loss
                    if any(x in error_msg for x in ['login', 'session', 'cookie', 'unauthorized']):
                        if attempt < max_retries:
                            print(f"Session lost, retrying ({attempt + 1}/{max_retries})...")
                            # Try to re-authenticate
                            if hasattr(self, 'session_manager'):
                                await self.session_manager.login()
                            await asyncio.sleep(2)
                            continue
                    raise
            return None
        return wrapper
    return decorator
