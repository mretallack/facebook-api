from datetime import datetime, timedelta
from typing import List, Optional, Dict
import json
from sqlalchemy.orm import Session
from src.cache.database import (
    CachedPost, CachedFriend, CachedFollowing, CachedProfile, 
    CachedFriendRequest, CacheMetadata, get_session
)

class CacheService:
    def __init__(self, engine):
        self.engine = engine
    
    def _get_session(self) -> Session:
        return get_session(self.engine)
    
    # Posts
    def get_posts(self, limit: int = 20, source_type: str = None) -> Optional[List[Dict]]:
        session = self._get_session()
        try:
            query = session.query(CachedPost).filter(
                CachedPost.expires_at > datetime.utcnow()
            )
            
            if source_type:
                query = query.filter(CachedPost.source_type == source_type)
            
            # Order by fetched_at descending to get newest first
            query = query.order_by(CachedPost.fetched_at.desc())
            
            posts = query.limit(limit).all()
            
            print(f"[CacheService] Query returned {len(posts)} posts (limit={limit}, source_type={source_type})")
            
            if not posts:
                return None
            
            result = [self._post_to_dict(p) for p in posts]
            print(f"[CacheService] Converted to {len(result)} dicts")
            return result
        finally:
            session.close()
    
    def set_posts(self, posts: List[Dict], expiry_hours: int = 1):
        session = self._get_session()
        try:
            # Clear old posts
            session.query(CachedPost).delete()
            
            # Add new posts
            expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
            for post in posts:
                cached_post = CachedPost(
                    id=post['id'],
                    author_name=post['author']['name'],
                    author_url=post['author']['profile_url'],
                    content=post['content'],
                    timestamp=post['timestamp'],
                    post_type=post['post_type'],
                    is_sponsored=post['is_sponsored'],
                    is_suggested=post['is_suggested'],
                    source_type=post.get('source_type', 'friend'),
                    likes=post['engagement']['likes'],
                    comments=post['engagement']['comments'],
                    shares=post['engagement']['shares'],
                    images=json.dumps(post['media']['images']),
                    videos=json.dumps(post['media']['videos']),
                    expires_at=expires_at
                )
                session.add(cached_post)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Friends
    def get_friends(self) -> Optional[List[Dict]]:
        session = self._get_session()
        try:
            friends = session.query(CachedFriend).filter(
                CachedFriend.expires_at > datetime.utcnow()
            ).all()
            
            if not friends:
                return None
            
            return [self._friend_to_dict(f) for f in friends]
        finally:
            session.close()
    
    def set_friends(self, friends: List[Dict], expiry_hours: int = 4):
        session = self._get_session()
        try:
            session.query(CachedFriend).delete()
            
            expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
            for friend in friends:
                cached_friend = CachedFriend(
                    id=friend.get('id', ''),
                    name=friend['name'],
                    url=friend['url'],
                    mutual_friends=friend.get('mutual_friends', 0),
                    profile_picture=friend.get('profile_picture', ''),
                    expires_at=expires_at
                )
                session.add(cached_friend)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Profile
    def get_profile(self) -> Optional[Dict]:
        session = self._get_session()
        try:
            profile = session.query(CachedProfile).filter(
                CachedProfile.expires_at > datetime.utcnow()
            ).first()
            
            if not profile:
                return None
            
            return {
                'name': profile.name,
                'bio': profile.bio,
                'url': profile.url
            }
        finally:
            session.close()
    
    def set_profile(self, profile: Dict, expiry_hours: int = 8):
        session = self._get_session()
        try:
            session.query(CachedProfile).delete()
            
            expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
            cached_profile = CachedProfile(
                user_id='default',
                name=profile.get('name'),
                bio=profile.get('bio'),
                url=profile.get('url'),
                expires_at=expires_at
            )
            session.add(cached_profile)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Friend Requests
    def get_friend_requests(self) -> Optional[List[Dict]]:
        session = self._get_session()
        try:
            requests = session.query(CachedFriendRequest).filter(
                CachedFriendRequest.expires_at > datetime.utcnow()
            ).all()
            
            if not requests:
                return None
            
            return [self._friend_to_dict(r) for r in requests]
        finally:
            session.close()
    
    def set_friend_requests(self, requests: List[Dict], expiry_hours: int = 2):
        session = self._get_session()
        try:
            session.query(CachedFriendRequest).delete()
            
            expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
            for req in requests:
                cached_req = CachedFriendRequest(
                    id=req.get('id', ''),
                    name=req['name'],
                    url=req['url'],
                    mutual_friends=req.get('mutual_friends', 0),
                    profile_picture=req.get('profile_picture', ''),
                    expires_at=expires_at
                )
                session.add(cached_req)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Metadata
    def get_metadata(self, key: str) -> Optional[Dict]:
        session = self._get_session()
        try:
            meta = session.query(CacheMetadata).filter_by(key=key).first()
            if not meta:
                return None
            return {
                'last_fetch': meta.last_fetch,
                'next_fetch': meta.next_fetch,
                'fetch_count': meta.fetch_count,
                'error_count': meta.error_count
            }
        finally:
            session.close()
    
    def update_metadata(self, key: str, success: bool, next_fetch: datetime):
        session = self._get_session()
        try:
            meta = session.query(CacheMetadata).filter_by(key=key).first()
            if not meta:
                meta = CacheMetadata(
                    key=key,
                    fetch_count=0,
                    error_count=0
                )
                session.add(meta)
            
            meta.last_fetch = datetime.utcnow()
            meta.next_fetch = next_fetch
            meta.fetch_count += 1
            if not success:
                meta.error_count += 1
            else:
                meta.error_count = 0  # Reset on success
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Helper methods
    def _post_to_dict(self, post: CachedPost, base_url: str = None) -> Dict:
        import hashlib
        
        # Convert image URLs to cached image URLs
        images = json.loads(post.images) if post.images else []
        
        # Generate cache keys for images - use relative URLs if no base_url provided
        cached_images = []
        for img_url in images:
            cache_key = hashlib.md5(img_url.encode()).hexdigest()
            if base_url:
                cached_images.append(f"{base_url}/media/image/{cache_key}")
            else:
                # Return relative URL - client will resolve against their base URL
                cached_images.append(f"/media/image/{cache_key}")
        
        return {
            'id': post.id,
            'author': {
                'name': post.author_name,
                'profile_url': post.author_url
            },
            'content': post.content,
            'timestamp': post.timestamp,
            'post_type': post.post_type,
            'is_sponsored': post.is_sponsored,
            'is_suggested': post.is_suggested,
            'source_type': post.source_type,
            'engagement': {
                'likes': post.likes,
                'comments': post.comments,
                'shares': post.shares
            },
            'media': {
                'images': cached_images,
                'videos': json.loads(post.videos) if post.videos else []
            }
        }
    
    def _friend_to_dict(self, friend) -> Dict:
        return {
            'id': friend.id,
            'name': friend.name,
            'url': friend.url,
            'mutual_friends': friend.mutual_friends,
            'profile_picture': friend.profile_picture
        }
