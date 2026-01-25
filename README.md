# Facebook Automation API

A comprehensive Python/FastAPI-based Facebook automation API with anti-detection measures and rate limiting.

## Features

- **Profile Management**: Get/update profile, upload pictures
- **Friends Management**: Search, send/accept requests, unfriend, block
- **Posts Management**: Create, delete, like, comment, share posts
- **Groups Management**: Search, join/leave, post to groups
- **Messages**: Send messages, get conversations
- **Anti-Detection**: Human-like behavior, rate limiting, preflight checks
- **Robust Selectors**: Automatic fallback and auto-discovery
- **UI Change Detection**: Proactive monitoring of Facebook UI changes

## Installation

```bash
# Install Python 3.12+
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Configuration

Create a `.env` file:

```env
FB_EMAIL=your_email@example.com
FB_PASSWORD=your_password
HEADLESS=true
API_HOST=0.0.0.0
API_PORT=8000
```

## Usage

### Start the API

```bash
python -m src.api.main
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API docs: `http://localhost:8000/docs`

### Example Requests

#### Authentication
```bash
curl -X POST http://localhost:8000/auth \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "password"}'
```

#### Get Profile
```bash
curl http://localhost:8000/profile/me
```

#### Create Post
```bash
curl -X POST http://localhost:8000/posts/create \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello from API!", "privacy": "public"}'
```

#### Search Friends
```bash
curl "http://localhost:8000/friends/search?q=John&limit=10"
```

#### Send Message
```bash
curl -X POST http://localhost:8000/messages/send/CONVERSATION_ID \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## API Endpoints

### Profile
- `GET /profile/me` - Get current profile
- `PUT /profile/me` - Update profile
- `POST /profile/picture` - Upload profile picture
- `POST /profile/cover` - Upload cover photo

### Friends
- `GET /friends/search?q=query` - Search people
- `GET /friends/list` - Get friends list
- `GET /friends/requests` - Get friend requests
- `POST /friends/request` - Send friend request
- `POST /friends/accept/{id}` - Accept request
- `DELETE /friends/{url}` - Unfriend

### Posts
- `GET /posts/feed` - Get feed posts
- `POST /posts/create` - Create post
- `DELETE /posts/{id}` - Delete post
- `POST /posts/{id}/like` - Like post
- `POST /posts/{id}/comment` - Comment on post
- `POST /posts/{id}/share` - Share post

### Groups
- `GET /groups/search?q=query` - Search groups
- `GET /groups/{id}` - Get group info
- `POST /groups/{id}/join` - Join group
- `POST /groups/{id}/post` - Post to group

### Messages
- `GET /messages/conversations` - Get conversations
- `GET /messages/{id}` - Get messages
- `POST /messages/send/{id}` - Send message

## Rate Limits

Conservative rate limits to prevent account restrictions:

- Friend requests: 15/hour
- Posts: 8/hour
- Messages: 40/hour
- Likes: 80/hour
- Comments: 20/hour
- Group joins: 5/hour

## Anti-Detection Features

- **PreflightChecker**: Validates actions before execution, blocks risky operations
- **Human-like behavior**: Random delays, natural typing speed, mouse movements
- **Selector fallbacks**: Multiple selector strategies with auto-discovery
- **UI change detection**: Monitors Facebook UI for changes
- **Rate limiting**: Conservative limits based on research
- **Session persistence**: Cookie-based authentication with "Remember Me"

## Architecture

```
src/
├── api/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   └── routes/              # API route handlers
│       ├── profile.py
│       ├── friends.py
│       ├── posts.py
│       ├── groups.py
│       └── messages.py
├── scraper/
│   ├── session_manager.py   # Browser session management
│   ├── preflight_checker.py # Risk assessment
│   ├── selector_manager.py  # Selector fallbacks
│   ├── ui_change_detector.py # UI monitoring
│   ├── action_handler.py    # Base action class
│   ├── profile_service.py   # Profile operations
│   ├── friends_service.py   # Friends operations
│   ├── posts_service.py     # Posts operations
│   ├── groups_service.py    # Groups operations
│   └── messages_service.py  # Messaging operations
└── config/
    └── settings.py          # Configuration
```

## Testing

```bash
# Run core component tests
python test_core_components.py

# Run login test
python test_real_login.py
```

## Security Notes

- Never commit `.env` file with credentials
- Use test accounts for development
- Be aware of Facebook's Terms of Service
- Rate limits are conservative but not guaranteed safe
- Account restrictions are possible with any automation

## Technical Issues

### Facebook Detection
Facebook actively detects and blocks automation. This API includes:
- Anti-detection measures (custom user agent, webdriver flag hiding)
- Conservative rate limiting
- Human-like behavior patterns
- Preflight checks to prevent risky actions

### Common Problems
1. **Login failures**: Cookie dialog blocking - handled automatically
2. **Selector changes**: Automatic fallback and discovery
3. **Rate limiting**: Preflight checker blocks excessive actions
4. **Account restrictions**: Use test accounts, follow rate limits

## License

MIT

## Disclaimer

This tool is for educational purposes. Automating Facebook violates their Terms of Service and may result in account restrictions or bans. Use at your own risk with test accounts only.
