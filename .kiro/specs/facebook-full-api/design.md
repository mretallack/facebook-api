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

**PreflightChecker**:
```python
class PreflightChecker:
    """Proactive detection of issues before they trigger on Facebook"""
    
    # Detection checks
    async def check_automation_flags() -> Dict[str, bool]
    async def check_fingerprint_consistency() -> bool
    async def check_rate_limits(account_id: str, action: str) -> bool
    async def check_session_health(account_id: str) -> bool
    async def check_proxy_reputation(proxy: str) -> Dict
    async def check_account_warmth(account_id: str) -> Dict
    async def check_suspicious_patterns(account_id: str) -> List[str]
    async def check_captcha_risk() -> float
    async def check_ip_consistency(account_id: str) -> bool
    async def check_timing_patterns() -> Dict
    
    # Comprehensive pre-action validation
    async def validate_action(account_id: str, action: Action) -> ValidationResult
    
    # Continuous monitoring
    async def monitor_session(account_id: str)
    async def get_risk_score(account_id: str) -> float
```

**PreflightChecker Implementation**:

```python
from dataclasses import dataclass
from typing import Dict, List, Optional
import time
import statistics

@dataclass
class ValidationResult:
    allowed: bool
    risk_score: float  # 0.0 (safe) to 1.0 (high risk)
    warnings: List[str]
    recommendations: List[str]
    should_delay: Optional[int]  # Seconds to wait before action

class PreflightChecker:
    """Proactive issue detection before Facebook triggers"""
    
    def __init__(self):
        self.action_history = {}  # Track actions per account
        self.timing_history = {}  # Track timing patterns
        self.session_starts = {}  # Track session durations
        
    async def validate_action(self, account_id: str, action: Action) -> ValidationResult:
        """Comprehensive pre-action validation"""
        warnings = []
        recommendations = []
        risk_score = 0.0
        should_delay = None
        
        # 1. Check automation flags
        flags = await self.check_automation_flags()
        if not flags['clean']:
            warnings.append("Automation flags detected")
            risk_score += 0.3
            recommendations.append("Restart browser with proper flags")
        
        # 2. Check rate limits
        if not await self.check_rate_limits(account_id, action.type):
            warnings.append(f"Rate limit approaching for {action.type}")
            risk_score += 0.4
            should_delay = self._calculate_delay(account_id, action.type)
            recommendations.append(f"Wait {should_delay}s before action")
        
        # 3. Check session health
        if not await self.check_session_health(account_id):
            warnings.append("Session may be expired or flagged")
            risk_score += 0.5
            recommendations.append("Validate and refresh session")
        
        # 4. Check suspicious patterns
        patterns = await self.check_suspicious_patterns(account_id)
        if patterns:
            warnings.extend(patterns)
            risk_score += 0.2 * len(patterns)
            recommendations.append("Vary action timing and patterns")
        
        # 5. Check timing patterns
        timing = await self.check_timing_patterns()
        if timing['too_regular']:
            warnings.append("Actions too regular - appears robotic")
            risk_score += 0.3
            recommendations.append("Add random delays between actions")
        
        # 6. Check account warmth
        warmth = await self.check_account_warmth(account_id)
        if warmth['too_aggressive']:
            warnings.append("Activity too aggressive for account age")
            risk_score += 0.4
            recommendations.append("Reduce activity frequency")
        
        # 7. Check CAPTCHA risk
        captcha_risk = await self.check_captcha_risk()
        if captcha_risk > 0.7:
            warnings.append("High CAPTCHA risk detected")
            risk_score += 0.3
            recommendations.append("Reduce activity and add delays")
        
        # 8. Check IP consistency
        if not await self.check_ip_consistency(account_id):
            warnings.append("IP location changed - may trigger security check")
            risk_score += 0.5
            recommendations.append("Use consistent proxy for this account")
        
        # 9. Check proxy reputation
        proxy_check = await self.check_proxy_reputation(self._get_current_proxy())
        if proxy_check['blacklisted']:
            warnings.append("Proxy IP is blacklisted")
            risk_score += 0.6
            recommendations.append("Switch to different proxy")
        
        # 10. Check fingerprint consistency
        if not await self.check_fingerprint_consistency():
            warnings.append("Browser fingerprint inconsistent")
            risk_score += 0.4
            recommendations.append("Maintain consistent browser profile")
        
        # Determine if action should be allowed
        allowed = risk_score < 0.7  # Block if risk too high
        
        return ValidationResult(
            allowed=allowed,
            risk_score=min(risk_score, 1.0),
            warnings=warnings,
            recommendations=recommendations,
            should_delay=should_delay
        )
    
    async def check_automation_flags(self) -> Dict[str, bool]:
        """Check for automation detection flags"""
        page = self._get_current_page()
        
        flags = await page.evaluate("""
            () => {
                return {
                    webdriver: navigator.webdriver,
                    chrome: !!window.chrome,
                    permissions: navigator.permissions !== undefined,
                    plugins: navigator.plugins.length > 0,
                    languages: navigator.languages.length > 0,
                    headless: navigator.userAgent.includes('Headless'),
                    automation: navigator.webdriver === true
                };
            }
        """)
        
        clean = (
            not flags['webdriver'] and
            flags['chrome'] and
            flags['plugins'] and
            not flags['headless']
        )
        
        return {'clean': clean, 'flags': flags}
    
    async def check_rate_limits(self, account_id: str, action_type: str) -> bool:
        """Check if action would exceed rate limits"""
        if account_id not in self.action_history:
            self.action_history[account_id] = {}
        
        if action_type not in self.action_history[account_id]:
            self.action_history[account_id][action_type] = []
        
        # Get actions in last hour
        now = time.time()
        recent_actions = [
            t for t in self.action_history[account_id][action_type]
            if now - t < 3600
        ]
        
        # Check against limits (80% threshold for warning)
        limits = {
            'friend_request': 12,  # 80% of 15
            'post': 6,             # 80% of 8
            'message': 32,         # 80% of 40
            'like': 64,            # 80% of 80
            'comment': 24,         # 80% of 30
        }
        
        limit = limits.get(action_type, 50)
        return len(recent_actions) < limit
    
    async def check_session_health(self, account_id: str) -> bool:
        """Check if session is healthy"""
        try:
            page = self._get_page(account_id)
            
            # Quick check: can we access a protected page?
            response = await page.goto("https://www.facebook.com/me", 
                                      wait_until="domcontentloaded",
                                      timeout=5000)
            
            # Check for login redirect
            if "login" in page.url:
                return False
            
            # Check for security checkpoint
            checkpoint = await page.query_selector('text="Security Check"')
            if checkpoint:
                return False
            
            return response.status == 200
        except:
            return False
    
    async def check_suspicious_patterns(self, account_id: str) -> List[str]:
        """Detect suspicious activity patterns"""
        patterns = []
        
        if account_id not in self.action_history:
            return patterns
        
        history = self.action_history[account_id]
        
        # Check for rapid-fire actions
        for action_type, timestamps in history.items():
            if len(timestamps) >= 3:
                recent = sorted(timestamps[-3:])
                intervals = [recent[i+1] - recent[i] for i in range(len(recent)-1)]
                
                # Too fast (< 2 seconds between actions)
                if any(interval < 2 for interval in intervals):
                    patterns.append(f"Actions too fast: {action_type}")
                
                # Too regular (same interval repeatedly)
                if len(set(round(i) for i in intervals)) == 1:
                    patterns.append(f"Actions too regular: {action_type}")
        
        # Check for burst activity
        now = time.time()
        recent_5min = sum(
            len([t for t in timestamps if now - t < 300])
            for timestamps in history.values()
        )
        
        if recent_5min > 20:
            patterns.append("Burst activity detected (>20 actions in 5 min)")
        
        # Check session duration
        if account_id in self.session_starts:
            duration = now - self.session_starts[account_id]
            total_actions = sum(len(timestamps) for timestamps in history.values())
            
            # Too many actions for session duration
            if duration < 600 and total_actions > 30:  # 30 actions in < 10 min
                patterns.append("Too many actions for session duration")
        
        return patterns
    
    async def check_timing_patterns(self) -> Dict:
        """Analyze timing patterns for regularity"""
        if not self.timing_history:
            return {'too_regular': False}
        
        # Get all action intervals
        all_intervals = []
        for account_history in self.timing_history.values():
            for timestamps in account_history.values():
                if len(timestamps) >= 2:
                    sorted_times = sorted(timestamps)
                    intervals = [sorted_times[i+1] - sorted_times[i] 
                               for i in range(len(sorted_times)-1)]
                    all_intervals.extend(intervals)
        
        if len(all_intervals) < 5:
            return {'too_regular': False}
        
        # Check variance
        mean = statistics.mean(all_intervals)
        stdev = statistics.stdev(all_intervals) if len(all_intervals) > 1 else 0
        
        # Low variance = too regular
        coefficient_of_variation = stdev / mean if mean > 0 else 0
        too_regular = coefficient_of_variation < 0.3  # Less than 30% variation
        
        return {
            'too_regular': too_regular,
            'mean_interval': mean,
            'stdev': stdev,
            'cv': coefficient_of_variation
        }
    
    async def check_account_warmth(self, account_id: str) -> Dict:
        """Check if account activity matches its age/history"""
        # Get account age (from database or config)
        account_age_days = self._get_account_age(account_id)
        
        # Get recent activity
        if account_id not in self.action_history:
            return {'too_aggressive': False}
        
        now = time.time()
        actions_today = sum(
            len([t for t in timestamps if now - t < 86400])
            for timestamps in self.action_history[account_id].values()
        )
        
        # Expected activity based on account age
        expected_max = {
            1: 10,    # Day 1: max 10 actions
            2: 20,    # Day 2: max 20 actions
            3: 30,    # Day 3: max 30 actions
            7: 50,    # Week 1: max 50 actions
            14: 100,  # Week 2: max 100 actions
            30: 200,  # Month 1: max 200 actions
        }
        
        max_allowed = 200  # Default for mature accounts
        for days, limit in sorted(expected_max.items()):
            if account_age_days <= days:
                max_allowed = limit
                break
        
        too_aggressive = actions_today > max_allowed
        
        return {
            'too_aggressive': too_aggressive,
            'actions_today': actions_today,
            'max_allowed': max_allowed,
            'account_age_days': account_age_days
        }
    
    async def check_captcha_risk(self) -> float:
        """Estimate CAPTCHA risk based on recent activity"""
        # Factors that increase CAPTCHA risk:
        risk = 0.0
        
        # 1. High action frequency
        total_recent = sum(
            len([t for t in timestamps if time.time() - t < 3600])
            for history in self.action_history.values()
            for timestamps in history.values()
        )
        if total_recent > 50:
            risk += 0.3
        
        # 2. Failed actions recently
        # (would track this separately)
        
        # 3. Suspicious patterns detected
        for account_id in self.action_history:
            patterns = await self.check_suspicious_patterns(account_id)
            risk += 0.1 * len(patterns)
        
        return min(risk, 1.0)
    
    async def check_ip_consistency(self, account_id: str) -> bool:
        """Check if IP/location is consistent for account"""
        current_ip = self._get_current_ip()
        
        if account_id not in self._ip_history:
            self._ip_history[account_id] = []
        
        history = self._ip_history[account_id]
        
        # First use - record it
        if not history:
            history.append(current_ip)
            return True
        
        # Check if current IP matches recent history
        return current_ip in history[-5:]  # Last 5 IPs
    
    async def check_proxy_reputation(self, proxy: str) -> Dict:
        """Check proxy IP reputation"""
        # Would integrate with IP reputation services
        # For now, basic checks
        
        return {
            'blacklisted': False,  # Check against known blacklists
            'datacenter': False,   # Detect datacenter IPs
            'vpn': False,          # Detect VPN IPs
            'reputation_score': 0.8  # 0.0 (bad) to 1.0 (good)
        }
    
    async def check_fingerprint_consistency(self) -> bool:
        """Check browser fingerprint hasn't changed"""
        page = self._get_current_page()
        
        current_fp = await page.evaluate("""
            () => {
                return {
                    user_agent: navigator.userAgent,
                    platform: navigator.platform,
                    language: navigator.language,
                    screen: `${screen.width}x${screen.height}`,
                    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
                };
            }
        """)
        
        # Compare with stored fingerprint
        if not hasattr(self, '_stored_fingerprint'):
            self._stored_fingerprint = current_fp
            return True
        
        return current_fp == self._stored_fingerprint
    
    async def monitor_session(self, account_id: str):
        """Continuous session monitoring"""
        while True:
            await asyncio.sleep(60)  # Check every minute
            
            # Check session health
            healthy = await self.check_session_health(account_id)
            if not healthy:
                logger.warning("session_unhealthy", account_id=account_id)
                await self._alert_session_issue(account_id)
            
            # Check risk score
            risk = await self.get_risk_score(account_id)
            if risk > 0.8:
                logger.warning("high_risk_detected", 
                             account_id=account_id, 
                             risk=risk)
                await self._alert_high_risk(account_id, risk)
    
    async def get_risk_score(self, account_id: str) -> float:
        """Calculate overall risk score for account"""
        # Aggregate all checks
        checks = [
            (await self.check_automation_flags())['clean'],
            await self.check_session_health(account_id),
            await self.check_ip_consistency(account_id),
            await self.check_fingerprint_consistency(),
        ]
        
        patterns = await self.check_suspicious_patterns(account_id)
        warmth = await self.check_account_warmth(account_id)
        captcha_risk = await self.check_captcha_risk()
        
        # Calculate score
        risk = 0.0
        risk += 0.2 if not checks[0] else 0  # Automation flags
        risk += 0.3 if not checks[1] else 0  # Session health
        risk += 0.1 if not checks[2] else 0  # IP consistency
        risk += 0.1 if not checks[3] else 0  # Fingerprint
        risk += 0.05 * len(patterns)         # Suspicious patterns
        risk += 0.2 if warmth['too_aggressive'] else 0
        risk += 0.1 * captcha_risk
        
        return min(risk, 1.0)
    
    def record_action(self, account_id: str, action_type: str):
        """Record action for tracking"""
        if account_id not in self.action_history:
            self.action_history[account_id] = {}
        if action_type not in self.action_history[account_id]:
            self.action_history[account_id][action_type] = []
        
        self.action_history[account_id][action_type].append(time.time())
```

