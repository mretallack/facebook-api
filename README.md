# Facebook Automation API

A Playwright-based REST API for extracting Facebook posts using GraphQL interception. Successfully extracts photo posts from friend profiles with full content, images, and timestamps.

## 🎉 Production Ready - Photo Post Extraction

### Current Status (2026-01-29)

✅ **Working Features:**
- Extracts 4-6 photo posts per friend profile
- Dual extraction: Initial DOM + GraphQL responses
- Preserves chronological order
- Instant cache retrieval (3ms vs 90s scraping)
- 15-minute auto-refresh in Android app
- Full image URLs from Facebook CDN
- Partial timestamp extraction

### How It Works

The scraper uses a **dual-source extraction strategy** discovered through investigation:

1. **Initial DOM Extraction**: Facebook server-renders the newest 2-3 posts in the initial HTML
2. **GraphQL Interception**: Captures older posts from `/api/graphql/` responses during scrolling
3. **Photo Filtering**: Only fetches photo posts (most reliable, text posts often timeout)
4. **Order Preservation**: Uses list instead of set to maintain chronological order

**Key Insight**: Facebook uses two delivery paths:
- Static posts embedded in initial page load (newest posts)
- Dynamic posts fetched via GraphQL on scroll (older posts)

### Architecture

```
User Request → Check Cache (3ms) → Return if fresh
                    ↓ (if stale)
            Scrape Profile:
              1. Load page (initial DOM)
              2. Extract photo links from DOM
              3. Scroll 15 times
              4. Intercept GraphQL responses
              5. Extract photo URLs from JSON
              6. Fetch first 6 photo posts
              7. Extract text + images + timestamps
              8. Store in SQLite cache
                    ↓
            Return posts (instant next time)
```

### Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Posts extracted | 4-6 | Per friend profile |
| Cache retrieval | 3ms | SQLite query |
| Fresh scrape | 90s | Full GraphQL + fetch |
| Success rate | 100% | For photo posts |
| Scroll iterations | 15 | Triggers GraphQL |
| Timeout per post | 30s | Graceful skip on failure |
| Cache TTL | 1 hour | Configurable |
| Auto-refresh | 15 min | Android app |

## Installation

```bash
# Install dependencies
pip install playwright
playwright install chromium

# Run standalone test
python3.12 test_new_feed.py

# Or test caching
python3.12 test_caching.py
```

## Quick Start

### Standalone Usage

```python
from playwright.async_api import async_playwright
from src.scraper.feed_aggregator import FeedAggregator
import json

async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context()
    
    # Load cookies
    with open('cookies/default.json') as f:
        await context.add_cookies(json.load(f)['cookies'])
    
    page = await context.new_page()
    
    # Extract posts
    aggregator = FeedAggregator(page)
    friends = [{'name': 'Friend Name', 'url': 'https://www.facebook.com/username'}]
    posts = await aggregator.get_feed(friends, [], limit=10)
    
    print(f"Got {len(posts)} posts")
    for post in posts:
        print(f"- {post['content'][:50]}")
        print(f"  {post['url']}")
    
    await browser.close()
```

### API Server

```bash
# Start server
python3.12 -m src.api.main

# Server runs on http://localhost:8000
```

### API Endpoints

```bash
# Get cached feed (instant)
GET /posts/feed?limit=5

# Force fresh scrape
GET /posts/feed?limit=5&fresh=true

# Refresh cache (background)
POST /posts/feed/refresh?limit=10
```

## Configuration

### Cookies Setup

Create `cookies/default.json` with your Facebook session:

```json
{
  "cookies": [
    {"name": "c_user", "value": "...", "domain": ".facebook.com"},
    {"name": "xs", "value": "...", "domain": ".facebook.com"}
  ]
}
```

Export cookies from your browser using a cookie extension.

### Cache Configuration

Edit `config/settings.py`:

```python
CACHE_ENABLED = True
CACHE_DB_PATH = "cache.db"
CACHE_TTL_HOURS = 1  # How long cache is valid
```

## Android App

The Android app provides a native interface with automatic background refresh.

### Features

- Instant feed loading from cache
- Auto-refresh every 15 minutes
- Pull-to-refresh for manual updates
- Material Design UI
- Image loading with Coil

### Installation

```bash
cd androidapp
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk
```

### Configuration

Update `util/Constants.kt`:

```kotlin
const val API_BASE_URL = "http://your-server:8000"
const val POSTS_PAGE_SIZE = 20
```

## Technical Deep Dive

### Problem 1: Missing Newest Posts

