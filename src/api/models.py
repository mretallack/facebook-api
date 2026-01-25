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