**Integration with Action Handler**:

```python
class ActionHandler:
    def __init__(self):
        self.preflight = PreflightChecker()
    
    async def execute_action(self, account_id: str, action: Action):
        """Execute action with preflight checks"""
        
        # Preflight validation
        validation = await self.preflight.validate_action(account_id, action)
        
        if not validation.allowed:
            logger.error("action_blocked", 
                        account_id=account_id,
                        action=action.type,
                        risk_score=validation.risk_score,
                        warnings=validation.warnings)
            raise ActionBlockedError(
                f"Action blocked due to high risk: {validation.warnings}"
            )
        
        # Log warnings
        if validation.warnings:
            logger.warning("action_warnings",
                         account_id=account_id,
                         warnings=validation.warnings,
                         recommendations=validation.recommendations)
        
        # Apply delay if recommended
        if validation.should_delay:
            logger.info("applying_delay", 
                       account_id=account_id,
                       delay=validation.should_delay)
            await asyncio.sleep(validation.should_delay)
        
        # Execute action
        try:
            result = await self._perform_action(action)
            
            # Record successful action
            self.preflight.record_action(account_id, action.type)
            
            return result
        except Exception as e:
            logger.error("action_failed", 
                        account_id=account_id,
                        action=action.type,
                        error=str(e))
            raise
```