**Issue**: GraphQL interception only captured older posts, missing the 2-3 newest posts.

**Investigation**: 
- Checked initial DOM - found only 3 old photo links
- Searched page source - found newest post text embedded
- Realized Facebook server-renders newest posts in HTML

**Solution**: Extract from both sources:
```python
# 1. Extract from initial DOM
dom_links = await page.query_selector_all('a[href*="/photo/"]')

# 2. Intercept GraphQL during scroll
page.on('response', handle_graphql_response)
await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
```

### Problem 2: Lost Chronological Order

**Issue**: Posts appeared in random order, not chronological.

**Root Cause**: Using `set()` for deduplication lost insertion order.

**Solution**: Changed to list with manual deduplication:
```python
# Before: self.post_urls = set()
# After: self.post_urls = []

if url not in self.post_urls:
    self.post_urls.append(url)  # Preserves order
```

### Problem 3: Text Posts Timeout

**Issue**: Text posts (pfbid URLs) took >30s to load or returned no content.

**Root Cause**: Different HTML structure, possibly privacy-restricted.

**Solution**: Filter to photo posts only:
```python
photo_urls = [url for url in unique_urls if '/photo/' in url]
for url in photo_urls[:6]:  # Only fetch photos
    content = await self._fetch_post(url)
```

### Problem 4: Group Posts Included

**Issue**: Posts to groups appeared in results.

**Solution**: Filter by URL pattern:
```python
if 'set=gm.' in url:  # gm = group media
    continue  # Skip group posts
if 'set=a.' in url:  # a = album (profile posts)
    self.post_urls.append(url)  # Include
```

### Problem 5: Comment URLs Extracted

**Issue**: Comment links extracted instead of post links.

**Solution**: Filter by URL parameters:
```python
if 'comment_id=' in url or 'reply_comment_id=' in url:
    continue  # Skip comments
```

### Problem 6: Timestamp Extraction

**Issue**: Timestamps not found with initial selectors.

**Partial Solution**: Multiple selector fallbacks:
```python
# Try data-utime attribute (Unix timestamp)
time_elem = await page.query_selector('abbr[data-utime]')
if time_elem:
    utime = await time_elem.get_attribute('data-utime')
    timestamp = datetime.fromtimestamp(int(utime))

# Fallback to text
else:
    timestamp = await time_elem.inner_text()  # "1d", "2h", etc.
```

**Status**: Works for ~25% of posts. Facebook's timestamp rendering is inconsistent.

## Test Cases

### Test 1: Basic Feed Extraction
```bash
python3.12 test_new_feed.py
```
**Expected**: 4 posts from Mark Retallack's profile  
**Result**: ✅ Pass

### Test 2: Caching Performance
```bash
python3.12 test_caching.py
```
**Expected**: <5ms cache retrieval  
**Result**: ✅ 3ms average

### Test 3: API Method
```bash
python3.12 test_api_method.py
```
**Expected**: Same results as Test 1, formatted as API response  
**Result**: ✅ Pass

### Test 4: Order Preservation
**Expected Order**:
1. Kiro post (newest)
2. A spot of digging
3. Melted cheese
4. Ben is somewhere

**Result**: ✅ Order preserved

## Troubleshooting

### No Posts Returned

**Check cookies:**
```bash
# Cookies expire after ~30 days
cat cookies/default.json
```

**Check profile URL:**
```bash
# Must be accessible to your account
curl -I https://www.facebook.com/username
```

**Check cache:**
```bash
sqlite3 cache.db "SELECT COUNT(*) FROM cached_posts;"
```

### Timeout Errors

Some posts timeout (30s limit) and are automatically skipped. This is normal for:
- Text posts (different HTML structure)
- Privacy-restricted posts
- Slow-loading pages

**Solution**: The scraper continues and returns successful posts.

### Session Expired

**Symptoms**: 0 posts returned, login page in logs

**Solution**: Re-export cookies from browser
```bash
# Delete old cookies
rm cookies/default.json

# Export new cookies from browser
# Update cookies/default.json
```

### Wrong Post Order

**Check**: Are you getting posts from GraphQL only?

**Solution**: Ensure DOM extraction runs first:
```python
# This should appear in logs:
# "Extracting posts from initial DOM..."
```

### Cache Not Working

**Check server logs:**
```bash
tail -f /tmp/facebook_api.log | grep Cache
```

**Manually refresh:**
```bash
curl -X POST "http://localhost:8000/posts/feed/refresh?limit=10"
```

**Check database:**
```bash
sqlite3 cache.db "SELECT content, fetched_at FROM cached_posts ORDER BY fetched_at DESC LIMIT 5;"
```

