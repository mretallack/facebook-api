"""
Messages service for Facebook messaging.
"""
from typing import Dict, List
from .action_handler import ActionHandler
import logging

logger = logging.getLogger(__name__)


class MessagesService(ActionHandler):
    """Service for Facebook messages management."""
    
    async def get_conversations(self, limit: int = 20) -> Dict:
        """Get list of conversations."""
        async def _get_conversations():
            await self.safe_navigate('https://www.facebook.com/messages')
            await self.page.wait_for_timeout(2000)
            
            conversations = await self.page.evaluate("""
                () => {
                    const convos = document.querySelectorAll('[role="row"], [data-testid="conversation"]');
                    return Array.from(convos).slice(0, 20).map(convo => {
                        const name = convo.querySelector('span[dir="auto"]')?.textContent;
                        const preview = convo.textContent;
                        const link = convo.querySelector('a')?.href;
                        const id = link?.split('/t/')[1]?.split('/')[0];
                        return name && id ? {id, name, preview: preview.substring(0, 100)} : null;
                    }).filter(c => c);
                }
            """)
            
            return conversations[:limit]
        
        return await self.execute('messages_list', _get_conversations)
    
    async def get_messages(self, conversation_id: str, limit: int = 50) -> Dict:
        """Get messages from a conversation."""
        async def _get_messages():
            await self.safe_navigate(f'https://www.facebook.com/messages/t/{conversation_id}')
            await self.page.wait_for_timeout(2000)
            
            messages = await self.page.evaluate("""
                () => {
                    const msgs = document.querySelectorAll('[role="row"]');
                    return Array.from(msgs).slice(-50).map(msg => {
                        const text = msg.querySelector('[dir="auto"]')?.textContent;
                        const time = msg.querySelector('abbr')?.textContent;
                        const isOutgoing = msg.closest('[data-scope="messages_table"]')?.getAttribute('data-is-outgoing') === 'true';
                        return text ? {text, time, is_outgoing: isOutgoing} : null;
                    }).filter(m => m);
                }
            """)
            
            return messages
        
        return await self.execute('messages_view', _get_messages)
    
    async def send_message(self, conversation_id: str, message: str) -> Dict:
        """Send a message."""
        async def _send():
            await self.safe_navigate(f'https://www.facebook.com/messages/t/{conversation_id}')
            await self.page.wait_for_timeout(2000)
            
            # Find message input
            msg_input = await self.selector_manager.find_element(self.page, 'message_composer')
            if not msg_input:
                msg_input = await self.page.query_selector('[aria-label="Message"]')
            
            if not msg_input:
                raise Exception("Message input not found")
            
            await self.human_click(msg_input)
            await self.page.wait_for_timeout(500)
            await self.human_type(msg_input, message)
            
            # Press Enter to send
            await self.page.keyboard.press('Enter')
            await self.page.wait_for_timeout(2000)
            
            return {'sent': True, 'message': message[:50]}
        
        return await self.execute('message', _send, account_age_days=None)
    
    async def mark_as_read(self, conversation_id: str) -> Dict:
        """Mark conversation as read."""
        async def _mark_read():
            await self.safe_navigate(f'https://www.facebook.com/messages/t/{conversation_id}')
            await self.page.wait_for_timeout(2000)
            
            # Just navigating to the conversation marks it as read
            return {'marked_read': True, 'conversation_id': conversation_id}
        
        return await self.execute('messages_view', _mark_read)
