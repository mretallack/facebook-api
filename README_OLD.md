# Facebook Scraper API

Playwright-based API for extracting and filtering Facebook posts.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browser:
```bash
playwright install chromium
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Facebook credentials
```

## Configuration

Edit `.env` file:
```
FB_EMAIL=your_email@example.com
FB_PASSWORD=your_password
API_HOST=0.0.0.0
API_PORT=8000
HEADLESS=true
```

## Usage

Start the API server:
```bash
python -m src.api.main
```

Or with uvicorn:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### GET /posts
Extract posts from Facebook feed.

Query parameters:
- `limit` (int, default: 20): Number of posts to return
- `offset` (int, default: 0): Pagination offset
- `exclude_ads` (bool, default: false): Filter out sponsored posts
- `exclude_suggested` (bool, default: false): Filter out suggested posts
- `post_type` (str, optional): Filter by type (text|photo|video|link|mixed)

Example:
```bash
curl "http://localhost:8000/posts?limit=10&exclude_ads=true"
```

### GET /health
Check API and browser status.

### POST /auth
Authenticate with Facebook credentials.

Body:
```json
{
  "email": "your_email@example.com",
  "password": "your_password"
}
```

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Notes

- First run will require Facebook login
- Session cookies are saved for reuse
- 2FA may require manual intervention
- Headless mode can be disabled for debugging (set `HEADLESS=false`)
- If login fails, check:
  - Credentials are correct
  - Account doesn't require verification
  - Account doesn't have 2FA enabled
  - Facebook isn't blocking automation (try with `HEADLESS=false`)

## Troubleshooting

### Login Fails
If automated login fails, you can manually login once:
1. Set `HEADLESS=false` in `.env`
2. Run the API
3. Complete login manually in the browser window
4. Cookies will be saved for future use

### Testing
Run login tests:
```bash
python3.12 test_login.py        # Basic browser tests
python3.12 test_real_login.py   # Actual login attempt
```

## Technical Issues & Solutions

### Issue: Cookie Dialog Blocking Login Button
**Problem**: Facebook's cookie consent dialog overlay was intercepting click events on the login button. Playwright's click method failed with error:
```
<span>Essential cookies: These cookies are required to...</span> 
from <div data-testid="cookie-policy-manage-dialog"> 
subtree intercepts pointer events
```

**Solution**: Instead of trying to click through the dialog, use JavaScript to:
1. Remove the cookie dialog: `document.querySelector('[data-testid="cookie-policy-manage-dialog"]').remove()`
2. Click login button via JavaScript: `document.querySelector('button[name="login"]').click()`

JavaScript clicks bypass Playwright's overlay detection, allowing the login to proceed.

**Implementation**: See `src/scraper/session_manager.py` - `login()` method

### Anti-Detection Measures
To avoid Facebook blocking automation:
- Custom user agent string (Chrome 120 on Linux)
- Hide webdriver flag: `Object.defineProperty(navigator, 'webdriver', {get: () => undefined})`
- Human-like typing with random delays (50-150ms per character)
- Random delays between actions (0.3-4 seconds)
- Disable automation-controlled Blink features

### Session Persistence
- Cookies saved to `cookies.json` after successful login
- Automatically loaded on subsequent runs
- Reduces login frequency and detection risk

## Security

**Important**: Never commit sensitive credentials to git!

Protected files (in `.gitignore`):
- `.env` - Contains Facebook credentials
- `cookies.json` - Contains session cookies
- `*.log` - May contain sensitive data

Always use `.env.example` as template and keep actual `.env` file local only.
