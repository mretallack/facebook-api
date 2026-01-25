# Facebook Full Automation API - Design

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Client                               │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Application                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Route Handlers                          │  │
│  │  /profile  /friends  /posts  /groups  /pages        │  │
│  │  /messages /events   /marketplace  /notifications   │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Service Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Profile    │  │   Friends    │  │    Posts     │     │
│  │   Service    │  │   Service    │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Groups     │  │   Messages   │  │   Events     │     │
│  │   Service    │  │   Service    │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Marketplace │  │    Pages     │  │    Stories   │     │
│  │   Service    │  │   Service    │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Core Components                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Session    │  │  Navigator   │  │  Extractor   │     │
│  │   Manager    │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Action     │  │    Cache     │  │    Queue     │     │
│  │   Handler    │  │   Manager    │  │   Manager    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Playwright Browser Engine                      │
│  - Session persistence                                      │
│  - Anti-detection                                           │
│  - Multi-tab support                                        │
└─────────────────────────────────────────────────────────────┘
```

## Component Design

### 1. API Layer (FastAPI)

**Route Structure**:
```
/api/v1/
├── auth/
│   ├── POST /login
│   ├── POST /logout
│   └── GET /status
├── profile/
│   ├── GET /me
│   ├── PUT /me
│   ├── POST /picture
│   └── POST /cover
├── friends/
│   ├── GET /search
│   ├── GET /list
│   ├── GET /requests
│   ├── POST /request
│   ├── POST /accept/{id}
│   ├── POST /reject/{id}
│   ├── DELETE /{id}
│   └── POST /block/{id}
├── posts/
│   ├── GET /feed
│   ├── GET /{id}
│   ├── POST /create
│   ├── PUT /{id}
│   ├── DELETE /{id}
│   ├── POST /{id}/like
│   ├── POST /{id}/react
│   ├── POST /{id}/comment
│   └── POST /{id}/share
├── groups/
│   ├── GET /search
│   ├── GET /{id}
│   ├── GET /{id}/posts
│   ├── POST /create
│   ├── POST /{id}/join
│   ├── POST /{id}/leave
│   ├── POST /{id}/post
│   └── POST /{id}/invite
├── pages/
│   ├── GET /search
│   ├── GET /{id}
│   ├── POST /{id}/like
│   ├── POST /{id}/unlike
│   ├── POST /create
│   └── POST /{id}/post
├── messages/
│   ├── GET /conversations
│   ├── GET /conversations/{id}
│   ├── POST /send
│   ├── POST /group
│   └── PUT /read/{id}
├── events/
│   ├── GET /search
│   ├── GET /{id}
│   ├── POST /create
│   ├── POST /{id}/rsvp
│   └── POST /{id}/invite
├── marketplace/
│   ├── GET /search
│   ├── GET /{id}
│   ├── POST /create
│   ├── PUT /{id}
│   ├── DELETE /{id}
│   └── POST /{id}/save
├── stories/
│   ├── GET /feed
│   ├── POST /create
│   ├── DELETE /{id}
│   └── POST /{id}/react
└── notifications/
    ├── GET /list
    ├── PUT /read/{id}
    └── PUT /read-all
```

### 2. Service Layer

Each service encapsulates business logic for a specific domain:

**ProfileService**:
- Get/update profile information
- Upload profile/cover photos
- Manage bio and details

**FriendsService**:
- Search users
- Send/accept/reject friend requests
- Manage friendships
- Block/unblock users

**PostsService**:
- Create posts (text, image, video, link)
- Edit/delete posts
- Get post details
- Manage post privacy

**InteractionService**:
- Like/react to posts
- Comment on posts
- Share posts
- Reply to comments

**GroupsService**:
- Search/join/leave groups
- Create groups
- Post in groups
- Manage members (admin)

**PagesService**:
- Search/like pages
- Create pages
- Post as page
- Get page insights

**MessagingService**:
- Get conversations
- Send messages
- Create group chats
- Mark as read

**EventsService**:
- Search/create events
- RSVP to events
- Invite to events
- Post in events

**MarketplaceService**:
- Search listings
- Create/edit/delete listings
- Save listings
- Message sellers

**StoriesService**:
- Post stories
- View stories
- React to stories
- Delete stories

**NotificationService**:
- Get notifications
- Mark as read
- Get unread count

### 3. Core Components

**SessionManager** (Enhanced):
```python
class SessionManager:
    - browser: Browser
    - contexts: Dict[str, BrowserContext]  # Multi-account support
    - pages: Dict[str, Page]
    - cookie_store: str = "cookies/"  # Per-account cookie storage
    
    async def create_session(account_id: str)
    async def get_session(account_id: str)
    async def close_session(account_id: str)
    async def is_logged_in(account_id: str)
    async def save_cookies(account_id: str)
    async def load_cookies(account_id: str)
    async def enable_remember_me(account_id: str)