**Dashboard Integration**:

```python
@app.get("/health/preflight/{account_id}")
async def get_preflight_status(account_id: str):
    """Get preflight check status for account"""
    checker = get_preflight_checker()
    
    risk_score = await checker.get_risk_score(account_id)
    validation = await checker.validate_action(
        account_id, 
        Action(type="test", data={})
    )
    
    return {
        "account_id": account_id,
        "risk_score": risk_score,
        "status": "safe" if risk_score < 0.3 else "warning" if risk_score < 0.7 else "danger",
        "warnings": validation.warnings,
        "recommendations": validation.recommendations,
        "checks": {
            "automation_flags": (await checker.check_automation_flags())['clean'],
            "session_health": await checker.check_session_health(account_id),
            "rate_limits_ok": await checker.check_rate_limits(account_id, "test"),
            "ip_consistent": await checker.check_ip_consistency(account_id),
            "fingerprint_consistent": await checker.check_fingerprint_consistency(),
        }
    }
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
│   │   ├── alert_manager.py      # NEW: Alerting system
│   │   └── preflight_checker.py  # NEW: Proactive issue detection
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
    ├── conftest.py               # Pytest configuration
    ├── test_session.py
    ├── test_services.py
    ├── test_selectors.py         # NEW: Selector tests
    ├── test_preflight_checker.py # NEW: Preflight tests
    ├── test_api.py
    ├── integration/              # NEW: Integration tests
    │   ├── test_post_creation.py
    │   ├── test_friend_requests.py
    │   └── test_selector_updates.py
    ├── e2e/                      # NEW: E2E tests
    │   ├── test_real_facebook.py
    │   └── test_selector_resilience.py
    └── mocks/                    # NEW: Mock Facebook pages
        └── facebook_pages.py
```

