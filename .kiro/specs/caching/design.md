# Facebook API Caching System

## Overview

Add SQLite caching layer to the Facebook scraper API to improve response times and reduce Facebook scraping load. The system will periodically fetch data in the background and serve cached data to API clients.

## Feed Architecture

### Feed Types

1. **Friends Feed** (`/posts/feed`)
   - Shows posts ONLY from actual Facebook friends
   - Sorted by timestamp (newest first)
   - Filters out suggested posts, sponsored content, and posts from non-friends
   
2. **Following Feed** (`/posts/following`)
   - Shows posts from pages/people the user is following (but not friends with)
   - Sorted by timestamp (newest first)
   - Separate from friends feed

3. **Filtering Rules**
   - Posts from non-friends and non-following accounts are excluded
   - Sponsored and suggested posts are excluded
   - Only show posts where author is in friends list OR following list

## Architecture

### Components

1. **Cache Database (SQLite)**
   - Store posts (with friend/following flag), friends, following, profile data, friend requests
   - Track last update timestamp per data type
   - Store metadata (fetch time, expiry)

2. **Background Scheduler**
   - Periodic tasks to refresh cached data
   - Respects rate limits and preflight checks
   - Configurable refresh intervals

3. **API Layer Updates**
   - Serve cached data by default
   - Optional `?fresh=true` parameter to force live scraping
   - Return cache metadata in response headers

### Database Schema

```sql
-- Posts cache (includes source type)
CREATE TABLE cached_posts (
    id TEXT PRIMARY KEY,
    author_name TEXT,
    author_url TEXT,
    content TEXT,
    timestamp TEXT,
    post_type TEXT,
    is_sponsored BOOLEAN,
    is_suggested BOOLEAN,
    source_type TEXT,  -- 'friend' or 'following'
    likes INTEGER,
    comments INTEGER,
    shares INTEGER,
    images TEXT,  -- JSON array
    videos TEXT,  -- JSON array
    fetched_at TIMESTAMP,
    expires_at TIMESTAMP
);

-- Friends cache
CREATE TABLE cached_friends (
    id TEXT PRIMARY KEY,
    name TEXT,
    url TEXT,
    mutual_friends INTEGER,
    profile_picture TEXT,
    fetched_at TIMESTAMP,
    expires_at TIMESTAMP
);

-- Profile cache
CREATE TABLE cached_profile (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    bio TEXT,
    url TEXT,
    fetched_at TIMESTAMP,
    expires_at TIMESTAMP
);

-- Friend requests cache
CREATE TABLE cached_friend_requests (
    id TEXT PRIMARY KEY,
    name TEXT,
    url TEXT,
    mutual_friends INTEGER,
    profile_picture TEXT,
    fetched_at TIMESTAMP,
    expires_at TIMESTAMP
);

-- Metadata
CREATE TABLE cache_metadata (
    key TEXT PRIMARY KEY,
    last_fetch TIMESTAMP,
    next_fetch TIMESTAMP,
    fetch_count INTEGER,
    error_count INTEGER
);
```

### Refresh Intervals

- **Posts**: Every 5 minutes
- **Friends**: Every 15 minutes
- **Profile**: Every 30 minutes
- **Friend Requests**: Every 10 minutes

### Rate Limiting

- Maximum 1 scrape operation per minute
- Use preflight checker before each scrape
- Exponential backoff on errors
- Skip refresh if previous fetch failed recently

## Implementation Considerations

### Concurrency
- Use asyncio locks to prevent concurrent scrapes
- Queue refresh tasks if rate limit reached
- Single worker process to avoid session conflicts

### Error Handling
- Serve stale cache if fresh fetch fails
- Log errors but don't crash scheduler
- Increment error counter in metadata
- Increase backoff time after repeated failures

### Cache Invalidation
- Expire posts after 1 hour
- Expire friends after 4 hours
- Expire profile after 8 hours
- Manual invalidation endpoint for testing

### API Endpoints

New endpoints:
- `GET /cache/status` - Show cache health and last refresh times
- `POST /cache/refresh/{type}` - Manually trigger refresh for specific data type
- `DELETE /cache/clear` - Clear all cached data

Modified endpoints (add `?fresh=true` parameter):
- `GET /posts/feed?fresh=true` - Force live scraping
- `GET /friends/list?fresh=true` - Force live scraping
- `GET /profile/me?fresh=true` - Force live scraping

Response headers:
- `X-Cache-Hit: true/false`
- `X-Cache-Age: <seconds>`
- `X-Cache-Expires: <timestamp>`

## Benefits

1. **Performance**: Sub-second API responses instead of 10-15 seconds
2. **Reliability**: Serve cached data even if Facebook scraping fails
3. **Rate Limiting**: Controlled scraping frequency
4. **User Experience**: Instant app loading
5. **Scalability**: Multiple API clients can share cache

## Migration Path

1. Add SQLite database and models
2. Implement cache service layer
3. Add background scheduler
4. Update API endpoints to use cache
5. Add cache management endpoints
6. Update Android app (no changes needed - transparent)
7. Monitor and tune refresh intervals