## Limitations

### Current Limitations

1. **Text posts**: Not extracted (timeout/structure issues)
2. **Timestamps**: Only ~25% success rate
3. **Post limit**: 4-6 posts per profile (Facebook's virtual scrolling)
4. **Private posts**: Only accessible posts are extracted
5. **Rate limiting**: ~1 profile per 90 seconds (scraping time)

### Facebook Restrictions

- **Login required**: Must have valid session cookies
- **Privacy settings**: Can only access posts visible to your account
- **Virtual scrolling**: Facebook limits posts in DOM to ~20 at a time
- **Anti-bot detection**: Aggressive scrolling may trigger rate limiting
- **Session expiry**: Cookies expire after ~30 days

### Technical Constraints

- **Headless browser**: Requires Chromium (~200MB)
- **Memory usage**: ~500MB per browser instance
- **Concurrent scraping**: Limited by browser instances
- **GraphQL changes**: Facebook may change API structure

## Production Deployment

### Server Requirements

- **CPU**: 2+ cores
- **RAM**: 2GB minimum (4GB recommended)
- **Disk**: 1GB for browser + cache
- **Network**: Stable connection to Facebook

### Recommended Setup

```bash
# Use systemd service
sudo cp facebook-api.service /etc/systemd/system/
sudo systemctl enable facebook-api
sudo systemctl start facebook-api

# Monitor logs
journalctl -u facebook-api -f
```

### Scaling Considerations

- **Multiple accounts**: Rotate cookies to avoid rate limits
- **Distributed caching**: Use Redis instead of SQLite
- **Load balancing**: Multiple API instances behind nginx
- **Background workers**: Separate scraping from API serving

## Security

- Store cookies in `.env` file (never commit)
- Use HTTPS in production
- Implement API key authentication
- Rate limit API endpoints
- Monitor for suspicious activity
- Rotate cookies regularly

## Future Improvements

### Planned Features

- [ ] Text post extraction (better selectors)
- [ ] Reliable timestamp extraction
- [ ] Video post support
- [ ] Comments extraction
- [ ] Reactions count
- [ ] Multiple friends in single request
- [ ] WebSocket for real-time updates

### Known Issues

- Text posts timeout (30s)
- Timestamps only work for 25% of posts
- API server session conflicts (use standalone scripts)
- Cache scheduler disabled (conflicts with scraping)

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
- Check troubleshooting section
- Review logs in `/tmp/facebook_api.log`
- Check test scripts: `test_new_feed.py`, `test_caching.py`
- Open an issue on GitHub

## Changelog

### v2.0.0 (2026-01-29)
- ✅ Dual extraction: DOM + GraphQL
- ✅ Photo-only filtering
- ✅ Order preservation
- ✅ Improved caching (3ms retrieval)
- ✅ Android app with 15-min auto-refresh
- ✅ Partial timestamp extraction
- ✅ 4-6 posts per profile consistently

### v1.0.0 (2026-01-26)
- Initial release
- GraphQL interception only
- Basic caching
- 2-3 posts per profile

### How It Works

The API uses **GraphQL response interception** to extract post URLs directly from Facebook's internal API responses:

1. **Navigate to profile** - Load friend's Facebook profile page
2. **Intercept GraphQL** - Capture `/api/graphql/` responses during page scroll
3. **Extract URLs** - Parse JSON responses to find `permalink_url` fields
4. **Fetch posts** - Navigate to each post URL and extract content
5. **Return data** - Structured JSON with text, images, author info

**Key Advantages**:
- ✅ No DOM scraping needed for post discovery
- ✅ Gets actual post URLs (not comments)
- ✅ Works with friend profiles
- ✅ Extracts full content and images
- ✅ More reliable than HTML parsing

### Test Results

**Test Command**:
```bash
python3.12 test_new_feed.py
```

**Output**:
```
✓ Got 4 posts

1. Mark Retallack
   Text: Emily making chrIstmas cards. Glitter everyware....
   URL: https://www.facebook.com/photo/?fbid=10152535112956167&set=a.10152164014711167

2. Mark Retallack
   Text: My next project.......
   URL: https://www.facebook.com/photo/?fbid=10162056399516167&set=a.10152164014711167

3. Mark Retallack
   Text: Home Assistant Santa tracker is up....
   URL: https://www.facebook.com/photo/?fbid=10162272323516167&set=a.10152164014711167

4. Mark Retallack
   Text: Ben is somewhere.......
   URL: https://www.facebook.com/photo/?fbid=10162281064726167&set=a.10152164014711167

✓ Test passed: 4 posts extracted
```

**JSON Response Format**:
```json
{
  "count": 4,
  "posts": [
    {
      "id": "https://www.facebook.com/photo/?fbid=10162281064726167&set=a.10152164014711167",
      "author": {
        "name": "Mark Retallack",
        "profile_url": "https://www.facebook.com/mark.retallack"
      },
      "content": "Ben is somewhere....",
      "url": "https://www.facebook.com/photo/?fbid=10162281064726167&set=a.10152164014711167",
      "timestamp": "",
      "image_url": "https://scontent-man2-1.xx.fbcdn.net/v/t39.30808-6/605699689_10162281064736167_947720682300811337_n.jpg?..."
    }
  ]
}
```

### Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Posts extracted | 2-4 | Per friend profile |
| Scroll iterations | 10 | Triggers GraphQL requests |
| Timeout per post | 30s | Graceful error handling |
| Success rate | ~70% | Some posts timeout, skipped |
| Total time | ~45s | For one profile |

### Technical Implementation

**GraphQL Interception**:
```python
async def handle_response(response):
    if '/api/graphql/' in response.url and response.status == 200:
        text = await response.text()
        for line in text.split('\n'):
            if line.strip():
                data = json.loads(line)
                self._extract_urls(data)  # Find permalink_url fields

page.on('response', handle_response)
await page.goto(profile_url)

# Scroll to trigger more GraphQL requests
for _ in range(10):
    await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
    await asyncio.sleep(2)
```

**URL Filtering**:
- ✅ Includes: `/posts/`, `/photo/` URLs
- ❌ Excludes: URLs with `comment_id=` or `reply_comment_id=`
- ❌ Excludes: Duplicate URLs

**Content Extraction**:
```python
# For photo posts
text = await page.get_attribute('meta[name="description"]', 'content')
img = await page.query_selector('img[src*="scontent"]')
image_url = await img.get_attribute('src')

# For text posts
article = await page.query_selector('[role="article"]')
text_elems = await article.query_selector_all('[dir="auto"]')
```

---

## 🎉 BREAKTHROUGH: Post IDs Found in GraphQL Responses!

### Discovery: Feed Data IS Transferred

**Method**: Captured complete network traffic using Playwright's HAR recording.

**Result**: Post URLs are embedded in GraphQL responses!

```bash
$ python capture_network_traffic.py

Total network requests: 242
GraphQL responses: 4
  - Response 3: 1.3MB (contains feed data!)
  - Response 4: 1.7MB (contains feed data!)

Extracted post URLs: 10 unique posts
  https://www.facebook.com/mark.retallack/posts/pfbid02FwR4zNcYyXhhXzEBR8fXe9sqnpWDNomh3b4waoEALfDMj3KbM5EPqrLDc4RAS49El
  https://www.facebook.com/photo/?fbid=10162259269131167&set=a.10152164014711167
```

### ✅ Works on Profile Pages Too!

**Tested on friend's profile**: `https://www.facebook.com/mark.retallack`

```bash
$ python test_profile_graphql.py

Loading profile: https://www.facebook.com/mark.retallack
Scrolling to load posts...
✓ Extracted 16 unique post URLs

Sample URLs:
  https://www.facebook.com/mark.retallack/posts/pfbid02FwR4zNcYyXhhXzEBR8fXe9sqnpWDNomh3b4waoEALfDMj3KbM5EPqrLDc4RAS49El
  https://www.facebook.com/photo/?fbid=10162259269131167&set=a.10152164014711167
```

### End-to-End Test Results

**Test**: Extract posts from friend's profile and fetch full content

```bash
$ python test_end_to_end.py

STEP 1: Extract post URLs from profile
✓ Extracted 12 unique post URLs

STEP 2: Fetch posts and extract content
[1/5] Fetching post...
  ✓ Author: Unknown
  ✓ Text: A lovely new year's day...
  ✓ Images: 0
  ✓ Comments: 0

STEP 3: Results Summary
✓ Profile URLs extracted: 12
✓ Posts fetched: 3
✓ Total images: 0
✓ Total comments: 0

✅ End-to-end test PASSED
```

**What Works**:
- ✅ Extract post URLs from friend's profile via GraphQL interception
- ✅ Access posts directly using extracted URLs
- ✅ Extract post text content
- ⚠️ Images/comments need better selectors (but posts are accessible)

### How It Works

1. **GraphQL Response Structure**:
```json
{
  "data": {
    "viewer": {
      "news_feed": {
        "edges": [{
          "node": {
            "permalink_url": "https://www.facebook.com/mark.retallack/posts/pfbid...",
            "comet_sections": {...}
          }
        }]
      }
    }
  }
}
```

2. **Data is NOT encrypted** - Plain JSON in GraphQL responses
3. **Multiple posts per response** - Each scroll triggers new GraphQL request
4. **Post URLs use pfbid format** - New Facebook ID format
5. **Works on both feed and profile pages**

### Implementation Strategy

**New Approach**: GraphQL Response Interception
1. Load profile page
2. Intercept GraphQL responses
3. Parse JSON to extract `permalink_url` fields
4. Access posts directly using URLs
5. Extract text, images, comments from rendered post

**Advantages**:
- ✅ Gets actual post URLs (not comments)
- ✅ Works with friend profiles
- ✅ No DOM parsing needed for discovery
- ✅ More reliable than scraping rendered HTML
- ✅ Bypasses profile timeline limitation

**Code Example**:
```python
async def handle_response(response):
    if 'graphql' in response.url:
        body = await response.body()
        text = body.decode('utf-8')
        
        # Parse NDJSON format
        for line in text.split('\n'):
            if line.strip():
                data = json.loads(line)
                # Extract permalink_url from nested structure
                post_urls = extract_post_urls(data)
```

---

## Investigation: Finding Post IDs from Friends Feed

### Attempted Approach: Friends Feed Scraping

**Goal**: Extract post IDs from friends feed (`/?sk=h_chr`) to enable direct post access.

**Test Results**:
```bash
$ python test_friends_feed_deep.py

Loading friends feed (/?sk=h_chr)...
Page title: (1) Facebook
✗ Feed container not found
Scroll 0-15: 0 articles
Total articles: 0
```

**Finding**: Friends feed does NOT load articles via standard scraping.

### Network Traffic Analysis

**GraphQL Requests Captured**: 14 responses
- Notification data: ✓
- User settings: ✓
- Feed/story data: ✗

**Post IDs Found**: 0 (only user ID: 61586881541300)

**Evidence**:
```json
{
  "data": {
    "viewer": {
      "id": "61586881541300",
      "notifications": [...]
    }
  }
}
```

### Why Friends Feed Doesn't Work

1. **No Article Elements**: `[role="article"]` selector returns 0 results
2. **No Feed Container**: `[role="feed"]` not found on page
3. **GraphQL Doesn't Return Posts**: Captured responses contain notifications/settings, not feed data
4. **Possible Reasons**:
   - Friends feed requires JavaScript interaction (click/hover)
   - Feed loads via different mechanism (WebSocket, long-polling)
   - Privacy settings block programmatic access
   - Facebook detects headless browser

### Alternative Discovery: Main Feed Analysis

**Main Feed** (`/`) shows 2 articles but:
- No post URLs in article links
- No author information
- No post text
- Likely placeholder/loading elements

**Screenshot Evidence**:
- Main feed: 672KB (has some content)
- Friends feed: Similar size but 0 articles

---

## ⚠️ CRITICAL FINDING: Profile Timelines Show Comments, Not Posts

### Evidence-Based Discovery

**What the scraper actually extracts**: Comments that the user made on other people's posts, NOT the user's own posts.

**Proof**:
```bash
$ python test_different_urls.py

Main profile (https://www.facebook.com/mark.retallack):
  Articles found: 3
  Has comment_id: True  ← This indicates a COMMENT
  Has post link: True   ← Link to the post being commented on
  Text: "Chris Retallack..."  ← Comment text

Posts tab (https://www.facebook.com/mark.retallack/posts):
  Articles found: 0  ← Privacy restricted, returns empty
```

**Screenshot Evidence**:
- Main profile: 1.2MB (shows comments)
- Posts tab: 50KB (empty/blocked)

### ✅ Direct Post Access WORKS (If You Have the Post ID)

**Discovery**: You CAN access individual posts directly if you know the post ID:

```bash
$ python test_direct_post_access.py

Testing: https://www.facebook.com/photo/?fbid=10160189910976167&set=a.10153685248131167
✓ Page contains 'Mark Retallack'
✓ Image viewer found
✓ Content accessible
```

**Post URL Formats That Work**:
```
https://www.facebook.com/photo/?fbid=POST_ID&set=ALBUM_ID
https://www.facebook.com/USERNAME/posts/POST_ID
https://www.facebook.com/permalink.php?story_fbid=POST_ID&id=USER_ID
```

**The Challenge**: Finding post IDs without scraping the profile
- Profile timeline doesn't show post links (only comments)
- Posts tab is privacy-restricted
- Need alternative method to discover post IDs

**Possible Solutions** (Tested):
1. **News Feed Scraping** - Extract post IDs from your own feed
   - **Status**: ❌ Tested - Main feed shows 2 articles with no post URLs
   - **Issue**: Feed doesn't load properly via Playwright
   
2. **Friends Feed** (`/?sk=h_chr`) - Chronological feed of friends' posts
   - **Status**: ❌ Tested - Returns 0 articles
   - **Issue**: Feed container not found, no articles load
   
3. **Notification Scraping** - Get post IDs from notifications
   - **Status**: ⏳ Not tested yet
   - **Potential**: Notifications may contain post references
   
4. **Graph API** - Use official API to get post IDs
   - **Status**: ✅ Works but requires app approval + OAuth
   - **Limitation**: Rate limited, requires user permissions
   
5. **Browser Extension** - Run in real browser with extension
   - **Status**: ⏳ Not tested
   - **Potential**: Could capture post IDs as user browses
   
6. **Historical Database** - Build database over time
   - **Status**: ⏳ Requires initial post ID source
   - **Limitation**: Doesn't solve discovery problem

**Current Blocker**: Cannot reliably extract post IDs from any Facebook page via Playwright:
- Profile timelines: Show comments, not posts
- Posts tab: Privacy restricted (0 articles)
- Main feed: Articles load but contain no post URLs
- Friends feed: No articles load at all (0 results)
- GraphQL responses: Contain notifications/settings, not feed data

**Root Cause**: Facebook's feed loading may require real browser interaction or uses mechanisms incompatible with headless scraping.

### Why This Happens

Facebook's profile timeline (`/username`) shows **recent activity**:
- ✅ Comments the user made
- ✅ Posts the user was tagged in
- ✅ Reactions the user made
- ❌ NOT the user's own posts

To see actual posts, you need:
1. **Direct post URL** - **Works if you have the post ID** ✅
2. **Posts tab** (`/username/posts`) - **Privacy blocked** for friends ❌
3. **Graph API** - Requires app approval + user OAuth consent
4. **News Feed** - Shows posts that appear in your feed

---

## Technical Deep Dive: How Facebook Renders Posts

### Executive Summary

Facebook uses **client-side JavaScript rendering with virtual scrolling**. Posts are NOT in the initial HTML source - they're created dynamically by JavaScript after the page loads. The only reliable way to extract posts is **DOM extraction during scrolling**, which is what this scraper implements.

**Key Finding**: Profile timelines yield 10-16 posts maximum due to Facebook's virtual scrolling design, not scraper limitations.

---

## Evidence-Based Analysis

### 1. Initial Page Load Analysis

**Test**: View page source vs rendered DOM
```bash
# Initial HTML size
curl -s 'https://www.facebook.com/mark.retallack' | wc -c
# Result: 2,482,784 chars

# Search for post text in source
grep -o "Do not give Ben J20" page_source.html
# Result: 0 matches (post text NOT in HTML source)

# Search in rendered DOM
page.query_selector_all('[role="article"]')
# Result: 2 articles initially, grows to 8 during scroll
```

**Evidence**: Post content exists only in rendered DOM, not in initial HTML.

---

### 2. Virtual Scrolling Behavior

**Test**: Monitor article count during scrolling
```python
Scroll 0:  2 articles in DOM
Scroll 5:  3 articles in DOM
Scroll 10: 5 articles in DOM
Scroll 15: 8 articles in DOM
Scroll 20: 2 articles in DOM  # Old posts REMOVED
```

**Evidence**: Facebook removes old `[role="article"]` elements as new ones load. Article count fluctuates, proving virtual scrolling.

**Technical Details**:
- DOM selector: `[role="article"]` for post containers
- Text selector: `[dir="auto"]` for post content
- Virtual DOM removes articles after ~10 new posts loaded
- Maximum ~20 posts in DOM at any time

---

### 3. GraphQL Network Analysis

**Test**: Intercept all network requests during profile load
```bash
# Captured GraphQL requests
x-fb-friendly-name: "CometNotificationsDropdownQuery"
x-fb-friendly-name: "fetchMWChatVideoAutoplaySettingQuery"
x-fb-friendly-name: "FBYRPTimeLimitsEnforcementQuery"
x-fb-friendly-name: "useMWEncryptedBackupsFetchBackupIdsV2Query"

# NO timeline/feed queries found
```

**Evidence**: Profile pages do NOT make GraphQL requests for timeline posts. GraphQL is only used for notifications, settings, and messenger features.

**GraphQL Request Structure** (for reference):
```http
POST https://www.facebook.com/api/graphql/
Content-Type: application/x-www-form-urlencoded

av=61586881541300
fb_dtsg=NAfvScOYsQLzCdKX5aAd3go8WvMQiaq1LRz6ptJpGn-V40LPdNBc-tw:2:1769418649
doc_id=25044355701909548
variables={"count":15,"environment":"MAIN_SURFACE","scale":1}
```

**Parameters**:
- `fb_dtsg`: CSRF token (extracted from page HTML, changes per session)
- `doc_id`: GraphQL query identifier (hardcoded, changes with Facebook updates)
- `variables`: JSON parameters (URL-encoded, not encrypted)
- `av`: Actor/user ID

**Response Format**: JSON (not encrypted)
```json
{
  "data": {
    "user": {
      "message_capabilities2_str": "107945653871116544",
      "id": "61586881541300"
    }
  }
}
```

---

### 4. Embedded JSON Analysis

**Test**: Search for JSON in page HTML
```bash
grep -o '"__bbox"' page.html | wc -l
# Result: 164 occurrences

# Extract and parse embedded JSON
# Found: Profile metadata, settings, UI state
# NOT found: Timeline posts
```

**Evidence**: Page HTML contains JSON for configuration and metadata, but NOT for timeline posts. Posts are rendered by JavaScript after page load.

---

### 5. DOM Extraction Success Rate

**Test**: Run scraper on multiple profiles
```bash
$ python test_friend_posts.py
Scroll 0: 0 posts so far
Scroll 5: 2 posts so far
Scroll 10: 4 posts so far
Scroll 15: 5 posts so far
Scroll 20: 8 posts so far

Total posts: 10
1. A lovely new year's day...
2. Great pic love Santa...
3. Wonder what three sons do for you...
```

**Evidence**: DOM extraction successfully retrieves 10-16 posts per profile, which matches Facebook's virtual scrolling limit.

**Implementation Details**:
```python
# Extract during scroll (not after)
for i in range(30):
    articles = await page.query_selector_all('[role="article"]')
    for article in articles:
        # Check if post or comment
        links = await article.query_selector_all('a[href*="facebook.com"]')
        has_comment_id = any('comment_id' in href for href in links)
        
        # Extract text
        text_elements = await article.query_selector_all('[dir="auto"]')
        text = max([await elem.inner_text() for elem in text_elements], key=len)
        
    await page.evaluate('window.scrollBy(0, 300)')
    await asyncio.sleep(1.5)
```

---

### 6. Comment vs Post Detection

**Test**: Analyze article link patterns
```python
# Comment indicators
'comment_id=123456' in href  # Has comment_id parameter

# Post indicators  
'/posts/' in href            # Direct post link
'/permalink/' in href        # Permalink to post

# Logic
if has_comment_id and not has_post_link:
    skip  # This is a comment on someone else's post
```

**Evidence**: Links containing `comment_id` without `/posts/` or `/permalink/` are comments, not posts. Scraper filters these out.

---

## Why You Can't Get "All" Posts

### Technical Limitations

1. **Virtual Scrolling Design**
   - Facebook intentionally limits to ~20 posts in DOM
   - Old posts removed as new ones load
   - No "load more" button - infinite scroll with removal

2. **Privacy Architecture**
   - Full post history requires Graph API with permissions
   - Profile timeline shows "recent activity" not "all posts"
   - `/username/posts` tab returns "content isn't available" for friends

3. **Anti-Bot Detection**
   - Aggressive scrolling triggers rate limiting
   - Session expires after ~5 minutes without activity
   - Headless browser detection (mitigated with stealth mode)

4. **API Access Requirements**
   - Official Graph API requires app approval
   - Needs user OAuth consent
   - Rate limited to 200 calls/hour
   - Only returns posts user has permission to see

---

## Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Initial articles | 2 | First render |
| Max articles in DOM | 8-10 | Before removal |
| Posts extracted | 10-16 | Per profile |
| Scroll iterations | 30 | Optimal balance |
| Time per scroll | 1.5s | Includes wait for render |
| Total scrape time | 45s | For one profile |
| GraphQL requests | 7-10 | None for timeline |
| Session duration | 3-5 min | Before refresh needed |

---

## Alternative Approaches Tested

### ❌ GraphQL Interception
**Attempted**: Intercept GraphQL responses for timeline data  
**Result**: Profile pages don't make timeline GraphQL requests  
**Evidence**: Only 7 GraphQL requests captured, all for notifications/settings

### ❌ JSON Extraction from HTML
**Attempted**: Parse embedded `<script type="application/json">` tags  
**Result**: No timeline data in embedded JSON  
**Evidence**: 164 JSON objects found, none contain posts

### ❌ Direct API Calls
**Attempted**: Replicate GraphQL requests with captured tokens  
**Result**: No timeline query endpoint identified  
**Evidence**: `doc_id` for timeline queries not exposed on profile pages

### ✅ DOM Extraction (Current Implementation)
**Method**: Extract from rendered DOM during scrolling  
**Result**: Successfully retrieves 10-16 posts per profile  
**Evidence**: Proven working in production

---

## Recommendations

### For Getting Actual Posts (Not Comments)

**The Reality**: You cannot scrape a friend's actual posts from their profile.

**Why**:
1. Profile timeline shows comments/activity, not posts
2. Posts tab (`/username/posts`) is privacy-restricted
3. Facebook intentionally blocks this for privacy

**Alternatives**:
1. **Official Graph API**
   - Requires Facebook app approval
   - User must grant OAuth permissions
   - Rate limited to 200 calls/hour
   - Only returns posts user has permission to see

2. **News Feed Scraping**
   - Scrape your own news feed (`/`)
   - Will show friends' posts that appear in your feed
   - Limited to what Facebook's algorithm shows you

3. **Group Posts**
   - If user posts in public groups
   - Scrape the group, not the profile

4. **Page Posts**
   - If user has a public Page
   - Pages are scrapable (not privacy-restricted)

### For Current Implementation (Comments)

The current scraper successfully extracts:
- ✅ Comments user made on posts
- ✅ 10-16 comments per profile
- ✅ Filters out nested replies
- ✅ Session keep-alive prevents expiration

If you need actual posts, you must use Facebook's official Graph API with proper permissions.

---

## Recommendations (Original)

### For Maximum Post Coverage
1. **Use official Graph API** - Requires app approval and user consent
2. **Scrape multiple sections** - Profile, photos, videos, tagged posts
3. **Historical scraping** - Run daily to build post history over time
4. **Multiple accounts** - Rotate to avoid rate limiting

### For Current Implementation
- ✅ DOM extraction is the correct approach
- ✅ 10-16 posts per profile is expected behavior
- ✅ Session keep-alive prevents expiration
- ✅ Comment filtering ensures quality data

---

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
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run standalone test
python3.12 test_new_feed.py

# Or test API method
python3.12 test_api_method.py
```

## API Usage (Standalone)

The feed extraction works standalone without the full API server:

```python
from playwright.async_api import async_playwright
from src.scraper.feed_aggregator import FeedAggregator
import json

async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context()
    
    # Load cookies
    with open('cookies/default.json') as f:
        await context.add_cookies(json.load(f)['cookies'])
    
    page = await context.new_page()
    
    # Extract posts
    aggregator = FeedAggregator(page)
    friends = [{'name': 'Friend Name', 'url': 'https://www.facebook.com/username'}]
    posts = await aggregator.get_feed(friends, [], limit=10)
    
    print(f"Got {len(posts)} posts")
    await browser.close()
```

## Configuration

Create `cookies/default.json` with your Facebook session cookies:
```json
{
  "cookies": [
    {"name": "c_user", "value": "...", "domain": ".facebook.com"},
    {"name": "xs", "value": "...", "domain": ".facebook.com"}
  ]
}
```

Export cookies from your browser using a cookie extension.

## Test Cases

### Test 1: Basic Feed Extraction
```bash
python3.12 test_new_feed.py
```
Expected: 2-4 posts from Mark Retallack's profile

### Test 2: API Method
```bash
python3.12 test_api_method.py
```
Expected: Same results as Test 1, formatted as API response

### Test 3: Multiple Friends
```python
friends = [
    {'name': 'Friend 1', 'url': 'https://www.facebook.com/friend1'},
    {'name': 'Friend 2', 'url': 'https://www.facebook.com/friend2'}
]
posts = await aggregator.get_feed(friends, [], limit=20)
```

## Troubleshooting

### No Posts Returned
- Check cookies are valid (not expired)
- Verify friend profile URL is correct
- Check friend's privacy settings (must be visible to you)
- Increase scroll iterations in `feed_aggregator.py`

### Timeout Errors
- Some posts may timeout (30s limit)
- These are automatically skipped
- Increase timeout in `_fetch_post()` if needed

### Session Expired
- Re-export cookies from browser
- Cookies expire after ~30 days
- Update `cookies/default.json`

---

## Original Documentation

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
