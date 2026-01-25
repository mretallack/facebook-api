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

## Common Problems from Other Projects & Solutions

Based on research of existing Facebook automation projects and anti-bot systems, the following issues are commonly encountered:

### 1. Detection & Blocking Issues

**Problem**: Facebook's multi-layered anti-bot detection system
- TLS fingerprinting detection
- JavaScript execution pattern analysis
- Browser fingerprint inconsistencies
- Timing regularity detection
- Request header analysis
- Navigator.webdriver flag exposure

**Solutions Implemented**:
```python
# Use undetected-playwright or patchright
# Patches Runtime.enable to avoid detection
# Removes navigator.webdriver flag

# Browser launch with anti-detection
browser = await playwright.chromium.launch(
    headless=False,  # Headless mode more easily detected
    args=[
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--no-sandbox',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process'
    ]
)

# Consistent browser fingerprinting
context = await browser.new_context(
    viewport={'width': 1920, 'height': 1080},
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    locale='en-US',
    timezone_id='America/New_York',
    permissions=['geolocation'],
    geolocation={'latitude': 40.7128, 'longitude': -74.0060},
    color_scheme='light'
)

# Hide automation flags
await page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
    window.chrome = {runtime: {}};
""")
```

**References**:
- [undetected-playwright-python](https://github.com/kaliiiiiiiiii/undetected-playwright-python)
- [playwright-with-fingerprints](https://github.com/CheshireCaat/playwright-with-fingerprints)

### 2. Account Suspension & Rate Limiting

**Problem**: Aggressive automation triggers account bans
- Rapid posting (>10 posts/hour)
- Mass messaging (>50 messages/hour)
- Excessive friend requests (>20/hour)
- Posting too close together
- Using third-party bots without approval

**Solutions**:
```python
class RateLimiter:
    """Enforce Facebook rate limits per action type"""
    
    limits = {
        'friend_request': {'max': 15, 'window': 3600},  # 15/hour (conservative)
        'post': {'max': 8, 'window': 3600},             # 8/hour
        'message': {'max': 40, 'window': 3600},         # 40/hour
        'like': {'max': 80, 'window': 3600},            # 80/hour
        'comment': {'max': 30, 'window': 3600},         # 30/hour
        'group_join': {'max': 5, 'window': 3600},       # 5/hour
    }
    
    async def check_limit(self, action_type: str, account_id: str):
        """Check if action is within rate limit"""
        # Track actions in time window
        # Block if limit exceeded
        # Add exponential backoff on repeated limits
```

**Account Warming Strategy**:
```python
# New accounts need gradual activity increase
warming_schedule = {
    'day_1': {'posts': 2, 'likes': 10, 'friend_requests': 3},
    'day_2': {'posts': 3, 'likes': 15, 'friend_requests': 5},
    'day_3': {'posts': 5, 'likes': 25, 'friend_requests': 8},
    # ... gradually increase over 2 weeks
}
```

**References**:
- 40% of marketers report ad account restrictions (Social Media Examiner 2022)
- Facebook disables accounts for automation tool use without warning

### 3. Dynamic Content & Selector Changes

**Problem**: Facebook frequently changes CSS selectors and page structure
- Selectors break without notice
- Dynamic CSS class names
- A/B testing different UIs
- Regional UI variations

**Solutions Already Implemented**:
- Selector database with version history
- Multiple fallback selectors
- Automatic selector validation
- UI change detection with screenshots
- Auto-discovery of new selectors

### 4. Login & Session Management

**Problem**: Frequent re-authentication required
- Sessions expire quickly
- 2FA challenges
- Security checkpoints
- "Suspicious activity" blocks

**Solutions Already Implemented**:
- Cookie persistence with "Remember Me"
- Session validation before actions
- Proactive cookie refresh (25-day cycle)
- Per-account cookie storage

**Additional Recommendations**:
```python
# Handle security checkpoints
async def handle_checkpoint(page: Page):
    """Detect and handle Facebook security checkpoints"""
    checkpoint_selectors = [
        'text="Security Check"',
        'text="Confirm Your Identity"',
        'text="Please Review Your Recent Activity"'
    ]
    
    for selector in checkpoint_selectors:
        if await page.query_selector(selector):
            logger.warning("security_checkpoint_detected")
            # Pause automation
            # Send alert for manual intervention
            # Save checkpoint screenshot
            await page.screenshot(path=f"logs/checkpoint_{timestamp}.png")
            raise SecurityCheckpointError("Manual intervention required")
```

### 5. CAPTCHA Challenges

**Problem**: Facebook shows CAPTCHAs to suspected bots
- Image recognition CAPTCHAs
- reCAPTCHA v2/v3
- hCaptcha

**Solutions**:
```python
# Detection
async def detect_captcha(page: Page) -> bool:
    """Check if CAPTCHA is present"""
    captcha_indicators = [
        'iframe[src*="recaptcha"]',
        'iframe[src*="hcaptcha"]',
        '[data-testid="captcha"]',
        'text="Please complete the security check"'
    ]
    
    for selector in captcha_indicators:
        if await page.query_selector(selector):
            return True
    return False

# Handling options:
# 1. Manual solving (pause and alert)
# 2. CAPTCHA solving service (2captcha, anticaptcha)
# 3. Reduce activity to avoid CAPTCHAs
```

### 6. Proxy & IP Management

**Problem**: Single IP makes detection easier
- IP reputation scoring
- Geographic inconsistencies
- Concurrent session limits per IP

**Solutions**:
```python
# Residential proxy rotation
class ProxyManager:
    """Manage proxy rotation per account"""
    
    async def get_proxy(self, account_id: str) -> str:
        """Get sticky residential proxy for account"""
        # Use same proxy for same account (consistency)
        # Rotate only on session refresh
        # Match proxy location to account location
        
    async def validate_proxy(self, proxy: str) -> bool:
        """Check proxy is working and not blacklisted"""
```

**Recommendations**:
- Use residential proxies (not datacenter)
- Sticky sessions (same IP per account)
- Match proxy location to account profile
- Rotate proxies only on new sessions

### 7. Memory Leaks & Resource Management

**Problem**: Long-running scrapers consume excessive memory
- Browser contexts not closed
- Page objects accumulate
- Event listeners not removed

**Solutions**:
```python
# Proper cleanup
async def cleanup_session(account_id: str):
    """Clean up browser resources"""
    if account_id in pages:
        await pages[account_id].close()
        del pages[account_id]
    
    if account_id in contexts:
        await contexts[account_id].close()
        del contexts[account_id]
    
    # Force garbage collection
    import gc
    gc.collect()

# Resource limits
MAX_PAGES_PER_CONTEXT = 5
MAX_CONTEXTS_PER_BROWSER = 10
```

### 8. Error Handling & Recovery

**Problem**: Cascading failures when errors occur
- Network timeouts
- Element not found
- Navigation failures
- Session expiration

**Solutions**:
```python
class RetryStrategy:
    """Intelligent retry with exponential backoff"""
    
    async def execute_with_retry(self, func, max_retries=3):
        """Execute function with retry logic"""
        for attempt in range(max_retries):
            try:
                return await func()
            except TimeoutError:
                if attempt < max_retries - 1:
                    wait = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(wait)
                else:
                    raise
            except ElementNotFoundError:
                # Selector might have changed
                await self.refresh_selectors()
                if attempt < max_retries - 1:
                    continue
                else:
                    raise
```

### 9. Content Extraction Challenges

**Problem**: Extracting clean data from dynamic content
- Lazy-loaded content
- Infinite scroll
- Duplicate posts
- Incomplete data

**Solutions**:
```python
async def extract_with_scroll(page: Page, limit: int):
    """Extract content with intelligent scrolling"""
    seen_ids = set()
    posts = []
    no_new_content_count = 0
    
    while len(posts) < limit and no_new_content_count < 3:
        # Scroll
        await page.evaluate('window.scrollBy(0, window.innerHeight)')
        await asyncio.sleep(random.uniform(2, 4))
        
        # Extract visible posts
        new_posts = await extract_visible_posts(page)
        
        # Deduplicate
        new_unique = [p for p in new_posts if p['id'] not in seen_ids]
        
        if not new_unique:
            no_new_content_count += 1
        else:
            no_new_content_count = 0
            posts.extend(new_unique)
            seen_ids.update(p['id'] for p in new_unique)
```

### 10. Monitoring & Adaptation

**Problem**: Fighting yesterday's war - not adapting to changes
- No visibility into failures
- Manual detection of issues
- Reactive rather than proactive

**Solutions Already Implemented**:
- Comprehensive logging with screenshots
- Selector validation health checks
- UI change detection
- Automatic alerts
- Metrics tracking

## Technology Recommendations

Based on research, use these libraries:

1. **undetected-playwright** or **patchright** (fork)
   - Patches Runtime.enable
   - Removes automation flags
   - Better than standard Playwright for Facebook

2. **playwright-stealth** (if not using undetected)
   - 17 evasion modules
   - Browser fingerprint modification
   - Automation signature masking

3. **Residential Proxy Services**
   - Bright Data, Smartproxy, Oxylabs
   - Avoid datacenter proxies
   - Use sticky sessions

4. **CAPTCHA Solving** (optional)
   - 2captcha, anticaptcha
   - Only as fallback
   - Better to avoid CAPTCHAs entirely

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

**Selector Management System**:

```python
class SelectorManager:
    """Manages Facebook selectors with fallbacks and auto-discovery"""
    
    selectors: Dict[str, List[str]]  # Multiple fallback selectors per element
    selector_history: Dict[str, List[SelectorVersion]]  # Track changes over time
    
    async def get_selector(element_name: str) -> str:
        """Try selectors in order until one works"""
        
    async def validate_selectors() -> Dict[str, bool]:
        """Check which selectors still work"""
        
    async def discover_selector(element_name: str, screenshot: bool = True) -> str:
        """Auto-discover new selector when old ones fail"""
        
    async def log_selector_failure(element_name: str, failed_selector: str):
        """Log failed selector with screenshot and page HTML"""
```

**Selector Database** (`src/utils/selectors.json`):
```json
{
  "login_button": {
    "selectors": [
      "button[name='login']",
      "button[data-testid='royal_login_button']",
      "button[type='submit'][value='1']"
    ],
    "last_validated": "2026-01-25T17:00:00Z",
    "last_updated": "2026-01-25T17:00:00Z",
    "version": "2.0"
  },
  "friend_request_button": {
    "selectors": [
      "button[aria-label='Add Friend']",
      "div[aria-label='Add Friend']",
      "a[href*='add_friend']"
    ],
    "last_validated": "2026-01-25T17:00:00Z",
    "version": "1.5"
  }
}
```

**UI Change Detection**:

```python
class UIChangeDetector:
    """Detects when Facebook UI has changed"""
    
    async def take_baseline_screenshot(page_name: str):
        """Capture reference screenshot of page"""
        
    async def detect_layout_change(page_name: str) -> bool:
        """Compare current page to baseline"""
        
    async def log_ui_change(page_name: str, diff_image: str):
        """Log UI change with visual diff"""
```

**Comprehensive Logging System**:

```python
# Structured logging with context
import structlog

logger = structlog.get_logger()

# Log levels:
# - DEBUG: Selector attempts, navigation steps
# - INFO: Successful actions, API requests
# - WARNING: Selector fallbacks, retries
# - ERROR: Failed actions, UI changes
# - CRITICAL: System failures, session loss

# Log format:
{
  "timestamp": "2026-01-25T17:00:00Z",
  "level": "ERROR",
  "event": "selector_failed",
  "element": "friend_request_button",
  "selector": "button[aria-label='Add Friend']",
  "page_url": "https://facebook.com/profile/123",
  "screenshot": "logs/screenshots/error_20260125_170000.png",
  "html_dump": "logs/html/error_20260125_170000.html",
  "account_id": "account1",
  "action": "send_friend_request",
  "retry_count": 3
}
```

**Automatic Diagnostics on Failure**:

```python
async def handle_selector_failure(element_name: str, page: Page):
    """Comprehensive diagnostics when selector fails"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Take screenshot
    screenshot_path = f"logs/screenshots/{element_name}_{timestamp}.png"
    await page.screenshot(path=screenshot_path, full_page=True)
    
    # 2. Save page HTML
    html_path = f"logs/html/{element_name}_{timestamp}.html"
    html = await page.content()
    with open(html_path, 'w') as f:
        f.write(html)
    
    # 3. Save page structure
    structure_path = f"logs/structure/{element_name}_{timestamp}.json"
    structure = await page.evaluate("""
        () => {
            const getStructure = (el, depth = 0) => {
                if (depth > 5) return null;
                return {
                    tag: el.tagName,
                    id: el.id,
                    classes: Array.from(el.classList),
                    attributes: Array.from(el.attributes).map(a => ({
                        name: a.name,
                        value: a.value
                    })),
                    children: Array.from(el.children).map(c => getStructure(c, depth + 1))
                };
            };
            return getStructure(document.body);
        }
    """)
    with open(structure_path, 'w') as f:
        json.dump(structure, f, indent=2)
    
    # 4. Log all buttons/clickable elements
    clickables_path = f"logs/clickables/{element_name}_{timestamp}.json"
    clickables = await page.evaluate("""
        () => {
            const elements = document.querySelectorAll('button, a, [role="button"], [onclick]');
            return Array.from(elements).map(el => ({
                tag: el.tagName,
                text: el.innerText?.substring(0, 100),
                aria_label: el.getAttribute('aria-label'),
                data_testid: el.getAttribute('data-testid'),
                name: el.getAttribute('name'),
                id: el.id,
                classes: Array.from(el.classList)
            }));
        }
    """)
    with open(clickables_path, 'w') as f:
        json.dump(clickables, f, indent=2)
    
    # 5. Log to structured logger
    logger.error(
        "selector_failed",
        element=element_name,
        screenshot=screenshot_path,
        html=html_path,
        structure=structure_path,
        clickables=clickables_path,
        url=page.url
    )
    
    # 6. Send alert (optional)
    await send_alert(f"Selector failed: {element_name}")
```

**Selector Auto-Discovery**:

```python
async def discover_new_selector(element_name: str, page: Page, 
                                 expected_text: str = None) -> Optional[str]:
    """Attempt to find new selector based on context"""
    
    # Try to find by text content
    if expected_text:
        candidates = await page.query_selector_all(f'text="{expected_text}"')
        if candidates:
            # Generate selector for first match
            selector = await page.evaluate("""
                (el) => {
                    // Generate unique selector
                    if (el.id) return `#${el.id}`;
                    if (el.getAttribute('data-testid')) 
                        return `[data-testid="${el.getAttribute('data-testid')}"]`;
                    if (el.getAttribute('aria-label'))
                        return `[aria-label="${el.getAttribute('aria-label')}"]`;
                    return null;
                }
            """, candidates[0])
            
            if selector:
                logger.info("discovered_new_selector", 
                           element=element_name, 
                           selector=selector)
                return selector
    
    return None
```

**Health Check & Monitoring**:

```python
# Add to API endpoints
@app.get("/health/selectors")
async def check_selectors():
    """Validate all selectors are working"""
    results = await selector_manager.validate_selectors()
    failing = [k for k, v in results.items() if not v]
    
    return {
        "status": "healthy" if not failing else "degraded",
        "total_selectors": len(results),
        "failing_selectors": failing,
        "last_check": datetime.now().isoformat()
    }

@app.get("/health/ui-changes")
async def check_ui_changes():
    """Check for detected UI changes"""
    changes = await ui_detector.get_recent_changes()
    
    return {
        "changes_detected": len(changes),
        "changes": changes
    }
```

**Alerting System**:

```python
class AlertManager:
    """Send alerts when critical issues occur"""
    
    async def send_alert(message: str, severity: str, context: Dict):
        """Send alert via configured channels"""
        # Email, Slack, webhook, etc.
        
    async def alert_selector_failure(element: str, screenshot: str):
        """Alert when selector fails after all retries"""
        
    async def alert_ui_change(page: str, diff_image: str):
        """Alert when significant UI change detected"""
        
    async def alert_rate_limit(account: str):
        """Alert when rate limited by Facebook"""
```

**Logs Directory Structure**:
```
logs/
├── app.log                    # Main application log
├── selectors.log              # Selector-specific events
├── ui_changes.log             # UI change detection log
├── screenshots/               # Error screenshots
│   ├── friend_request_20260125_170000.png
│   └── post_create_20260125_170100.png
├── html/                      # Page HTML dumps
│   ├── friend_request_20260125_170000.html
│   └── post_create_20260125_170100.html
├── structure/                 # DOM structure dumps
│   └── friend_request_20260125_170000.json
├── clickables/                # Clickable elements catalog
│   └── friend_request_20260125_170000.json
└── baselines/                 # Reference screenshots
    ├── profile_page.png
    ├── feed_page.png
    └── groups_page.png
```

**Configuration** (`.env`):
```
# Logging
LOG_LEVEL=INFO
LOG_DIR=logs
ENABLE_SCREENSHOTS=true
ENABLE_HTML_DUMPS=true
ENABLE_STRUCTURE_DUMPS=true

# Monitoring
ENABLE_UI_CHANGE_DETECTION=true
ENABLE_SELECTOR_VALIDATION=true
SELECTOR_VALIDATION_INTERVAL=3600  # seconds

# Alerting
ALERT_EMAIL=admin@example.com
ALERT_WEBHOOK=https://hooks.slack.com/...
ALERT_ON_SELECTOR_FAILURE=true
ALERT_ON_UI_CHANGE=true
```

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
- Document selector changes in selector database
- Include screenshots of UI changes
- Reference log files for debugging

**Example Issue Documentation Format**:
```markdown
### Issue: Cookie Dialog Blocking Login (2026-01-25)
**Problem**: Facebook's cookie consent dialog overlay intercepted login button clicks.
**Error**: `subtree intercepts pointer events`
**Solution**: Use JavaScript to remove dialog and click button directly.
**Code**: See `src/scraper/session_manager.py:login()` lines 45-50
**Logs**: `logs/screenshots/login_20260125_170000.png`
**Status**: Resolved

### Issue: Friend Request Button Selector Changed (2026-01-26)
**Problem**: Selector `button[aria-label='Add Friend']` no longer works
**Detection**: Automatic selector validation detected failure
**Investigation**: 
  - Screenshot: `logs/screenshots/friend_request_20260126_100000.png`
  - HTML dump: `logs/html/friend_request_20260126_100000.html`
  - Clickables: `logs/clickables/friend_request_20260126_100000.json`
**New Selector**: `div[aria-label='Add Friend'][role='button']`
**Solution**: Updated `src/utils/selectors.json` with new selector as primary
**Code**: Selector database updated, old selector kept as fallback
**Status**: Resolved
```

**Selector Change Documentation**:
```markdown
### Selector History: friend_request_button

| Date | Version | Selector | Status | Notes |
|------|---------|----------|--------|-------|
| 2026-01-20 | 1.0 | `button[aria-label='Add Friend']` | Deprecated | Stopped working 2026-01-26 |
| 2026-01-26 | 1.5 | `div[aria-label='Add Friend'][role='button']` | Active | Current working selector |
| 2026-01-26 | 1.5 | `a[href*='add_friend']` | Fallback | Alternative selector |
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
│   │   ├── queue_manager.py
│   │   ├── selector_manager.py   # NEW: Selector management
│   │   ├── ui_detector.py        # NEW: UI change detection
│   │   └── alert_manager.py      # NEW: Alerting system
│   └── utils/
│       ├── selectors.py
│       ├── selectors.json         # NEW: Selector database
│       ├── encryption.py
│       └── validators.py
├── config/
│   └── settings.py
├── logs/                          # NEW: Comprehensive logging
│   ├── app.log
│   ├── selectors.log
│   ├── ui_changes.log
│   ├── screenshots/
│   ├── html/
│   ├── structure/
│   ├── clickables/
│   └── baselines/
└── tests/
    ├── test_session.py
    ├── test_services.py
    ├── test_selectors.py         # NEW: Selector tests
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

- Request/response logging with structured format
- Action success/failure metrics
- Rate limit tracking per account
- Session health monitoring
- Selector failure alerts with screenshots
- UI change detection with visual diffs
- Error rate tracking by endpoint
- Performance metrics (response times)
- Automatic diagnostics on failure:
  - Full page screenshots
  - HTML dumps
  - DOM structure exports
  - Clickable elements catalog
- Health check endpoints:
  - `/health/selectors` - Validate all selectors
  - `/health/ui-changes` - Check for UI changes
  - `/health/sessions` - Check session status
- Alerting system for critical issues:
  - Selector failures after retries
  - Significant UI changes detected
  - Rate limiting events
  - Session expiration
- Log retention and rotation
- Metrics dashboard (Grafana/Prometheus)
- Selector version history tracking