```

**Cookie Persistence Strategy**:
- Store cookies per account: `cookies/{account_id}.json`
- Save cookies after every successful login
- Load cookies on session creation
- Validate cookie freshness (check if still logged in)
- Re-login only if cookies expired or invalid
- Enable "Remember Me" checkbox during login to extend session lifetime

**Remember Me Implementation**:
```python
async def login_with_remember(email: str, password: str):
    # Fill login form
    await page.fill('input[name="email"]', email)
    await page.fill('input[name="pass"]', password)
    
    # Check "Remember Me" checkbox if present
    try:
        remember_checkbox = await page.query_selector('input[name="persistent"]')
        if remember_checkbox and not await remember_checkbox.is_checked():
            await remember_checkbox.check()
    except:
        pass
    
    # Submit login
    await page.evaluate('document.querySelector("button[name=login]").click()')
    
    # Save cookies after successful login
    await save_cookies(account_id)
```

**Session Validation**:
```python
async def validate_session(account_id: str) -> bool:
    """Check if existing cookies are still valid"""
    if not cookie_file_exists(account_id):
        return False
    
    await load_cookies(account_id)
    
    # Quick validation: check if we can access a protected page
    try:
        await page.goto("https://www.facebook.com/me")
        await page.wait_for_selector('[data-pagelet="ProfileActions"]', timeout=5000)
        return True
    except:
        return False
```

**Cookie Refresh Strategy**:
- Validate cookies on startup
- Re-save cookies after every 100 actions
- Automatic re-login if validation fails
- Cookie expiry tracking (Facebook cookies typically last 30 days with "Remember Me")
- Proactive refresh before expiry

**Navigator**:
```python
class Navigator:
    - Handles navigation to different Facebook sections
    - Waits for page loads
    - Handles redirects
    - Manages URL construction
    
    async def goto_profile(user_id: str)
    async def goto_group(group_id: str)
    async def goto_page(page_id: str)
    async def goto_marketplace()
    async def goto_messages()
```

**Extractor**:
```python
class Extractor:
    - Extracts data from Facebook pages
    - Handles dynamic content loading
    - Parses different content types
    
    async def extract_profile(page: Page)
    async def extract_posts(page: Page)
    async def extract_comments(page: Page)
    async def extract_friends(page: Page)
```

**ActionHandler**:
```python
class ActionHandler:
    - Performs actions on Facebook
    - Handles form submissions
    - Manages file uploads
    - Implements retry logic
    
    async def click_button(selector: str)
    async def fill_form(data: Dict)
    async def upload_file(path: str)
    async def submit_form()
```

**CacheManager**:
```python
class CacheManager:
    - Caches frequently accessed data
    - Reduces Facebook requests
    - Implements TTL
    
    async def get(key: str)
    async def set(key: str, value: Any, ttl: int)
    async def invalidate(key: str)
```

**QueueManager**:
```python
class QueueManager:
    - Manages action queue
    - Implements rate limiting
    - Handles concurrent requests
    
    async def enqueue(action: Action)
    async def process_queue()
    async def get_queue_status()
```

### 4. Data Models

**Pydantic Models**:

```python
# Profile
class Profile(BaseModel):
    id: str
    name: str
    username: Optional[str]
    bio: Optional[str]
    profile_picture: Optional[str]
    cover_photo: Optional[str]
    friends_count: int
    followers_count: int

# Friend Request
class FriendRequest(BaseModel):
    id: str
    from_user: Profile
    timestamp: datetime
    mutual_friends: int

# Post
class Post(BaseModel):
    id: str
    author: Profile
    content: str
    timestamp: datetime
    privacy: str
    reactions: Dict[str, int]
    comments_count: int
    shares_count: int
    media: List[Media]

# Comment
class Comment(BaseModel):
    id: str
    author: Profile
    content: str
    timestamp: datetime
    reactions: Dict[str, int]
    replies: List['Comment']

# Group
class Group(BaseModel):
    id: str
    name: str
    description: str
    privacy: str
    members_count: int
    cover_photo: Optional[str]

# Message
class Message(BaseModel):
    id: str
    conversation_id: str
    sender: Profile
    content: str
    timestamp: datetime
    attachments: List[Attachment]
    is_read: bool

# Event
class Event(BaseModel):
    id: str
    name: str
    description: str
    start_time: datetime
    end_time: Optional[datetime]
    location: Optional[str]
    host: Profile
    attendees_count: int

# Marketplace Listing
class Listing(BaseModel):
    id: str
    title: str
    description: str
    price: float
    currency: str
    location: str
    seller: Profile
    images: List[str]
    category: str
    condition: str
