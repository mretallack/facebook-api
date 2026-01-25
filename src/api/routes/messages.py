"""
Messages API routes.
"""
from fastapi import APIRouter, HTTPException
from typing import List
from ..models import ConversationData, MessageData, SendMessageRequest, MessageActionResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/messages", tags=["messages"])

messages_service = None


def set_messages_service(service):
    """Set the messages service instance."""
    global messages_service
    messages_service = service


@router.get("/conversations", response_model=List[ConversationData])
async def get_conversations(limit: int = 20):
    """Get list of conversations."""
    if not messages_service:
        raise HTTPException(status_code=503, detail="Messages service not initialized")
    
    result = await messages_service.get_conversations(limit)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to get conversations'))
    
    return result['data']


@router.get("/{conversation_id}", response_model=List[MessageData])
async def get_messages(conversation_id: str, limit: int = 50):
    """Get messages from a conversation."""
    if not messages_service:
        raise HTTPException(status_code=503, detail="Messages service not initialized")
    
    result = await messages_service.get_messages(conversation_id, limit)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to get messages'))
    
    return result['data']


@router.post("/send/{conversation_id}", response_model=MessageActionResponse)
async def send_message(conversation_id: str, request: SendMessageRequest):
    """Send a message."""
    if not messages_service:
        raise HTTPException(status_code=503, detail="Messages service not initialized")
    
    result = await messages_service.send_message(conversation_id, request.message)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to send message'))
    
    return MessageActionResponse(success=True, message="Message sent")


@router.post("/{conversation_id}/read", response_model=MessageActionResponse)
async def mark_as_read(conversation_id: str):
    """Mark conversation as read."""
    if not messages_service:
        raise HTTPException(status_code=503, detail="Messages service not initialized")
    
    result = await messages_service.mark_as_read(conversation_id)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Failed to mark as read'))
    
    return MessageActionResponse(success=True, message="Marked as read")
