# Facebook Automation API - Project Overview

## Description

A comprehensive REST API for automating Facebook interactions using Playwright. Supports multi-account management and provides endpoints for posts, friends, groups, messages, events, pages, marketplace, and stories.

## Key Features

- **Multi-Account Support** - Manage multiple Facebook accounts simultaneously
- **Profile Management** - Get/update profiles, upload pictures
- **Friends Management** - Search, send/accept requests, unfriend, block
- **Posts Management** - Create, delete, like, comment, share posts
- **Groups Management** - Search, join/leave, post to groups
- **Messaging** - Send messages, get conversations
- **Events** - Search events, RSVP
- **Pages** - Search, like, post to pages
- **Marketplace** - Search listings, create listings
- **Stories** - View, create, delete stories
- **GraphQL Interception** - Extract data from Facebook's GraphQL API
- **Rate Limiting** - Automatic rate limiting per account
- **Caching** - In-memory caching with TTL
- **Queue Management** - Priority-based async task queue

## Architecture

```
facebook-api/
├── src/
│   ├── api/              # FastAPI routes and models
│   ├── core/             # Core components (cache, queue, GraphQL)
│   ├── scraper/          # Playwright automation
│   └── services/         # Business logic
├── config/               # Configuration
├── cookies/              # Session cookies (per account)
└── tests/                # Tests
```

## Technology Stack

- **Python 3** - Core language
- **FastAPI** - REST API framework
- **Playwright** - Browser automation
- **Chromium** - Headless browser

## Getting Started

See `README.md` at the project root for:
- Installation instructions
- Configuration setup
- API documentation
- Usage examples
- Security best practices

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Configure credentials
cp .env.example .env
# Edit .env with your credentials

# Start API server
python3 -m src.api.main
# API available at http://localhost:8000
```

## Documentation

- **README.md** - Complete API documentation, endpoints, examples, and troubleshooting
  - **Important**: Keep README.md up to date with any changes to features, endpoints, or configuration
- API docs available at `http://localhost:8000/docs` when server is running

## Security Notes

- Store credentials in `.env` file (never commit)
- Cookies stored per account in `cookies/` directory
- Respect Facebook's Terms of Service
- Use reasonable delays between actions
- Implement API key authentication for production

## Rate Limits

- Friend requests: 15/hour
- Posts: 8/hour
- Messages: 40/hour
- Likes: 80/hour
- Comments: 30/hour
