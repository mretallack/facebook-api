from pydantic import BaseModel
from typing import List, Literal, Optional

class Author(BaseModel):
    name: str
    profile_url: str

class Engagement(BaseModel):
    likes: int
    comments: int
    shares: int

class Media(BaseModel):
    images: List[str]
    videos: List[str]

class Post(BaseModel):
    id: str
    author: Author
    content: str
    timestamp: str
    post_type: Literal['text', 'photo', 'video', 'link', 'mixed']
    is_sponsored: bool
    is_suggested: bool
    engagement: Engagement
    media: Media

class AuthRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str

class HealthResponse(BaseModel):
    status: str
    browser_ready: bool

# Profile models
class ProfileData(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    url: Optional[str] = None

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None

class ProfilePictureResponse(BaseModel):
    success: bool
    uploaded: bool
    path: Optional[str] = None

# Friends models
class FriendData(BaseModel):
    id: Optional[str] = None
    name: str
    url: str
    mutual_friends: Optional[int] = 0

class FriendRequestData(BaseModel):
    profile_url: str

class FriendActionResponse(BaseModel):
    success: bool
    message: Optional[str] = None

# Posts models
class CreatePostRequest(BaseModel):
    content: str
    image_paths: Optional[List[str]] = None
    privacy: Optional[str] = 'public'

class CommentRequest(BaseModel):
    comment: str

class ShareRequest(BaseModel):
    message: Optional[str] = None

class ReactionRequest(BaseModel):
    reaction: str = 'like'

class PostActionResponse(BaseModel):
    success: bool
    message: Optional[str] = None

# Groups models
class GroupData(BaseModel):
    name: str
    url: str
    members: Optional[int] = 0
    privacy: Optional[str] = 'public'
    description: Optional[str] = None

class GroupPostRequest(BaseModel):
    content: str
    image_paths: Optional[List[str]] = None

class GroupActionResponse(BaseModel):
    success: bool
    message: Optional[str] = None

# Messages models
class ConversationData(BaseModel):
    id: str
    name: str
    preview: Optional[str] = None

class MessageData(BaseModel):
    text: str
    time: Optional[str] = None
    is_outgoing: bool = False

class SendMessageRequest(BaseModel):
    message: str

class MessageActionResponse(BaseModel):
    success: bool
    message: Optional[str] = None