```

## Sequence Diagrams

### Post Creation Flow
```
Client          API         PostService    ActionHandler    Browser
  │              │               │               │             │
  │─POST /posts─>│               │               │             │
  │              │─create()─────>│               │             │
  │              │               │─navigate()───>│             │
  │              │               │               │─goto()─────>│
  │              │               │               │<─loaded─────│
  │              │               │<─ready────────│             │
  │              │               │─fill_form()──>│             │
  │              │               │               │─type()─────>│
  │              │               │               │─upload()───>│
  │              │               │<─filled───────│             │
  │              │               │─submit()─────>│             │
  │              │               │               │─click()────>│
  │              │               │               │<─posted─────│
  │              │               │<─success──────│             │
  │              │<─post_data────│               │             │
  │<─201 Created│               │               │             │
```

### Friend Request Flow
```
Client          API      FriendsService   Navigator    Extractor    Browser
  │              │             │              │            │           │
  │─POST /friend│             │              │            │           │
  │  /request───>│             │              │            │           │
  │              │─send()─────>│              │            │           │
  │              │             │─goto_profile>│            │           │
  │              │             │              │─navigate──>│           │
  │              │             │              │<─loaded────│           │
  │              │             │<─ready───────│            │           │
  │              │             │─extract()────────────────>│           │
  │              │             │              │            │─query────>│
  │              │             │<─user_data────────────────│           │
  │              │             │─click_add_friend()───────────────────>│
  │              │             │              │            │<─clicked──│
  │              │             │<─success─────│            │           │
  │              │<─confirmed──│              │            │           │
  │<─200 OK─────│             │              │            │           │
```

## Implementation Considerations

### Session Persistence & Cookie Management

**Cookie Storage**:
- Store cookies per account in `cookies/{account_id}.json`
- Use Playwright's `storage_state` for complete session persistence
- Include localStorage and sessionStorage data
- Encrypt cookie files for security

**Remember Me Feature**:
- Always enable "Remember Me" checkbox during login
- Selector: `input[name="persistent"]` or `input[type="checkbox"][name="login_persistent"]`
- Extends Facebook session from 1 day to 30 days
- Reduces login frequency significantly

**Session Lifecycle**:
1. **Startup**: Load cookies from file if exists
2. **Validation**: Check if cookies are still valid
3. **Login**: Only if validation fails
4. **Periodic Save**: Save cookies after every 100 actions
5. **Shutdown**: Save cookies before closing

**Cookie Validation**:
```python
async def is_session_valid(account_id: str) -> bool:
    # Load cookies
    cookie_file = f"cookies/{account_id}.json"
    if not os.path.exists(cookie_file):
        return False
    
    # Check cookie age
    file_age = time.time() - os.path.getmtime(cookie_file)
    if file_age > 25 * 24 * 3600:  # 25 days (refresh before 30-day expiry)
        return False
    
    # Validate by accessing protected page
    try:
        await page.goto("https://www.facebook.com/me", timeout=10000)
        return await page.query_selector('[data-pagelet="ProfileActions"]') is not None
    except:
        return False
