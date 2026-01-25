"""
Profile service for managing Facebook profile operations.
"""
from typing import Dict, Optional
from .action_handler import ActionHandler
import logging

logger = logging.getLogger(__name__)


class ProfileService(ActionHandler):
    """Service for Facebook profile management."""
    
    async def get_profile(self) -> Dict:
        """Get current user's profile information."""
        async def _get_profile():
            # Navigate to profile
            await self.safe_navigate('https://www.facebook.com/me')
            
            # Extract profile data
            profile_data = await self.page.evaluate("""
                () => {
                    const getName = () => {
                        const selectors = [
                            'h1[role="heading"]',
                            'h1',
                            '[data-testid="profile_name"]'
                        ];
                        for (const sel of selectors) {
                            const el = document.querySelector(sel);
                            if (el) return el.textContent.trim();
                        }
                        return null;
                    };
                    
                    const getBio = () => {
                        const selectors = [
                            '[data-testid="profile_bio"]',
                            'div[role="main"] div[dir="auto"]'
                        ];
                        for (const sel of selectors) {
                            const el = document.querySelector(sel);
                            if (el) return el.textContent.trim();
                        }
                        return null;
                    };
                    
                    return {
                        name: getName(),
                        bio: getBio(),
                        url: window.location.href,
                    };
                }
            """)
            
            return profile_data
        
        return await self.execute('profile_view', _get_profile)
    
    async def update_profile(self, name: Optional[str] = None, bio: Optional[str] = None) -> Dict:
        """Update profile information."""
        async def _update_profile():
            # Navigate to edit profile
            await self.safe_navigate('https://www.facebook.com/me/about')
            
            updates = {}
            
            if name:
                # Find and click edit name button
                edit_btn = await self.wait_for_element('edit_name_button')
                if edit_btn:
                    await self.human_click(edit_btn)
                    
                    # Find name input
                    name_input = await self.wait_for_element('name_input')
                    if name_input:
                        await name_input.fill('')
                        await self.human_type(name_input, name)
                        
                        # Save
                        save_btn = await self.wait_for_element('save_button')
                        if save_btn:
                            await self.human_click(save_btn)
                            updates['name'] = name
            
            if bio:
                # Find and click edit bio button
                edit_bio_btn = await self.wait_for_element('edit_bio_button')
                if edit_bio_btn:
                    await self.human_click(edit_bio_btn)
                    
                    # Find bio input
                    bio_input = await self.wait_for_element('bio_input')
                    if bio_input:
                        await bio_input.fill('')
                        await self.human_type(bio_input, bio)
                        
                        # Save
                        save_btn = await self.wait_for_element('save_button')
                        if save_btn:
                            await self.human_click(save_btn)
                            updates['bio'] = bio
            
            return updates
        
        return await self.execute('profile_update', _update_profile)
    
    async def upload_profile_picture(self, image_path: str) -> Dict:
        """Upload profile picture."""
        async def _upload_picture():
            # Navigate to profile
            await self.safe_navigate('https://www.facebook.com/me')
            
            # Click profile picture
            profile_pic = await self.wait_for_element('profile_picture')
            if not profile_pic:
                raise Exception("Profile picture element not found")
            
            await self.human_click(profile_pic)
            
            # Click upload photo
            upload_btn = await self.wait_for_element('upload_photo_button')
            if not upload_btn:
                raise Exception("Upload button not found")
            
            # Set file input
            file_input = await self.page.query_selector('input[type="file"]')
            if not file_input:
                raise Exception("File input not found")
            
            await file_input.set_input_files(image_path)
            
            # Wait for upload and click save
            await self.page.wait_for_timeout(2000)
            save_btn = await self.wait_for_element('save_button')
            if save_btn:
                await self.human_click(save_btn)
            
            return {'uploaded': True, 'path': image_path}
        
        return await self.execute('profile_picture_upload', _upload_picture)
    
    async def upload_cover_photo(self, image_path: str) -> Dict:
        """Upload cover photo."""
        async def _upload_cover():
            # Navigate to profile
            await self.safe_navigate('https://www.facebook.com/me')
            
            # Click cover photo area
            cover_photo = await self.wait_for_element('cover_photo')
            if not cover_photo:
                raise Exception("Cover photo element not found")
            
            await self.human_click(cover_photo)
            
            # Click upload photo
            upload_btn = await self.wait_for_element('upload_photo_button')
            if not upload_btn:
                raise Exception("Upload button not found")
            
            # Set file input
            file_input = await self.page.query_selector('input[type="file"]')
            if not file_input:
                raise Exception("File input not found")
            
            await file_input.set_input_files(image_path)
            
            # Wait for upload and click save
            await self.page.wait_for_timeout(2000)
            save_btn = await self.wait_for_element('save_button')
            if save_btn:
                await self.human_click(save_btn)
            
            return {'uploaded': True, 'path': image_path}
        
        return await self.execute('cover_photo_upload', _upload_cover)
