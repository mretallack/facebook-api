# Facebook API Caching - Implementation Tasks

## Phase 1: Database Setup

- [ ] **Task 1.1**: Create SQLite database schema
  - Create `src/cache/database.py` with SQLAlchemy models
  - Define tables: cached_posts, cached_friends, cached_profile, cached_friend_requests, cache_metadata
  - Add indexes on fetched_at and expires_at columns
  - Create database initialization function

- [ ] **Task 1.2**: Implement cache service layer
  - Create `src/cache/cache_service.py`
  - Add methods: get_posts(), set_posts(), get_friends(), set_friends(), etc.
  - Implement cache expiry logic
  - Add transaction handling

- [ ] **Task 1.3**: Add cache configuration
  - Update `config/settings.py` with cache settings
  - Add refresh intervals (posts: 5min, friends: 15min, profile: 30min, requests: 10min)
  - Add cache expiry times
  - Add rate limit settings

## Phase 2: Background Scheduler

- [ ] **Task 2.1**: Create background task scheduler
  - Create `src/cache/scheduler.py`
  - Use APScheduler for periodic tasks
  - Add task for each data type (posts, friends, profile, requests)
  - Implement task queue with rate limiting

- [ ] **Task 2.2**: Implement refresh tasks
  - Create `src/cache/refresh_tasks.py`
  - Add refresh_posts() task
  - Add refresh_friends() task
  - Add refresh_profile() task
  - Add refresh_friend_requests() task
  - Each task: check rate limit → scrape → update cache → update metadata

- [ ] **Task 2.3**: Add rate limiting and backoff
  - Implement rate limiter (1 scrape/minute max)
  - Add exponential backoff on errors
  - Track error counts in metadata
  - Skip refresh if too many recent errors

- [ ] **Task 2.4**: Integrate scheduler with API startup
  - Update `src/api/main.py` lifespan
  - Start scheduler on app startup
  - Stop scheduler on app shutdown
  - Add asyncio locks to prevent concurrent scrapes

## Phase 3: API Integration

- [ ] **Task 3.1**: Update posts endpoint to use cache
  - Modify `src/api/routes/posts.py`
  - Check cache first, return if valid
  - Add `?fresh=true` parameter to bypass cache
  - Add cache headers to response

- [ ] **Task 3.2**: Update friends endpoint to use cache
  - Modify `src/api/routes/friends.py`
  - Check cache first for list and requests
  - Add `?fresh=true` parameter
  - Add cache headers

- [ ] **Task 3.3**: Update profile endpoint to use cache
  - Modify `src/api/routes/profile.py`
  - Check cache first
  - Add `?fresh=true` parameter
  - Add cache headers

- [ ] **Task 3.4**: Add cache management endpoints
  - Create `src/api/routes/cache.py`
  - Add `GET /cache/status` endpoint
  - Add `POST /cache/refresh/{type}` endpoint
  - Add `DELETE /cache/clear` endpoint

## Phase 4: Testing & Monitoring

- [ ] **Task 4.1**: Add cache unit tests
  - Test cache service CRUD operations
  - Test expiry logic
  - Test concurrent access
  - Test error handling

- [ ] **Task 4.2**: Add scheduler tests
  - Test refresh tasks
  - Test rate limiting
  - Test backoff logic
  - Test error recovery

- [ ] **Task 4.3**: Add integration tests
  - Test API with cache enabled
  - Test fresh parameter
  - Test cache headers
  - Test stale data fallback

- [ ] **Task 4.4**: Add monitoring and logging
  - Log each cache refresh
  - Log cache hits/misses
  - Log errors with context
  - Add metrics endpoint

## Phase 5: Deployment & Tuning

- [ ] **Task 5.1**: Update deployment configuration
  - Add SQLite database path to config
  - Update systemd service if needed
  - Add database backup script
  - Document cache management

- [ ] **Task 5.2**: Performance testing
  - Measure API response times
  - Test with multiple concurrent clients
  - Verify memory usage
  - Tune refresh intervals if needed

- [ ] **Task 5.3**: Documentation
  - Update API documentation with cache behavior
  - Document cache management endpoints
  - Add troubleshooting guide
  - Update README with caching info

- [ ] **Task 5.4**: Monitor and optimize
  - Monitor cache hit rates
  - Check error rates
  - Adjust refresh intervals based on usage
  - Optimize database queries if needed

## Dependencies

- SQLAlchemy (ORM)
- APScheduler (background tasks)
- aiosqlite (async SQLite)

## Estimated Effort

- Phase 1: 4 hours
- Phase 2: 6 hours
- Phase 3: 4 hours
- Phase 4: 4 hours
- Phase 5: 2 hours

**Total**: ~20 hours

## Phase 6: Friends vs Following Feed Separation

- [ ] **Task 6.1**: Add source_type column to cached_posts table
  - Update database schema to add source_type column ('friend' or 'following')
  - Create migration to add column to existing database
  - Update CachedPost model in database.py

- [ ] **Task 6.2**: Create following list scraper
  - Create method to scrape list of pages/people user is following
  - Store following list in cache (similar to friends)
  - Add cached_following table to database

- [ ] **Task 6.3**: Update FeedAggregator to classify posts
  - Match post authors against friends list → mark as 'friend'
  - Match post authors against following list → mark as 'following'
  - Exclude posts that match neither list
  - Exclude sponsored and suggested posts

- [ ] **Task 6.4**: Add /posts/following endpoint
  - Create new endpoint to return following feed
  - Filter cached posts where source_type='following'
  - Sort by timestamp descending

- [ ] **Task 6.5**: Update /posts/feed endpoint
  - Filter cached posts where source_type='friend'
  - Exclude posts from non-friends
  - Sort by timestamp descending

- [ ] **Task 6.6**: Add Following tab to Android app
  - Update navigation to include Following tab
  - Create FollowingScreen composable
  - Add FollowingViewModel
  - Wire up to /posts/following endpoint

- [ ] **Task 6.7**: Test and verify filtering
  - Verify friends feed only shows friends' posts
  - Verify following feed only shows following posts
  - Verify no overlap between feeds
  - Test in Android app

## Success Criteria

- [ ] Friends feed shows ONLY posts from actual friends
- [ ] Following feed shows ONLY posts from following (non-friends)
- [ ] No posts from non-friends/non-following appear in either feed
- [ ] Both feeds sorted by timestamp (newest first)
- [ ] Android app has separate tabs for Friends and Following
- [ ] Sponsored/suggested posts excluded from both feeds
