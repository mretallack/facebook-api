# Facebook Scraper API - Design

## Architecture Overview

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────────────────┐
│      REST API Server            │
│  (FastAPI)                      │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│   Scraper Service               │
│  - Session Manager              │
│  - Post Extractor               │
│  - Content Classifier           │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│   Playwright Browser            │
│  - Headless Chromium            │
│  - Cookie/Session Storage       │
└─────────────────────────────────┘
```

## Component Design

### 1. API Server
**Technology**: FastAPI
**Responsibilities**:
- Handle HTTP requests
- Validate input parameters (automatic with Pydantic)
- Route requests to scraper service
- Format and return JSON responses
- Auto-generate OpenAPI documentation

**Endpoints**:
```
GET /posts
  Query params:
    - limit: int (default: 20)
    - offset: int (default: 0)
    - exclude_ads: bool (default: false)
    - exclude_suggested: bool (default: false)
    - post_type: str (optional: text|photo|video|link|mixed)

GET /health
  Returns: API and browser status

POST /auth
  Body: { email: str, password: str }
  Returns: Authentication status
```

### 2. Scraper Service

**SessionManager**:
- Manages Playwright browser instance
- Handles Facebook authentication
- Stores and restores cookies
- Monitors session validity

**PostExtractor**:
- Navigates to Facebook feed
- Scrolls to load posts
- Extracts post elements using selectors
- Parses post data into structured format

**ContentClassifier**:
- Identifies sponsored posts (looks for "Sponsored" label)
- Identifies suggested posts (looks for "Suggested for you")
- Classifies post types based on content structure
- Applies filters based on API parameters

### 3. Data Models

**Pydantic Models**:
```python
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
```

## Sequence Diagram

```
Client          API Server      Scraper         Playwright
  │                 │              │                 │
  │─GET /posts─────>│              │                 │
  │                 │              │                 │
  │                 │─extract()───>│                 │
  │                 │              │                 │
  │                 │              │─navigate()─────>│
  │                 │              │                 │
  │                 │              │<─page loaded────│
  │                 │              │                 │
  │                 │              │─scroll & wait──>│
  │                 │              │                 │
  │                 │              │<─elements ready─│
  │                 │              │                 │
  │                 │              │─extract data───>│
  │                 │              │                 │
  │                 │              │<─raw HTML───────│
  │                 │              │                 │
  │                 │<─parsed posts│                 │
  │                 │              │                 │
  │                 │─filter()────>│                 │
  │                 │              │                 │
  │                 │<─filtered────│                 │
  │                 │              │                 │
  │<─JSON response──│              │                 │
```

## Implementation Considerations

### Facebook Selectors
Facebook frequently changes CSS selectors. Strategy:
- Use multiple fallback selectors
- Identify elements by aria-labels and data attributes
- Log selector failures for monitoring
- Implement selector update mechanism

### Anti-Detection
- Use realistic user agent
- Random delays between actions (1-3 seconds)
- Mimic human scrolling patterns
- Maintain persistent browser context
- Avoid headless detection flags

### Session Persistence
- Store cookies in encrypted file
- Restore session on startup
- Validate session before each scrape
- Re-authenticate only when necessary

### Error Handling
- Browser crashes: Restart and retry
- Network errors: Exponential backoff
- Element not found: Log and skip
- Rate limiting: Increase delays
- Authentication failures: Return 401 to client

### Performance Optimization
- Cache extracted posts (5-minute TTL)
- Reuse browser instance across requests
- Lazy load images/videos
- Implement request queuing for concurrent requests

## Technology Stack

- **Runtime**: Python 3.11+
- **Browser Automation**: Playwright for Python
- **API Framework**: FastAPI
- **Async Runtime**: asyncio (built-in)
- **Storage**: File-based (cookies, cache)
- **Logging**: Python logging module or structlog
- **Validation**: Pydantic (included with FastAPI)

## Security Considerations

- Store credentials securely (environment variables or python-dotenv)
- Never log sensitive data (passwords, tokens)
- Implement rate limiting with slowapi
- Validate all input parameters (automatic with Pydantic)
- Use HTTPS in production
- Implement API authentication (API keys or JWT with fastapi-jwt-auth)

## Deployment

- Run as standalone Python service with uvicorn
- Docker container with Playwright dependencies
- Environment variables for configuration (.env file)
- Health check endpoint for monitoring
- Install Playwright browsers: `playwright install chromium`
