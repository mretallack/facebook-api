# Facebook Automation API

A comprehensive REST API for automating Facebook interactions using Playwright. Supports posts, friends, groups, messages, events, pages, marketplace, and stories.

## ⚠️ How Facebook Renders Posts

### Current Implementation: DOM Extraction ✅

The scraper uses **DOM extraction during scrolling** which is the most reliable method:

**Why it works:**
- Extracts from rendered HTML that browser displays
- Handles Facebook's virtual scrolling (posts added/removed dynamically)
- Gets 10-16 posts per profile (typical for timeline view)
- Filters out comments using link analysis (`comment_id` detection)

**Typical Results:**
```bash
$ python test_friend_posts.py
Total posts: 10
1. A lovely new year's day...
2. Great pic love Santa...
3. Wonder what three sons do for you...
```

### Why You Can't Get "All" Posts

Facebook's profile timeline is **intentionally limited**:

1. **Virtual Scrolling**: Only loads ~20 posts max, removes old ones
2. **Privacy Design**: Full post history requires Graph API access
3. **Timeline vs Archive**: Timeline shows recent activity, not complete history
4. **Rate Limiting**: Aggressive scrolling triggers anti-bot detection

### Alternative: GraphQL API (Not Recommended)

Facebook uses GraphQL (`POST /api/graphql/`) but:

❌ **Timeline queries not exposed** - Profile page doesn't trigger post-loading GraphQL
❌ **Requires authentication tokens** - `fb_dtsg` from session
❌ **API changes frequently** - `doc_id` values change with updates
❌ **Anti-bot detection** - Direct API calls get blocked

**GraphQL Request Example:**
```
POST https://www.facebook.com/api/graphql/
fb_dtsg=NAfvScOYsQLzCdKX5aAd3go8WvMQiaq1LRz6ptJpGn-V40LPdNBc-tw:2:1769418649
doc_id=25044355701909548
variables={"count":15,"environment":"MAIN_SURFACE"}
```

The data is URL-encoded form data (not encrypted), but the profile timeline doesn't use GraphQL for post loading - posts are embedded in initial page load and rendered by JavaScript.

### Performance Metrics
- Initial load: 2 articles
- After 30 scrolls: 10-16 unique posts
- GraphQL requests: ~28 per session
- Time per scroll: ~1.5 seconds
- Total scrape time: ~45 seconds

## Features

- ✅ **Multi-Account Support** - Manage multiple Facebook accounts simultaneously
- ✅ **Profile Management** - Get/update profiles, upload pictures
- ✅ **Friends Management** - Search, send/accept requests, unfriend, block
- ✅ **Posts Management** - Create, delete, like, comment, share posts
- ✅ **Groups Management** - Search, join/leave, post to groups
- ✅ **Messaging** - Send messages, get conversations
- ✅ **Events** - Search events, RSVP
- ✅ **Pages** - Search, like, post to pages
- ✅ **Marketplace** - Search listings, create listings
- ✅ **Stories** - View, create, delete stories
- ✅ **GraphQL Interception** - Extract data from Facebook's GraphQL API
- ✅ **Rate Limiting** - Automatic rate limiting per account
- ✅ **Caching** - In-memory caching with TTL
- ✅ **Queue Management** - Priority-based async task queue
- ✅ **Session Keep-Alive** - Automatic session refresh to prevent expiration

## Installation

```bash
# Clone repository
git clone <repository-url>
cd facebook

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create .env file
cp .env.example .env
# Edit .env with your credentials
```

## Configuration

Create `.env` file:

```env
FB_EMAIL=your_email@example.com
FB_PASSWORD=your_password
HEADLESS=true
COOKIES_FILE=cookies/default.json
```

## Quick Start

```bash
# Start the API server
python3 -m src.api.main

# API will be available at http://localhost:8000
```

## API Documentation

### Authentication

```bash
POST /auth
{
  "email": "your_email@example.com",
  "password": "your_password"
}
```

### Profile

```bash
# Get your profile
GET /profile/me

# Update profile
PUT /profile/me
{
  "bio": "New bio text"
}

# Upload profile picture
POST /profile/picture
Content-Type: multipart/form-data
file: <image_file>
```

### Friends

```bash
# Search people
GET /friends/search?query=john

# Send friend request
POST /friends/request
{
  "profile_url": "https://facebook.com/user123"
}

# Accept friend request
POST /friends/accept/{request_id}

# Unfriend
DELETE /friends/{profile_url}
```

### Posts

```bash
# Get feed
GET /posts/feed?limit=10

# Create post
POST /posts/create
{
  "content": "Hello world!",
  "privacy": "public"
}

# Like post
POST /posts/{post_id}/like

# Comment on post
POST /posts/{post_id}/comment
{
  "comment": "Great post!"
}

# Delete post
DELETE /posts/{post_id}
```

### Groups

```bash
# Search groups
GET /groups/search?query=python

# Get group details
GET /groups/{group_id}

# Join group
POST /groups/{group_id}/join

# Post to group
POST /groups/{group_id}/post
{
  "content": "Hello group!"
}
```

### Messages

```bash
# Get conversations
GET /messages/conversations

# Get messages from conversation
GET /messages/{conversation_id}

# Send message
POST /messages/send/{user_id}
{
  "message": "Hello!"
}
```

### Events

```bash
# Search events
GET /events/search?query=concert

# Get event details
GET /events/{event_id}

# RSVP to event
POST /events/{event_id}/rsvp
{
  "response": "going"  # or "interested", "not_going"
}
```

### Pages