```

**Benefits**:
- Reduces login attempts by 95%+
- Avoids Facebook login rate limits
- Faster API startup (no login delay)
- Lower detection risk (fewer login events)
- Better user experience

### Facebook Selectors Strategy
- Maintain selector database with fallbacks
- Use data attributes when available
- Implement selector auto-discovery
- Version selectors by Facebook UI version
- Regular selector validation

### Rate Limiting
- Implement exponential backoff
- Track action frequency per account
- Respect Facebook's rate limits:
  - Friend requests: ~20/hour
  - Posts: ~10/hour
  - Messages: ~50/hour
  - Likes/reactions: ~100/hour
- Queue actions when limit reached

### Error Handling
- Detect Facebook error messages
- Handle session expiration
- Retry transient failures
- Graceful degradation for unavailable features
- Detailed error logging

### Anti-Detection
- Random delays between actions (2-5 seconds)
- Human-like mouse movements
- Realistic typing speeds
- Vary action patterns
- Rotate user agents
- Maintain realistic session duration

### Performance Optimization
- Cache user profiles (5-minute TTL)
- Cache group/page info (10-minute TTL)
- Reuse browser tabs
- Parallel action processing
- Lazy load media content
- Implement request batching

### Multi-Account Support
- Separate browser contexts per account
- Isolated cookie storage
- Account-specific rate limiting
- Session rotation
- Concurrent account operations

## Technology Stack

- **API Framework**: FastAPI
- **Browser Automation**: Playwright
- **Async Runtime**: asyncio
- **Validation**: Pydantic v2
- **Caching**: Redis (optional) or in-memory
- **Queue**: asyncio.Queue or Celery (for distributed)
- **Database**: SQLite/PostgreSQL (for selector storage, rate limiting)
- **Logging**: structlog
- **Configuration**: python-dotenv

## Security Considerations

- Store credentials encrypted
- Encrypt cookie files with account-specific keys
- Implement API key authentication
- Rate limit API endpoints
- Validate all inputs
- Sanitize extracted data
- Implement CORS properly
- Use HTTPS in production
- Audit log all actions
- Implement account lockout on suspicious activity
- Secure cookie storage directory (chmod 600)
- Never commit cookie files to git (.gitignore)

## Documentation Requirements

**README.md Must Include**:

1. **Installation & Setup**
   - Dependencies and installation steps
   - Playwright browser installation
   - Configuration file setup
   - Multi-account setup instructions

2. **API Documentation**
   - All endpoint descriptions
   - Request/response examples
   - Authentication methods
   - Rate limits per endpoint

3. **Technical Issues & Solutions**
   - Document every issue encountered during development
   - Include error messages and symptoms
   - Provide detailed solutions and workarounds
   - Add code snippets showing fixes
   - Reference specific files and line numbers

4. **Session Management**
   - Cookie persistence explanation
   - Remember Me feature details
   - Session validation process
   - Cookie refresh strategy
   - Troubleshooting login issues

5. **Troubleshooting Guide**
   - Common errors and solutions
   - Facebook detection issues
   - Rate limiting problems
   - Selector failures
   - Cookie expiration handling

6. **Development Notes**
   - Facebook UI changes and adaptations
   - Selector updates history
   - Performance optimizations applied
   - Anti-detection techniques used

7. **Security Best Practices**
   - Credential storage
   - Cookie file protection
   - API key management
   - .gitignore requirements

8. **Testing**
   - How to run tests
   - Test account setup
   - CI/CD considerations

**Documentation Update Process**:
- Update README.md immediately when issues are discovered
- Document the problem, investigation, and solution
- Include timestamps and Facebook UI version if relevant
- Add examples and code snippets
- Keep a changelog section for major updates

**Example Issue Documentation Format**:
```markdown
### Issue: Cookie Dialog Blocking Login (2026-01-25)
**Problem**: Facebook's cookie consent dialog overlay intercepted login button clicks.
**Error**: `subtree intercepts pointer events`
**Solution**: Use JavaScript to remove dialog and click button directly.
**Code**: See `src/scraper/session_manager.py:login()` lines 45-50
**Status**: Resolved
```

## Deployment

- Docker container with Playwright
- Environment-based configuration
- Health check endpoints
- Metrics collection (Prometheus)
- Horizontal scaling support
- Load balancer for multiple instances
- Separate worker processes for queue
- Persistent volume for cookie storage
- Backup strategy for cookies directory
- Cookie encryption key management

## File Structure

```
facebook-api/
├── .env                          # Credentials (gitignored)
├── .env.example                  # Template
├── .gitignore                    # Includes cookies/, .env, *.log
├── README.md                     # Comprehensive documentation
├── requirements.txt
├── cookies/                      # Per-account cookies (gitignored)
│   ├── account1.json
│   └── account2.json
├── src/
│   ├── api/
│   │   ├── main.py
│   │   ├── models.py
│   │   └── routes/
│   │       ├── profile.py
│   │       ├── friends.py
│   │       ├── posts.py
│   │       ├── groups.py
│   │       ├── pages.py
│   │       ├── messages.py
│   │       ├── events.py
│   │       ├── marketplace.py
│   │       └── stories.py
│   ├── services/
│   │   ├── profile_service.py
│   │   ├── friends_service.py
│   │   ├── posts_service.py
│   │   ├── groups_service.py
│   │   ├── pages_service.py
│   │   ├── messaging_service.py
│   │   ├── events_service.py
│   │   ├── marketplace_service.py
│   │   └── stories_service.py
│   ├── core/
│   │   ├── session_manager.py    # Enhanced with cookie persistence
│   │   ├── navigator.py
│   │   ├── extractor.py
│   │   ├── action_handler.py
│   │   ├── cache_manager.py
│   │   └── queue_manager.py
│   └── utils/
│       ├── selectors.py
│       ├── encryption.py
│       └── validators.py
├── config/
│   └── settings.py
└── tests/
    ├── test_session.py
    ├── test_services.py
    └── test_api.py
```

## Testing Strategy

- Unit tests for each service
- Integration tests for API endpoints
- E2E tests with real Facebook account
- Mock Facebook responses for CI/CD
- Selector validation tests
- Rate limiting tests
- Multi-account tests

## Monitoring & Observability

- Request/response logging
- Action success/failure metrics
- Rate limit tracking
- Session health monitoring
- Selector failure alerts
- Performance metrics
- Error rate tracking
