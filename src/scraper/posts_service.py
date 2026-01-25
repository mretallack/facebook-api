"""
Enhanced posts service for creating and interacting with Facebook posts.
"""
from typing import Dict, List, Optional
from .action_handler import ActionHandler
import logging

logger = logging.getLogger(__name__)


class PostsService(ActionHandler):
    """Service for Facebook posts management and interactions."""
    
    async def create_post(
        self,
        content: str,
        image_paths: Optional[List[str]] = None,
        privacy: str = 'public'
    ) -> Dict:
        """Create a new post."""
        async def _create_post():
            await self.safe_navigate('https://www.facebook.com')
            
            # Click post composer
            composer = await self.selector_manager.find_element(self.page, 'post_composer')
            if not composer:
                raise Exception("Post composer not found")
            
            await self.human_click(composer)
            await self.page.wait_for_timeout(1000)
            
            # Type content
            text_area = await self.selector_manager.find_element(self.page, 'post_composer')
            if text_area:
                await self.human_type(text_area, content)
            
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
            
            # Set privacy if needed
            if privacy != 'public':
                privacy_btn = await self.page.query_selector('[aria-label*="Privacy"]')
                if privacy_btn:
                    await self.human_click(privacy_btn)
                    await self.page.wait_for_timeout(500)
                    
                    # Select privacy option
                    option = await self.page.query_selector(f'text={privacy.capitalize()}')
                    if option:
                        await self.human_click(option)
            
            # Click post button
            post_btn = await self.selector_manager.find_element(self.page, 'post_submit')
            if not post_btn:
                raise Exception("Post button not found")
            
            await self.human_click(post_btn)
            await self.page.wait_for_timeout(3000)
            
            return {'posted': True, 'content': content[:50]}
        
        return await self.execute('post', _create_post, account_age_days=None)
    
    async def delete_post(self, post_id: str) -> Dict:
        """Delete a post."""
        async def _delete():
            # Navigate to post
            await self.safe_navigate(f'https://www.facebook.com/{post_id}')
            
            # Click more options
            more_btn = await self.page.query_selector('[aria-label="More"]')
            if not more_btn:
                raise Exception("More options not found")
            
            await self.human_click(more_btn)
            await self.page.wait_for_timeout(500)
            
            # Click delete
            delete_btn = await self.page.query_selector('[role="menuitem"]:has-text("Delete")')
            if not delete_btn:
                delete_btn = await self.page.query_selector('text=Delete')
            
            if not delete_btn:
                raise Exception("Delete option not found")
            
            await self.human_click(delete_btn)
            await self.page.wait_for_timeout(500)
            
            # Confirm delete
            confirm_btn = await self.page.query_selector('[aria-label="Delete"]')
            if confirm_btn:
                await self.human_click(confirm_btn)
            
            await self.page.wait_for_timeout(2000)
            
            return {'deleted': True, 'post_id': post_id}
        
        return await self.execute('post_delete', _delete)
    
    async def like_post(self, post_id: str) -> Dict:
        """Like a post."""
        async def _like():
            await self.safe_navigate(f'https://www.facebook.com/{post_id}')
            
            like_btn = await self.selector_manager.find_element(self.page, 'like_button')
            if not like_btn:
                raise Exception("Like button not found")
            
            # Check if already liked
            aria_label = await like_btn.get_attribute('aria-label')
            if 'Remove' in aria_label or 'Unlike' in aria_label:
                return {'liked': True, 'already_liked': True}
            
            await self.human_click(like_btn)
            await self.page.wait_for_timeout(1000)
            
            return {'liked': True, 'post_id': post_id}
        
        return await self.execute('like', _like, account_age_days=None)
    
    async def react_post(self, post_id: str, reaction: str = 'like') -> Dict:
        """React to a post with specific reaction."""
        async def _react():
            await self.safe_navigate(f'https://www.facebook.com/{post_id}')
            
            like_btn = await self.selector_manager.find_element(self.page, 'like_button')
            if not like_btn:
                raise Exception("Like button not found")
            
            # Hover to show reactions
            await like_btn.hover()
            await self.page.wait_for_timeout(500)
            
            # Click reaction
            reaction_btn = await self.page.query_selector(f'[aria-label="{reaction.capitalize()}"]')
            if not reaction_btn:
                # Fallback to just liking
                await self.human_click(like_btn)
            else:
                await self.human_click(reaction_btn)
            
            await self.page.wait_for_timeout(1000)
            
            return {'reacted': True, 'reaction': reaction, 'post_id': post_id}
        
        return await self.execute('like', _react, account_age_days=None)
    
    async def comment_post(self, post_id: str, comment: str) -> Dict:
        """Comment on a post."""
        async def _comment():
            await self.safe_navigate(f'https://www.facebook.com/{post_id}')
            
            comment_input = await self.selector_manager.find_element(self.page, 'comment_input')
            if not comment_input:
                raise Exception("Comment input not found")
            
            await self.human_click(comment_input)
            await self.page.wait_for_timeout(500)
            
            await self.human_type(comment_input, comment)
            
            # Press Enter to submit
            await self.page.keyboard.press('Enter')
            await self.page.wait_for_timeout(2000)
            
            return {'commented': True, 'comment': comment[:50], 'post_id': post_id}
        
        return await self.execute('comment', _comment, account_age_days=None)
    
    async def share_post(self, post_id: str, message: Optional[str] = None) -> Dict:
        """Share a post."""
        async def _share():
            await self.safe_navigate(f'https://www.facebook.com/{post_id}')
            
            share_btn = await self.selector_manager.find_element(self.page, 'share_button')
            if not share_btn:
                raise Exception("Share button not found")
            
            await self.human_click(share_btn)
            await self.page.wait_for_timeout(1000)
            
            # Click "Share now" or add message
            if message:
                # Click "Share to Feed"
                share_feed = await self.page.query_selector('text=Share to Feed')
                if share_feed:
                    await self.human_click(share_feed)
                    await self.page.wait_for_timeout(1000)
                    
                    # Add message
                    text_area = await self.page.query_selector('[role="textbox"]')
                    if text_area:
                        await self.human_type(text_area, message)
                    
                    # Click Post
                    post_btn = await self.page.query_selector('[aria-label="Post"]')
                    if post_btn:
                        await self.human_click(post_btn)
            else:
                # Quick share
                share_now = await self.page.query_selector('text=Share now')
                if share_now:
                    await self.human_click(share_now)
            
            await self.page.wait_for_timeout(2000)
            
            return {'shared': True, 'post_id': post_id}
        
        return await self.execute('post', _share, account_age_days=None)