```bash
# Search pages
GET /pages/search?query=tech

# Get page details
GET /pages/{page_id}

# Like page
POST /pages/{page_id}/like

# Post to page (requires admin)
POST /pages/{page_id}/post
{
  "content": "New update!"
}
```

### Marketplace

```bash
# Search listings
GET /marketplace/search?query=laptop

# Get listing details
GET /marketplace/{listing_id}

# Create listing
POST /marketplace/create
{
  "title": "Laptop for sale",
  "price": "500",
  "description": "Great condition",
  "category": "electronics"
}
```

### Stories

```bash
# Get stories
GET /stories/feed

# Create text story
POST /stories/create
{
  "text": "Hello from my story!"
}

# Create photo story
POST /stories/create
Content-Type: multipart/form-data
image: <image_file>

# Delete story
DELETE /stories/{story_id}
```

### Search

```bash
# Search people
GET /search/people?query=john

# Get profile details
GET /search/profile?url=https://facebook.com/user123
```

## Multi-Account Usage

```python
from src.scraper.session_manager import SessionManager

# Create session manager
session = SessionManager()

# Start account 1
await session.start("account1")
await session.login("email1@example.com", "password1", "account1")

# Start account 2
await session.start("account2")
await session.login("email2@example.com", "password2", "account2")

# Switch between accounts
page1 = await session.switch_account("account1")
page2 = await session.switch_account("account2")

# Get specific account page
page = session.get_page("account1")
```

## Rate Limiting

The API automatically enforces rate limits per account:

- Friend requests: 15/hour
- Posts: 8/hour
- Messages: 40/hour
- Likes: 80/hour
- Comments: 30/hour

## Caching

Responses are cached with TTL:

```python
from src.core.cache_manager import cache

# Set cache
await cache.set("key", "value", ttl=300)  # 5 minutes

# Get cache
value = await cache.get("key")

# Delete cache
await cache.delete("key")

# Get stats
stats = cache.stats()
```

## Queue Management

Priority-based async task queue:

```python
from src.core.queue_manager import queue, Priority

# Enqueue task
task_id = await queue.enqueue(
    "task1",
    my_function,
    args=("arg1",),
    priority=Priority.HIGH,
    account_id="account1"
)

# Start queue
await queue.start()

# Get task status
status = queue.get_status(task_id)

# Get stats
stats = queue.stats()
```

## GraphQL Interception

The API intercepts Facebook's GraphQL responses for more reliable data extraction:

```python
from src.core.graphql_extractor import GraphQLExtractor

extractor = GraphQLExtractor()
await extractor.intercept_responses(page)

# Navigate to page
await page.goto(url)

# Extract profile data
profile = extractor.extract_profile()

# Save responses for debugging
extractor.save_responses('/tmp/graphql.json')
```

## Architecture

```
facebook-api/
├── src/
│   ├── api/              # FastAPI routes and models
│   ├── core/             # Core components
│   │   ├── cache_manager.py
│   │   ├── queue_manager.py
│   │   └── graphql_extractor.py
│   ├── scraper/          # Playwright automation
│   │   ├── session_manager.py
│   │   ├── post_extractor.py
│   │   └── search_service.py
│   └── services/         # Business logic
│       ├── events_service.py
│       ├── pages_service.py
│       ├── marketplace_service.py
│       └── stories_service.py
├── config/               # Configuration
├── cookies/              # Session cookies (per account)
└── tests/                # Tests
```

## Security

- Store credentials in `.env` file (never commit)
- Cookies are stored per account in `cookies/` directory
- Add `cookies/` and `.env` to `.gitignore`
- Use HTTPS in production
- Implement API key authentication for production use

## Rate Limits & Best Practices

1. **Respect Facebook's Terms of Service**
2. **Use reasonable delays between actions**
3. **Don't exceed rate limits**
4. **Use residential proxies for production**
5. **Implement proper error handling**
6. **Monitor for security checkpoints**
7. **Keep cookies fresh (re-login every 25 days)**

## Troubleshooting

### Login Issues

- Check credentials in `.env`
- Delete old cookies: `rm cookies/*.json`
- Disable headless mode: `HEADLESS=false`
- Check for security checkpoints

### Rate Limiting

- Reduce action frequency
- Use multiple accounts
- Implement longer delays

### Selector Failures

- Facebook UI changes frequently
- Check logs for failed selectors
- Update selectors in code
- Use GraphQL interception when possible

## Development

```bash
# Run tests
python3 tests/test_core_infrastructure.py

# Start with debug logging
DEBUG=true python3 -m src.api.main

# Check API health
curl http://localhost:8000/health
```

## API Health Check

```bash
GET /health

Response:
{
  "status": "ok",
  "browser_ready": true
}
```

## Limitations

- **Login Required**: Most features require authentication
- **Privacy Settings**: Can only access public data or data visible to logged-in user
- **Rate Limits**: Facebook enforces strict rate limits
- **UI Changes**: Facebook frequently changes UI, requiring selector updates
- **GraphQL Restrictions**: Profile data limited for logged-out users

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

MIT License

## Disclaimer

This tool is for educational purposes only. Use responsibly and in accordance with Facebook's Terms of Service. The authors are not responsible for any misuse or violations.

## Support

For issues and questions:
- Check documentation
- Review logs in `/tmp/facebook-api.log`
- Check GraphQL responses in `/tmp/fb_profile_graphql.json`
- Open an issue on GitHub

## Changelog

### v1.0.0 (2026-01-26)
- Initial release
- Multi-account support
- Complete Facebook automation API
- GraphQL interception
- Rate limiting and caching
- Queue management
- Events, Pages, Marketplace, Stories support
