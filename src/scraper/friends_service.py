"""
Friends service for managing Facebook friend operations.
"""
from typing import Dict, List, Optional
from .action_handler import ActionHandler
import logging

logger = logging.getLogger(__name__)


class FriendsService(ActionHandler):
    """Service for Facebook friends management."""
    
    async def search_friends(self, query: str, limit: int = 20) -> Dict:
        """Search for people by name."""
        async def _search():
            await self.safe_navigate(f'https://www.facebook.com/search/people/?q={query}')
            
            results = []
            for _ in range(limit // 10):
                people = await self.page.evaluate("""
                    () => {
                        const cards = document.querySelectorAll('[role="article"], [data-testid="search_result"]');
                        return Array.from(cards).slice(0, 10).map(card => {
                            const name = card.querySelector('a[role="link"] span')?.textContent;
                            const link = card.querySelector('a[role="link"]')?.href;
                            const mutual = card.textContent.match(/(\d+) mutual friend/)?.[1] || '0';
                            return name && link ? {name, url: link, mutual_friends: parseInt(mutual)} : null;
                        }).filter(p => p);
                    }
                """)
                results.extend(people)
                
                if len(results) >= limit:
                    break
                    
                await self.scroll_slowly(300)
                await self.page.wait_for_timeout(1000)
            
            return results[:limit]
        
        return await self.execute('friend_search', _search)
    
    async def send_friend_request(self, profile_url: str) -> Dict:
        """Send friend request to a user."""
        async def _send_request():
            await self.safe_navigate(profile_url)
            
            # Find add friend button
            add_btn = await self.selector_manager.find_element(self.page, 'friend_request_button')
            if not add_btn:
                raise Exception("Add friend button not found")
            
            await self.human_click(add_btn)
            await self.page.wait_for_timeout(1000)
            
            return {'sent': True, 'profile_url': profile_url}
        
        return await self.execute('friend_request', _send_request, account_age_days=None)
    
    async def accept_friend_request(self, request_id: str) -> Dict:
        """Accept a friend request."""
        async def _accept():
            await self.safe_navigate('https://www.facebook.com/friends/requests')
            
            # Find confirm button for this request
            confirm_btn = await self.page.query_selector(f'[data-id="{request_id}"] [aria-label="Confirm"]')
            if not confirm_btn:
                # Try alternative selector
                confirm_btn = await self.page.query_selector('[aria-label="Confirm"]')
            
            if not confirm_btn:
                raise Exception("Confirm button not found")
            
            await self.human_click(confirm_btn)
            await self.page.wait_for_timeout(1000)
            
            return {'accepted': True, 'request_id': request_id}
        
        return await self.execute('friend_accept', _accept)
    
    async def reject_friend_request(self, request_id: str) -> Dict:
        """Reject a friend request."""
        async def _reject():
            await self.safe_navigate('https://www.facebook.com/friends/requests')
            
            # Find delete button
            delete_btn = await self.page.query_selector(f'[data-id="{request_id}"] [aria-label="Delete"]')
            if not delete_btn:
                delete_btn = await self.page.query_selector('[aria-label="Delete"]')
            
            if not delete_btn:
                raise Exception("Delete button not found")
            
            await self.human_click(delete_btn)
            await self.page.wait_for_timeout(1000)
            
            return {'rejected': True, 'request_id': request_id}
        
        return await self.execute('friend_reject', _reject)
    
    async def get_friend_requests(self) -> Dict:
        """Get pending friend requests."""
        async def _get_requests():
            await self.safe_navigate('https://www.facebook.com/friends/requests')
            
            requests = await self.page.evaluate("""
                () => {
                    const cards = document.querySelectorAll('[role="article"]');
                    return Array.from(cards).map(card => {
                        const name = card.querySelector('a[role="link"] span')?.textContent;
                        const link = card.querySelector('a[role="link"]')?.href;
                        const mutual = card.textContent.match(/(\d+) mutual friend/)?.[1] || '0';
                        const id = link?.split('/').pop();
                        return name && link ? {
                            id,
                            name,
                            url: link,
                            mutual_friends: parseInt(mutual)
                        } : null;
                    }).filter(r => r);
                }
            """)
            
            return requests
        
        return await self.execute('friend_requests_list', _get_requests)
    
    async def unfriend(self, profile_url: str) -> Dict:
        """Remove a friend."""
        async def _unfriend():
            await self.safe_navigate(profile_url)
            
            # Click friends button to open menu
            friends_btn = await self.page.query_selector('[aria-label="Friends"]')
            if not friends_btn:
                raise Exception("Friends button not found")
            
            await self.human_click(friends_btn)
            await self.page.wait_for_timeout(500)
            
            # Click unfriend
            unfriend_btn = await self.page.query_selector('[role="menuitem"]:has-text("Unfriend")')
            if not unfriend_btn:
                unfriend_btn = await self.page.query_selector('text=Unfriend')
            
            if not unfriend_btn:
                raise Exception("Unfriend option not found")
            
            await self.human_click(unfriend_btn)
            await self.page.wait_for_timeout(1000)
            
            return {'unfriended': True, 'profile_url': profile_url}
        
        return await self.execute('unfriend', _unfriend)
    
    async def block_user(self, profile_url: str) -> Dict:
        """Block a user."""
        async def _block():
            await self.safe_navigate(profile_url)
            
            # Click more options (three dots)
            more_btn = await self.page.query_selector('[aria-label="More"]')
            if not more_btn:
                raise Exception("More options button not found")
            
            await self.human_click(more_btn)
            await self.page.wait_for_timeout(500)
            
            # Click block
            block_btn = await self.page.query_selector('[role="menuitem"]:has-text("Block")')
            if not block_btn:
                block_btn = await self.page.query_selector('text=Block')
            
            if not block_btn:
                raise Exception("Block option not found")
            
            await self.human_click(block_btn)
            await self.page.wait_for_timeout(500)
            
            # Confirm block
            confirm_btn = await self.page.query_selector('[aria-label="Confirm"]')
            if confirm_btn:
                await self.human_click(confirm_btn)
            
            await self.page.wait_for_timeout(1000)
            
            return {'blocked': True, 'profile_url': profile_url}
        
        return await self.execute('block_user', _block)
    
    async def get_friends_list(self, limit: int = 50) -> Dict:
        """Get list of friends."""
        async def _get_friends():
            await self.safe_navigate('https://www.facebook.com/me/friends')
            
            friends = []
            for _ in range(limit // 20):
                batch = await self.page.evaluate("""
                    () => {
                        const cards = document.querySelectorAll('[data-testid="friend_list_item"], a[href*="/friends"]');
                        return Array.from(cards).slice(0, 20).map(card => {
                            const name = card.querySelector('span')?.textContent;
                            const link = card.href || card.querySelector('a')?.href;
                            return name && link ? {name, url: link} : null;
                        }).filter(f => f);
                    }
                """)
                friends.extend(batch)
                
                if len(friends) >= limit:
                    break
                
                await self.scroll_slowly(300)
                await self.page.wait_for_timeout(1000)
            
            return friends[:limit]
        
        return await self.execute('friends_list', _get_friends)