## Testing Strategy

- Unit tests for each service
- Integration tests for API endpoints
- E2E tests with real Facebook account
- Mock Facebook responses for CI/CD
- Selector validation tests
- Rate limiting tests
- Multi-account tests

## Testing Strategy

### Test Pyramid

```
                    ┌─────────────┐
                    │   E2E Tests │  (5%)
                    │  Real FB    │
                    └─────────────┘
                  ┌───────────────────┐
                  │ Integration Tests │  (25%)
                  │  Mock FB Pages    │
                  └───────────────────┘
              ┌─────────────────────────────┐
              │      Unit Tests             │  (70%)
              │  Individual Components      │
              └─────────────────────────────┘
```

### Unit Tests (70% coverage target)

**Test each component in isolation:**

```python
# tests/test_preflight_checker.py
import pytest
from src.core.preflight_checker import PreflightChecker, Action

@pytest.fixture
def checker():
    return PreflightChecker()

class TestAutomationFlagDetection:
    async def test_clean_flags(self, checker):
        """Test detection of clean automation flags"""
        result = await checker.check_automation_flags()
        assert result['clean'] == True
        assert result['flags']['webdriver'] == False
    
    async def test_webdriver_detected(self, checker):
        """Test detection when webdriver flag present"""
        # Mock page with webdriver flag
        result = await checker.check_automation_flags()
        assert result['clean'] == False

class TestRateLimiting:
    async def test_within_limits(self, checker):
        """Test action allowed when within rate limits"""
        result = await checker.check_rate_limits("account1", "friend_request")
        assert result == True
    
    async def test_exceeds_limits(self, checker):
        """Test action blocked when exceeding rate limits"""
        # Record 15 friend requests in last hour
        for _ in range(15):
            checker.record_action("account1", "friend_request")
        
        result = await checker.check_rate_limits("account1", "friend_request")
        assert result == False
    
    async def test_delay_calculation(self, checker):
        """Test delay calculation when approaching limit"""
        for _ in range(12):
            checker.record_action("account1", "post")
        
        validation = await checker.validate_action(
            "account1", 
            Action(type="post", data={})
        )
        assert validation.should_delay is not None
        assert validation.should_delay > 0

class TestSuspiciousPatterns:
    async def test_rapid_fire_detection(self, checker):
        """Test detection of rapid-fire actions"""
        import time
        now = time.time()
        
        # Record 3 actions within 1 second each
        checker.action_history["account1"] = {
            "like": [now, now + 0.5, now + 1.0]
        }
        
        patterns = await checker.check_suspicious_patterns("account1")
        assert any("too fast" in p for p in patterns)
    
    async def test_regular_timing_detection(self, checker):
        """Test detection of too-regular timing"""
        import time
        now = time.time()
        
        # Record actions at exactly 5-second intervals
        checker.action_history["account1"] = {
            "post": [now, now + 5, now + 10, now + 15]
        }
        
        patterns = await checker.check_suspicious_patterns("account1")
        assert any("too regular" in p for p in patterns)
    
    async def test_burst_activity_detection(self, checker):
        """Test detection of burst activity"""
        import time
        now = time.time()
        
        # Record 25 actions in last 5 minutes
        checker.action_history["account1"] = {
            "like": [now - i for i in range(25)]
        }
        
        patterns = await checker.check_suspicious_patterns("account1")
        assert any("Burst activity" in p for p in patterns)

class TestAccountWarmth:
    async def test_new_account_limits(self, checker):
        """Test new account has strict limits"""
        checker._account_ages = {"account1": 1}  # 1 day old
        
        # Record 15 actions today
        import time
        now = time.time()
        checker.action_history["account1"] = {
            "post": [now - i * 3600 for i in range(15)]
        }
        
        warmth = await checker.check_account_warmth("account1")
        assert warmth['too_aggressive'] == True
        assert warmth['max_allowed'] == 10
    
    async def test_mature_account_limits(self, checker):
        """Test mature account has higher limits"""
        checker._account_ages = {"account1": 60}  # 60 days old
        
        # Record 150 actions today
        import time
        now = time.time()
        checker.action_history["account1"] = {
            "post": [now - i * 600 for i in range(150)]
        }
        
        warmth = await checker.check_account_warmth("account1")
        assert warmth['too_aggressive'] == False

class TestRiskScoring:
    async def test_low_risk_score(self, checker):
        """Test low risk score for clean account"""
        risk = await checker.get_risk_score("clean_account")
        assert risk < 0.3
    
    async def test_high_risk_score(self, checker):
        """Test high risk score for problematic account"""
        # Set up problematic conditions
        checker.action_history["bad_account"] = {
            "post": [time.time() - i for i in range(50)]  # 50 posts recently
        }
        
        risk = await checker.get_risk_score("bad_account")
        assert risk > 0.7
    
    async def test_action_blocked_on_high_risk(self, checker):
        """Test action blocked when risk too high"""
        # Create high-risk scenario
        checker.action_history["account1"] = {
            "like": [time.time() - i for i in range(100)]
        }
        
        validation = await checker.validate_action(
            "account1",
            Action(type="like", data={})
        )
        
        assert validation.allowed == False
        assert validation.risk_score > 0.7
        assert len(validation.warnings) > 0

# tests/test_selector_manager.py
class TestSelectorManager:
    async def test_selector_fallback(self, selector_manager):
        """Test selector fallback when primary fails"""
        result = await selector_manager.get_selector("friend_request_button")
        assert result is not None
    
    async def test_selector_validation(self, selector_manager):
        """Test selector validation detects failures"""
        results = await selector_manager.validate_selectors()
        assert isinstance(results, dict)
        assert all(isinstance(v, bool) for v in results.values())
    
    async def test_selector_discovery(self, selector_manager):
        """Test auto-discovery of new selectors"""
        new_selector = await selector_manager.discover_selector(
            "friend_request_button",
            expected_text="Add Friend"
        )
        assert new_selector is not None

# tests/test_session_manager.py
class TestSessionManager:
    async def test_cookie_persistence(self, session_manager):
        """Test cookies are saved and loaded"""
        await session_manager.save_cookies("account1")
        assert os.path.exists("cookies/account1.json")
        
        await session_manager.load_cookies("account1")
        # Verify cookies loaded
    
    async def test_session_validation(self, session_manager):
        """Test session validation works"""
        result = await session_manager.is_logged_in("account1")
        assert isinstance(result, bool)
    
    async def test_remember_me_enabled(self, session_manager):
        """Test Remember Me checkbox is checked during login"""
        # Mock login flow
        # Verify checkbox was checked

# tests/test_action_handler.py
class TestActionHandler:
    async def test_preflight_integration(self, action_handler):
        """Test preflight checks run before actions"""
        action = Action(type="post", data={"content": "test"})
        
        # Should run preflight checks
        result = await action_handler.execute_action("account1", action)
        # Verify preflight was called
    
    async def test_action_blocked_on_validation_failure(self, action_handler):
        """Test action blocked when validation fails"""
        # Set up failing validation
        with pytest.raises(ActionBlockedError):
            await action_handler.execute_action("bad_account", action)
    
    async def test_delay_applied(self, action_handler):
        """Test delay applied when recommended"""
        # Mock validation returning delay
        start = time.time()
        await action_handler.execute_action("account1", action)
        duration = time.time() - start
        assert duration >= 2  # Delay was applied
```

