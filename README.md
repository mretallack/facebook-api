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
- Headless mode can be disabled for debugging
