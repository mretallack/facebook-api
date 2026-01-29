# Facebook Client - Android App

A clean, chronological Facebook client for Android that shows only posts from your actual friends.

## Features

- **Chronological Feed**: Posts sorted newest first (no algorithm)
- **Friends Only**: Only shows posts from people you actually follow
- **No Ads**: Filters out sponsored and suggested content
- **Full Functionality**: Like, comment, share, create posts
- **Friends Management**: Search, add, accept friend requests
- **Messaging**: View conversations and send messages
- **Material Design 3**: Modern, clean UI

## Requirements

- Android 7.0 (API 24) or higher
- Facebook Automation API backend running (see main project README)

## Installation

### From Source

1. Clone the repository:
```bash
cd /home/mark/git/facebook/androidapp
```

2. Open in Android Studio

3. Build and run on device/emulator

### From APK

1. Download the latest APK from releases
2. Enable "Install from Unknown Sources" on your device
3. Install the APK

## Configuration

On first launch, you'll need to configure:

1. **API Server URL**: The URL where your Facebook API backend is running
   - For emulator: `http://10.0.2.2:8000`
   - For device on same network: `http://YOUR_COMPUTER_IP:8000`
   - For remote server: `https://your-server.com:8000`

2. **Facebook Credentials**: Your Facebook email and password
   - These are sent to YOUR API server, not to us
   - Credentials are stored encrypted on device

## Usage

### Feed
- Pull down to refresh
- Tap like/comment/share buttons
- Tap + button to create a post

### Friends
- View your friends list
- Switch to "Requests" tab to see pending requests
- Tap "Accept" to accept a friend request

### Messages
- View your conversations
- Tap a conversation to view messages (coming soon)

### Profile
- View your profile information
- Tap "Logout" to sign out

## Architecture

- **MVVM**: Model-View-ViewModel architecture
- **Jetpack Compose**: Modern declarative UI
- **Hilt**: Dependency injection
- **Retrofit**: REST API client
- **Room**: Local database (for future caching)
- **Kotlin Coroutines**: Async operations

## API Backend

This app requires the Facebook Automation API backend to be running. See the main project README for setup instructions.

The backend handles all Facebook automation using Playwright, while this app provides a clean mobile interface.

## Security

- Credentials stored using encrypted DataStore
- HTTPS enforced for API communication
- No data sent to third parties
- All communication is between your phone and YOUR API server

## Known Limitations

- Requires API backend to be running
- No offline mode yet (caching planned)
- No push notifications (requires backend support)
- Limited to API capabilities (no real-time updates)

## Development

### Build

```bash
./gradlew assembleDebug
```

### Run Tests

```bash
./gradlew test
```

### Build Release APK

```bash
./gradlew assembleRelease
```

## Contributing

This is an open-source project. Contributions welcome!

## License

MIT

## Disclaimer

This app uses automation to access Facebook, which may violate Facebook's Terms of Service. Use at your own risk with test accounts only.