### Integration Tests (25% coverage target)

**Test component interactions with mocked Facebook pages:**

```python
# tests/integration/test_post_creation.py
import pytest
from playwright.async_api import async_playwright

@pytest.fixture
async def mock_facebook_page():
    """Create mock Facebook page for testing"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Load mock HTML that mimics Facebook
        await page.set_content("""
            <html>
                <body>
                    <div data-testid="status-attachment-mentions-input">
                        <textarea name="xhpc_message"></textarea>
                    </div>
                    <button name="post_button">Post</button>
                </body>
            </html>
        """)
        
        yield page
        await browser.close()

class TestPostCreation:
    async def test_create_text_post(self, mock_facebook_page, post_service):
        """Test creating a text post"""
        result = await post_service.create_post(
            account_id="test_account",
            content="Test post",
            page=mock_facebook_page
        )
        
        assert result['success'] == True
        assert result['post_id'] is not None
    
    async def test_create_post_with_image(self, mock_facebook_page, post_service):
        """Test creating post with image"""
        result = await post_service.create_post(
            account_id="test_account",
            content="Test post",
            images=["test_image.jpg"],
            page=mock_facebook_page
        )
        
        assert result['success'] == True
        assert result['media_uploaded'] == True

# tests/integration/test_friend_request_flow.py
class TestFriendRequestFlow:
    async def test_send_friend_request(self, mock_facebook_page, friends_service):
        """Test complete friend request flow"""
        result = await friends_service.send_friend_request(
            account_id="test_account",
            target_user_id="12345",
            page=mock_facebook_page
        )
        
        assert result['success'] == True
        assert result['request_sent'] == True
    
    async def test_rate_limit_prevents_excessive_requests(self, friends_service):
        """Test rate limiting prevents too many friend requests"""
        # Send 15 requests
        for i in range(15):
            await friends_service.send_friend_request(
                account_id="test_account",
                target_user_id=f"user_{i}"
            )
        
        # 16th should be blocked
        with pytest.raises(RateLimitError):
            await friends_service.send_friend_request(
                account_id="test_account",
                target_user_id="user_16"
            )

# tests/integration/test_selector_updates.py
class TestSelectorUpdates:
    async def test_selector_fallback_on_failure(self, page, selector_manager):
        """Test selector fallback when primary fails"""
        # Mock page with changed selectors
        await page.set_content("""
            <div aria-label="Add Friend" role="button">Add Friend</div>
        """)
        
        # Primary selector fails, should use fallback
        element = await selector_manager.find_element(
            page, 
            "friend_request_button"
        )
        
        assert element is not None
    
    async def test_selector_auto_discovery(self, page, selector_manager):
        """Test auto-discovery finds new selector"""
        await page.set_content("""
            <button data-new-attr="add-friend">Add Friend</button>
        """)
        
        new_selector = await selector_manager.discover_selector(
            "friend_request_button",
            expected_text="Add Friend"
        )
        
        assert "data-new-attr" in new_selector
```

