"""Stories service for Facebook stories"""
import asyncio
from typing import List, Dict
from playwright.async_api import Page


class StoriesService:
    def __init__(self, page: Page):
        self.page = page
    
    async def get_stories(self) -> List[Dict]:
        """Get available stories from feed"""
        try:
            await self.page.goto("https://www.facebook.com/", timeout=30000, wait_until='networkidle')
            await asyncio.sleep(2)
            
            stories = []
            story_elements = await self.page.query_selector_all('[aria-label*="story"]')
            
            for elem in story_elements[:10]:
                try:
                    name = await elem.get_attribute('aria-label')
                    stories.append({
                        'author': name,
                        'timestamp': '',
                        'type': 'image'
                    })
                except:
                    continue
            
            return stories
        except Exception as e:
            print(f"Get stories error: {e}")
            return []
    
    async def create_story(self, image_path: str = None, text: str = None) -> bool:
        """Create a story"""
        try:
            await self.page.goto("https://www.facebook.com/stories/create", 
                               timeout=30000, wait_until='networkidle')
            await asyncio.sleep(2)
            
            if text:
                # Text story
                text_button = await self.page.query_selector('text="Create a text story"')
                if text_button:
                    await text_button.click()
                    await asyncio.sleep(1)
                    
                    text_input = await self.page.query_selector('[contenteditable="true"]')
                    if text_input:
                        await text_input.type(text)
                        await asyncio.sleep(1)
                        
                        share_button = await self.page.query_selector('text="Share to story"')
                        if share_button:
                            await share_button.click()
                            await asyncio.sleep(2)
                            return True
            
            elif image_path:
                # Photo story
                file_input = await self.page.query_selector('input[type="file"]')
                if file_input:
                    await file_input.set_input_files(image_path)
                    await asyncio.sleep(2)
                    
                    share_button = await self.page.query_selector('text="Share to story"')
                    if share_button:
                        await share_button.click()
                        await asyncio.sleep(2)
                        return True
            
            return False
        except Exception as e:
            print(f"Create story error: {e}")
            return False
    
    async def delete_story(self, story_id: str) -> bool:
        """Delete a story"""
        try:
            # Navigate to your stories
            await self.page.goto("https://www.facebook.com/stories", 
                               timeout=30000, wait_until='networkidle')
            await asyncio.sleep(2)
            
            # Find and click delete option
            more_button = await self.page.query_selector('[aria-label="More"]')
            if more_button:
                await more_button.click()
                await asyncio.sleep(1)
                
                delete_button = await self.page.query_selector('text="Delete"')
                if delete_button:
                    await delete_button.click()
                    await asyncio.sleep(1)
                    
                    confirm_button = await self.page.query_selector('text="Delete"')
                    if confirm_button:
                        await confirm_button.click()
                        await asyncio.sleep(2)
                        return True
            
            return False
        except Exception as e:
            print(f"Delete story error: {e}")
            return False
