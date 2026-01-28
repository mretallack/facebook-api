# Facebook Scraping Technical Design

## Overview
This document details the technical findings and approaches for scraping Facebook profile posts.

## Key Findings

### 1. Profile Timeline Content

**What Profile Timelines Show**:
- Mix of user's own posts AND comments on those posts
- Each `[role="article"]` can be either a post or a comment
- Comments have `comment_id` in their links
- Posts have `/posts/` or `/permalink/` in their links
- **Privacy restriction**: `/username/posts` tab is NOT accessible to friends (shows "content isn't available")

**Detection Strategy**:
- Articles with ONLY `comment_id` links = comments (skip these)
- Articles with `/posts/` or `/permalink/` links = posts or post+comment (keep these)
- Extract all content as it represents activity on the friend's timeline

**Result**: Can extract 10-15 items per friend profile (mix of posts and comments)
**Problem**: Facebook sessions expire aggressively
- Cookies expire after navigation or inactivity
- Session lost after clicking cookie consent
- Requires continuous session maintenance

**Solution**: Session Keep-Alive Service
- Refresh session every 3-5 minutes
- Navigate to Facebook homepage periodically
- Re-authenticate automatically if session lost
- Implementation: `src/scraper/session_keeper.py`

### 2. Page Loading Architecture

#### Initial Page Load
- HTML contains only **2 article elements** initially
- Minimal post data in initial response
- Logged-in session confirmed by user data in HTML: `"ACCOUNT_ID":"61586881541300","USER_ID":"61586881541300","NAME":"Carrot Retallack"`

#### Dynamic Content Loading
- **Virtual Scrolling**: Facebook adds/removes posts from DOM dynamically
- **JavaScript-driven**: Posts loaded via GraphQL requests during scrolling
- **Article count fluctuates**: 2→3→5→8→2 as user scrolls
- **28 GraphQL requests** made during 30 scroll iterations
- Old posts removed from DOM to conserve memory

### 3. JSON Extraction Approach

**Status**: ❌ DOES NOT WORK

**Findings**:
- Facebook no longer uses `<script type="application/json">` tags on logged-in profile pages
- Found 186 JSON script tags but **0 contain post data**
- JSON scripts contain configuration/metadata, not posts
- Previous JSON extraction approach is obsolete

### 4. DOM Extraction Approach

**Status**: ✅ WORKS

**Method**:
1. Navigate to profile URL
2. Scroll page incrementally (30 iterations)
3. Extract posts from `[role="article"]` elements **during** scrolling
4. Track seen content to avoid duplicates
5. Continue until desired post count reached

**Results**:
- Successfully extracted **15 unique posts** from Mark Retallack's profile
- Posts are actual timeline posts by the profile owner
- Text extraction via `[dir="auto"]` elements with length > 20 chars

**Implementation**:
```python
# Extract during scrolling, not after
for scroll_num in range(30):
    articles = await page.query_selector_all('[role="article"]')
    
    for article in articles:
        # Extract text from [dir="auto"] elements
        dir_elems = await article.query_selector_all('[dir="auto"]')
        for elem in dir_elems:
            text = await elem.inner_text()
            if len(text) > 20:  # Substantial text
                # Store post if not seen before
                if text not in seen_content:
                    seen_content.add(text)
                    posts.append(post_data)
    
    # Scroll to load more
    await page.evaluate('window.scrollBy(0, window.innerHeight * 2)')
    await asyncio.sleep(1.5)
```

### 5. Post Structure

**Article Element Structure**:
```
[role="article"]
├── Author info
│   ├── Profile link with name
│   └── Timestamp link
├── Post content
│   └── [dir="auto"] text blocks
└── Media (images/videos)
    └── img[src*="scontent"]
```

**Post vs Comment Distinction**:
- Profile timeline shows posts BY the profile owner
- Comments from friends appear as text within posts
- Each `[role="article"]` represents one post
- Comments are nested within the post structure

### 6. Cookie Consent Handling

**Status**: ✅ RESOLVED

**Solution**: Use `[role="button"]` selector
```python
button = await page.query_selector('[role="button"]:has-text("Allow all cookies")')
if button:
    await button.click()
```

**Note**: Cookie consent button is a `[role="button"]` element, not a `<button>` tag

## Working Architecture

### Components

1. **SessionKeeper** (`src/scraper/session_keeper.py`)
   - Keeps session alive every 3-5 minutes
   - Auto-reauthenticates on session loss

2. **DOMPostExtractor** (`src/scraper/dom_extractor.py`)
   - Extracts posts from article elements
   - Handles text extraction from `[dir="auto"]` elements
   - Filters substantial content (>20 chars)

3. **FeedAggregator** (`src/scraper/feed_aggregator.py`)
   - Orchestrates profile scraping
   - Implements scroll-and-extract pattern
   - Tracks seen content for deduplication

4. **RetryDecorator** (`src/scraper/retry_decorator.py`)
   - Retries operations on session loss
   - Max 2 retries with re-authentication

## Scraping Flow

```
1. Load cookies from storage
2. Navigate to profile URL
3. Handle cookie consent if present
4. FOR each scroll iteration (30x):
   a. Query all [role="article"] elements
   b. Extract text from each article
   c. Store unique posts
   d. Scroll down 2x viewport height
   e. Wait 1.5 seconds for content to load
5. Return collected posts
```

## Performance Metrics

- **Initial articles**: 2
- **Articles after 30 scrolls**: 2-8 (fluctuates)
- **Unique posts extracted**: 15
- **GraphQL requests**: 28
- **Time per scroll**: ~1.5 seconds
- **Total scrape time**: ~45 seconds

## Limitations

1. **Privacy restrictions**: Can only see posts visible to logged-in friend
2. **Virtual scrolling**: Must extract during scrolling, not after
3. **Rate limiting**: Aggressive scrolling may trigger rate limits
4. **Session expiry**: Requires active session maintenance
5. **Post count**: Limited by what Facebook loads (typically 15-20 posts per profile)

## Alternative Approaches

### Graph API (Official)
**Status**: ✅ IMPLEMENTED (`src/api/routes/graph_api.py`)

**Pros**:
- Stable, documented, supported
- No session management issues
- Reliable data structure

**Cons**:
- Requires app registration
- Limited by API permissions
- User must grant access token

**Endpoints**:
- `/graph/me` - Get user profile
- `/graph/me/feed` - Get user feed

## Recommendations

1. **Primary approach**: DOM extraction with scroll-and-extract pattern
2. **Fallback**: Graph API for users who provide access tokens
3. **Session management**: Always use SessionKeeper for scraping
4. **Error handling**: Implement retry logic with re-authentication
5. **Rate limiting**: Add delays between profile scrapes (2-3 seconds minimum)

## Known Issues

1. **Author detection**: Current implementation returns "Unknown" for author
   - Need to extract from profile link or header
   - Selector: `a[role="link"] strong` or similar

2. **Timestamp extraction**: Not reliably captured
   - Need to find timestamp element within article
   - Selector: `a[href*="/posts/"] abbr` or similar

3. **Media extraction**: Images found but not consistently extracted
   - Selector: `img[src*="scontent"]`
   - Need to handle multiple images per post

## Next Steps

1. Improve author extraction from article elements
2. Add timestamp parsing
3. Enhance media (image/video) extraction
4. Implement comment extraction within posts
5. Add engagement metrics (likes, shares, comments count)
6. Test with different profile types (public, private, pages)