### E2E Tests (5% coverage target)

**Test with real Facebook account (use test account only):**

```python
# tests/e2e/test_real_facebook.py
import pytest

@pytest.mark.e2e
@pytest.mark.slow
class TestRealFacebook:
    """E2E tests with real Facebook - use test account only"""
    
    async def test_login_flow(self, api_client):
        """Test complete login flow with real Facebook"""
        response = await api_client.post("/auth", json={
            "email": os.getenv("TEST_FB_EMAIL"),
            "password": os.getenv("TEST_FB_PASSWORD")
        })
        
        assert response.status_code == 200
        assert response.json()['success'] == True
    
    async def test_create_and_delete_post(self, api_client):
        """Test creating and deleting a post on real Facebook"""
        # Create post
        create_response = await api_client.post("/posts/create", json={
            "content": f"Test post {datetime.now()}"
        })
        
        assert create_response.status_code == 201
        post_id = create_response.json()['post_id']
        
        # Verify post exists
        get_response = await api_client.get(f"/posts/{post_id}")
        assert get_response.status_code == 200
        
        # Delete post
        delete_response = await api_client.delete(f"/posts/{post_id}")
        assert delete_response.status_code == 200
        
        # Verify post deleted
        get_response = await api_client.get(f"/posts/{post_id}")
        assert get_response.status_code == 404
    
    async def test_preflight_prevents_rate_limit(self, api_client):
        """Test preflight checker prevents hitting rate limits"""
        # Send multiple friend requests rapidly
        for i in range(20):
            response = await api_client.post("/friends/request", json={
                "user_id": f"test_user_{i}"
            })
            
            if i < 15:
                # Should succeed
                assert response.status_code in [200, 202]
            else:
                # Should be blocked by preflight
                assert response.status_code == 429
                assert "rate limit" in response.json()['message'].lower()

@pytest.mark.e2e
@pytest.mark.slow
class TestSelectorResilience:
    """Test selector resilience with real Facebook"""
    
    async def test_selectors_work_on_real_facebook(self, session_manager):
        """Validate all selectors work on current Facebook UI"""
        page = await session_manager.get_page("test_account")
        
        # Test each critical selector
        selectors_to_test = [
            ("login_button", "https://facebook.com"),
            ("post_button", "https://facebook.com"),
            ("friend_request_button", "https://facebook.com/profile/123"),
        ]
        
        results = {}
        for selector_name, url in selectors_to_test:
            await page.goto(url)
            element = await selector_manager.find_element(page, selector_name)
            results[selector_name] = element is not None
        
        # Log failures for investigation
        failures = [k for k, v in results.items() if not v]
        if failures:
            logger.error("selectors_failed_on_real_facebook", 
                        failures=failures)
        
        # At least 80% should work
        success_rate = sum(results.values()) / len(results)
        assert success_rate >= 0.8
```

