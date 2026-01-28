from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class CachedPost(Base):
    __tablename__ = 'cached_posts'
    
    id = Column(String, primary_key=True)
    author_name = Column(String)
    author_url = Column(String)
    content = Column(Text)
    timestamp = Column(String)
    post_type = Column(String)
    is_sponsored = Column(Boolean)
    is_suggested = Column(Boolean)
    source_type = Column(String)  # 'friend' or 'following'
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    images = Column(Text)  # JSON array
    videos = Column(Text)  # JSON array
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, index=True)

class CachedFriend(Base):
    __tablename__ = 'cached_friends'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    url = Column(String)
    mutual_friends = Column(Integer, default=0)
    profile_picture = Column(String)
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, index=True)

class CachedFollowing(Base):
    __tablename__ = 'cached_following'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    url = Column(String)
    profile_picture = Column(String)
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, index=True)

class CachedProfile(Base):
    __tablename__ = 'cached_profile'
    
    user_id = Column(String, primary_key=True)
    name = Column(String)
    bio = Column(Text)
    url = Column(String)
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, index=True)

class CachedFriendRequest(Base):
    __tablename__ = 'cached_friend_requests'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    url = Column(String)
    mutual_friends = Column(Integer, default=0)
    profile_picture = Column(String)
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, index=True)

class CacheMetadata(Base):
    __tablename__ = 'cache_metadata'
    
    key = Column(String, primary_key=True)
    last_fetch = Column(DateTime)
    next_fetch = Column(DateTime)
    fetch_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)

def init_database(db_path: str = "cache.db"):
    """Initialize database and create tables"""
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    """Get database session"""
    Session = sessionmaker(bind=engine)
    return Session()
