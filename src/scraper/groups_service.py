"""
Groups service for managing Facebook group operations.
"""
from typing import Dict, List, Optional
from .action_handler import ActionHandler
import logging

logger = logging.getLogger(__name__)


class GroupsService(ActionHandler):
    """Service for Facebook groups management."""
    
    async def search_groups(self, query: str, limit: int = 20) -> Dict:
        """Search for groups."""
        async def _search():
            await self.safe_navigate(f'https://www.facebook.com/search/groups/?q={query}')
            
            results = []
            for _ in range(limit // 10):
                groups = await self.page.evaluate("""
                    () => {
                        const cards = document.querySelectorAll('[role="article"]');
                        return Array.from(cards).slice(0, 10).map(card => {
                            const name = card.querySelector('a[role="link"] span')?.textContent;
                            const link = card.querySelector('a[role="link"]')?.href;
                            const members = card.textContent.match(/([\\d,]+) members?/)?.[1];
                            const privacy = card.textContent.includes('Private') ? 'private' : 'public';
                            return name && link ? {
                                name,
                                url: link,
                                members: members ? parseInt(members.replace(/,/g, '')) : 0,
                                privacy
                            } : null;
                        }).filter(g => g);
                    }
                """)
                results.extend(groups)
                
                if len(results) >= limit:
                    break
                
                await self.scroll_slowly(300)
                await self.page.wait_for_timeout(1000)
            
            return results[:limit]
        
        return await self.execute('group_search', _search)
    
    async def get_group(self, group_id: str) -> Dict:
        """Get group information."""
        async def _get_group():
            await self.safe_navigate(f'https://www.facebook.com/groups/{group_id}')
            
            group_info = await self.page.evaluate("""
                () => {
                    const name = document.querySelector('h1')?.textContent;
                    const privacy = document.body.textContent.includes('Private group') ? 'private' : 'public';
                    const members = document.body.textContent.match(/([\\d,]+) members?/)?.[1];
                    const description = document.querySelector('[data-testid="group_description"]')?.textContent;
                    
                    return {
                        name,
                        privacy,
                        members: members ? parseInt(members.replace(/,/g, '')) : 0,
                        description,
                        url: window.location.href
                    };
                }
            """)
            
            return group_info
        
        return await self.execute('group_view', _get_group)
    
    async def join_group(self, group_id: str) -> Dict:
        """Join a group."""
        async def _join():
            await self.safe_navigate(f'https://www.facebook.com/groups/{group_id}')
            
            # Find join button
            join_btn = await self.page.query_selector('[aria-label="Join group"]')
            if not join_btn:
                join_btn = await self.page.query_selector('text=Join group')
            
            if not join_btn:
                raise Exception("Join button not found - may already be a member")
            
            await self.human_click(join_btn)
            await self.page.wait_for_timeout(2000)
            
            # Handle questions if private group
            questions = await self.page.query_selector('[role="dialog"]')
            if questions:
                # Skip questions for now - just close dialog
                close_btn = await self.page.query_selector('[aria-label="Close"]')
                if close_btn:
                    await self.human_click(close_btn)
            
            return {'joined': True, 'group_id': group_id}
        
        return await self.execute('group_join', _join, account_age_days=None)
    
    async def leave_group(self, group_id: str) -> Dict:
        """Leave a group."""
        async def _leave():
            await self.safe_navigate(f'https://www.facebook.com/groups/{group_id}')
            
            # Click joined button
            joined_btn = await self.page.query_selector('[aria-label="Joined"]')
            if not joined_btn:
                raise Exception("Not a member of this group")
            
            await self.human_click(joined_btn)
            await self.page.wait_for_timeout(500)
            
            # Click leave group
            leave_btn = await self.page.query_selector('[role="menuitem"]:has-text("Leave group")')
            if not leave_btn:
                leave_btn = await self.page.query_selector('text=Leave group')
            
            if not leave_btn:
                raise Exception("Leave option not found")
            
            await self.human_click(leave_btn)
            await self.page.wait_for_timeout(500)
            
            # Confirm
            confirm_btn = await self.page.query_selector('[aria-label="Leave group"]')
            if confirm_btn:
                await self.human_click(confirm_btn)
            
            await self.page.wait_for_timeout(2000)
            
            return {'left': True, 'group_id': group_id}
        
        return await self.execute('group_leave', _leave)
    
    async def post_to_group(self, group_id: str, content: str, image_paths: Optional[List[str]] = None) -> Dict:
        """Post to a group."""
        async def _post():
            await self.safe_navigate(f'https://www.facebook.com/groups/{group_id}')
            
            # Click post composer
            composer = await self.page.query_selector('[role="textbox"][contenteditable="true"]')
            if not composer:
                # Try clicking "Write something..."
                write_btn = await self.page.query_selector('text=Write something')
                if write_btn:
                    await self.human_click(write_btn)
                    await self.page.wait_for_timeout(1000)
                    composer = await self.page.query_selector('[role="textbox"][contenteditable="true"]')
            
            if not composer:
                raise Exception("Post composer not found")
            
            await self.human_click(composer)
            await self.page.wait_for_timeout(500)
            await self.human_type(composer, content)
            
            # Upload images if provided
            if image_paths:
                photo_btn = await self.page.query_selector('[aria-label="Photo/video"]')
                if photo_btn:
                    await self.human_click(photo_btn)
                    await self.page.wait_for_timeout(500)
                    
                    file_input = await self.page.query_selector('input[type="file"]')
                    if file_input:
                        await file_input.set_input_files(image_paths)
                        await self.page.wait_for_timeout(2000)
            
            # Click post
            post_btn = await self.page.query_selector('[aria-label="Post"]')
            if not post_btn:
                post_btn = await self.page.query_selector('text=Post')
            
            if not post_btn:
                raise Exception("Post button not found")
            
            await self.human_click(post_btn)
            await self.page.wait_for_timeout(3000)
            
            return {'posted': True, 'group_id': group_id, 'content': content[:50]}
        
        return await self.execute('post', _post, account_age_days=None)
    
    async def get_group_posts(self, group_id: str, limit: int = 20) -> Dict:
        """Get posts from a group."""
        async def _get_posts():
            await self.safe_navigate(f'https://www.facebook.com/groups/{group_id}')
            
            posts = []
            for _ in range(limit // 10):
                batch = await self.page.evaluate("""
                    () => {
                        const articles = document.querySelectorAll('[role="article"]');
                        return Array.from(articles).slice(0, 10).map(article => {
                            const author = article.querySelector('a[role="link"] span')?.textContent;
                            const content = article.querySelector('[data-ad-preview="message"]')?.textContent;
                            const timestamp = article.querySelector('abbr')?.textContent;
                            
                            return author && content ? {
                                author,
                                content: content.substring(0, 200),
                                timestamp
                            } : null;
                        }).filter(p => p);
                    }
                """)
                posts.extend(batch)
                
                if len(posts) >= limit:
                    break
                
                await self.scroll_slowly(300)
                await self.page.wait_for_timeout(1000)
            
            return posts[:limit]
        
        return await self.execute('group_posts_view', _get_posts)