### Mock Facebook Pages

**Create realistic mock pages for testing:**

```python
# tests/mocks/facebook_pages.py
class MockFacebookPages:
    """Generate mock Facebook HTML for testing"""
    
    @staticmethod
    def login_page():
        return """
        <html>
            <body>
                <input name="email" type="text" />
                <input name="pass" type="password" />
                <input name="persistent" type="checkbox" />
                <button name="login" type="submit">Log In</button>
            </body>
        </html>
        """
    
    @staticmethod
    def feed_page():
        return """
        <html>
            <body>
                <div role="article" data-post-id="123">
                    <a href="/user/123">John Doe</a>
                    <div>This is a test post</div>
                    <span>Sponsored</span>
                </div>
                <div role="article" data-post-id="124">
                    <a href="/user/124">Jane Smith</a>
                    <div>Another test post</div>
                </div>
            </body>
        </html>
        """
    
    @staticmethod
    def profile_page():
        return """
        <html>
            <body>
                <div data-pagelet="ProfileActions">
                    <button aria-label="Add Friend">Add Friend</button>
                    <button aria-label="Message">Message</button>
                </div>
            </body>
        </html>
        """
```

### Test Configuration

```python
# tests/conftest.py
import pytest
import os

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

@pytest.fixture(scope="session")
def test_account_credentials():
    """Test account credentials from environment"""
    return {
        "email": os.getenv("TEST_FB_EMAIL"),
        "password": os.getenv("TEST_FB_PASSWORD")
    }

@pytest.fixture
async def api_client():
    """FastAPI test client"""
    from httpx import AsyncClient
    from src.api.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_page():
    """Mock Playwright page"""
    # Return mock page object
    pass

# pytest.ini
[pytest]
markers =
    e2e: End-to-end tests with real Facebook
    slow: Slow running tests
    unit: Unit tests
    integration: Integration tests

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Run only fast tests by default
addopts = -v -m "not slow and not e2e"
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run unit tests
        run: pytest tests/ -m "unit" --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
  
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      - name: Run integration tests
        run: pytest tests/ -m "integration"
  
  e2e-tests:
    runs-on: ubuntu-latest
    # Only run on main branch
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      - name: Run E2E tests
        env:
          TEST_FB_EMAIL: ${{ secrets.TEST_FB_EMAIL }}
          TEST_FB_PASSWORD: ${{ secrets.TEST_FB_PASSWORD }}
        run: pytest tests/ -m "e2e"
```

### Test Coverage Goals

- **Overall**: 80% code coverage
- **Core Components**: 90% coverage
  - PreflightChecker
  - SessionManager
  - SelectorManager
- **Services**: 75% coverage
- **API Routes**: 70% coverage

### Testing Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Mock External Dependencies**: Don't hit real Facebook in unit tests
3. **Use Fixtures**: Reuse common setup code
4. **Test Edge Cases**: Not just happy paths
5. **Fast Tests**: Unit tests should run in < 1 second each
6. **Descriptive Names**: Test names should describe what they test
7. **Arrange-Act-Assert**: Clear test structure
8. **Test One Thing**: Each test should verify one behavior

### Running Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run E2E tests (requires test account)
pytest -m e2e

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_preflight_checker.py

# Run specific test
pytest tests/test_preflight_checker.py::TestRateLimiting::test_exceeds_limits

# Run in parallel
pytest -n auto
```

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
