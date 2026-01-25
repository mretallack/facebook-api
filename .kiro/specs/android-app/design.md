# Android Facebook Client - Design

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         UI Layer                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Jetpack Compose Screens                 │  │
│  │  Feed  Friends  Profile  Messages  Settings          │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      ViewModel Layer                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FeedViewModel  FriendsViewModel  ProfileViewModel   │  │
│  │  MessagesViewModel  AuthViewModel                    │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Repository Layer                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PostRepository  FriendRepository  ProfileRepository │  │
│  │  MessageRepository  AuthRepository                   │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Sources                           │
│  ┌──────────────┐              ┌──────────────┐           │
│  │   Remote     │              │    Local     │           │
│  │  (API Client)│              │  (Room DB)   │           │
│  └──────────────┘              └──────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Core
- **Language**: Kotlin
- **Min SDK**: 24 (Android 7.0)
- **Target SDK**: 34 (Android 14)
- **Build System**: Gradle with Kotlin DSL

### UI
- **Framework**: Jetpack Compose
- **Navigation**: Compose Navigation
- **Theme**: Material Design 3

### Architecture
- **Pattern**: MVVM + Repository
- **DI**: Hilt (Dagger)
- **Async**: Kotlin Coroutines + Flow

### Networking
- **HTTP Client**: Retrofit
- **JSON**: Moshi
- **Image Loading**: Coil

### Storage
- **Database**: Room
- **Preferences**: DataStore (encrypted)
- **Cache**: Room + in-memory

### Testing
- **Unit Tests**: JUnit, MockK
- **UI Tests**: Compose Testing

## Module Structure

```
androidapp/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/facebook/client/
│   │   │   │   ├── ui/
│   │   │   │   │   ├── screens/
│   │   │   │   │   │   ├── FeedScreen.kt
│   │   │   │   │   │   ├── FriendsScreen.kt
│   │   │   │   │   │   ├── ProfileScreen.kt
│   │   │   │   │   │   ├── MessagesScreen.kt
│   │   │   │   │   │   └── LoginScreen.kt
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── PostCard.kt
│   │   │   │   │   │   ├── FriendItem.kt
│   │   │   │   │   │   └── MessageBubble.kt
│   │   │   │   │   └── theme/
│   │   │   │   │       └── Theme.kt
│   │   │   │   ├── viewmodel/
│   │   │   │   │   ├── FeedViewModel.kt
│   │   │   │   │   ├── FriendsViewModel.kt
│   │   │   │   │   ├── ProfileViewModel.kt
│   │   │   │   │   ├── MessagesViewModel.kt
│   │   │   │   │   └── AuthViewModel.kt
│   │   │   │   ├── repository/
│   │   │   │   │   ├── PostRepository.kt
│   │   │   │   │   ├── FriendRepository.kt
│   │   │   │   │   ├── ProfileRepository.kt
│   │   │   │   │   ├── MessageRepository.kt
│   │   │   │   │   └── AuthRepository.kt
│   │   │   │   ├── data/
│   │   │   │   │   ├── remote/
│   │   │   │   │   │   ├── ApiService.kt
│   │   │   │   │   │   ├── ApiClient.kt
│   │   │   │   │   │   └── dto/
│   │   │   │   │   │       ├── PostDto.kt
│   │   │   │   │   │       ├── FriendDto.kt
│   │   │   │   │   │       └── ProfileDto.kt
│   │   │   │   │   ├── local/
│   │   │   │   │   │   ├── AppDatabase.kt
│   │   │   │   │   │   ├── dao/
│   │   │   │   │   │   │   ├── PostDao.kt
│   │   │   │   │   │   │   ├── FriendDao.kt
│   │   │   │   │   │   │   └── MessageDao.kt
│   │   │   │   │   │   └── entity/
│   │   │   │   │   │       ├── PostEntity.kt
│   │   │   │   │   │       ├── FriendEntity.kt
│   │   │   │   │   │       └── MessageEntity.kt
│   │   │   │   │   └── model/
│   │   │   │   │       ├── Post.kt
│   │   │   │   │       ├── Friend.kt
│   │   │   │   │       ├── Profile.kt
│   │   │   │   │       └── Message.kt
│   │   │   │   ├── di/
│   │   │   │   │   ├── AppModule.kt
│   │   │   │   │   ├── NetworkModule.kt
│   │   │   │   │   └── DatabaseModule.kt
│   │   │   │   └── util/
│   │   │   │       ├── Constants.kt
│   │   │   │       └── Extensions.kt
│   │   │   ├── res/
│   │   │   └── AndroidManifest.xml
│   │   └── test/
│   └── build.gradle.kts
├── gradle/
├── build.gradle.kts
├── settings.gradle.kts
└── README.md
```

## Data Models

### Domain Models

```kotlin
data class Post(
    val id: String,
    val author: Author,
    val content: String,
    val timestamp: Long,
    val postType: PostType,
    val engagement: Engagement,
    val images: List<String>,
    val isFriend: Boolean
)

data class Author(
    val name: String,
    val profileUrl: String,
    val profilePicture: String?
)

data class Engagement(
    val likes: Int,
    val comments: Int,
    val shares: Int,
    val isLiked: Boolean
)

data class Friend(
    val id: String,
    val name: String,
    val profileUrl: String,
    val profilePicture: String?,
    val mutualFriends: Int
)

data class Profile(
    val name: String,
    val bio: String?,
    val profilePicture: String?,
    val coverPhoto: String?
)

data class Message(
    val id: String,
    val conversationId: String,
    val text: String,
    val timestamp: Long,
    val isOutgoing: Boolean
)

data class Conversation(
    val id: String,
    val name: String,
    val lastMessage: String?,
    val timestamp: Long,
    val unreadCount: Int
)
```

## API Integration

### API Service Interface

```kotlin
interface ApiService {
    // Auth
    @POST("auth")
    suspend fun authenticate(@Body request: AuthRequest): AuthResponse
    
    // Posts
    @GET("posts/feed")
    suspend fun getFeed(
        @Query("limit") limit: Int,
        @Query("offset") offset: Int
    ): List<PostDto>
    
    @POST("posts/create")
    suspend fun createPost(@Body request: CreatePostRequest): PostActionResponse
    
    @POST("posts/{id}/like")
    suspend fun likePost(@Path("id") postId: String): PostActionResponse
    
    @POST("posts/{id}/comment")
    suspend fun commentPost(
        @Path("id") postId: String,
        @Body request: CommentRequest
    ): PostActionResponse
    
    // Friends
    @GET("friends/search")
    suspend fun searchFriends(
        @Query("q") query: String,
        @Query("limit") limit: Int
    ): List<FriendDto>
    
    @GET("friends/list")
    suspend fun getFriendsList(@Query("limit") limit: Int): List<FriendDto>
    
    @POST("friends/request")
    suspend fun sendFriendRequest(@Body request: FriendRequestData): FriendActionResponse
    
    @GET("friends/requests")
    suspend fun getFriendRequests(): List<FriendDto>
    
    @POST("friends/accept/{id}")
    suspend fun acceptFriendRequest(@Path("id") requestId: String): FriendActionResponse
    
    // Profile
    @GET("profile/me")
    suspend fun getProfile(): ProfileDto
    
    @PUT("profile/me")
    suspend fun updateProfile(@Body request: ProfileUpdateRequest): ProfileDto
    
    // Messages
    @GET("messages/conversations")
    suspend fun getConversations(@Query("limit") limit: Int): List<ConversationDto>
    
    @GET("messages/{id}")
    suspend fun getMessages(
        @Path("id") conversationId: String,
        @Query("limit") limit: Int
    ): List<MessageDto>
    
    @POST("messages/send/{id}")
    suspend fun sendMessage(
        @Path("id") conversationId: String,
        @Body request: SendMessageRequest
    ): MessageActionResponse
}
```

## Screen Designs

### 1. Login Screen
- API server URL input (with default)
- Email input
- Password input (masked)
- Login button
- Remember me checkbox
- Error message display

### 2. Feed Screen (Main)
- Top app bar with title and refresh button
- Pull-to-refresh
- List of post cards:
  - Profile picture (circular)
  - Author name
  - Timestamp (relative, e.g., "2 hours ago")
  - Post content
  - Images (if any)
  - Like/Comment/Share buttons
  - Engagement counts
- Floating action button for create post
- Bottom navigation bar

### 3. Friends Screen
- Top app bar with search button
- Tabs: Friends / Requests
- Friends tab:
  - List of friend items with profile picture, name, mutual friends
  - Unfriend option (swipe or menu)
- Requests tab:
  - List of pending requests
  - Accept/Reject buttons
- Floating action button for search

### 4. Profile Screen
- Cover photo
- Profile picture (large, circular)
- Name
- Bio
- Edit profile button
- Stats (friends count, posts count)

### 5. Messages Screen
- List of conversations:
  - Profile picture
  - Name
  - Last message preview
  - Timestamp
  - Unread indicator
- Tap to open conversation

### 6. Conversation Screen
- Top app bar with contact name
- Message list (scrollable):
  - Outgoing messages (right-aligned, blue)
  - Incoming messages (left-aligned, gray)
  - Timestamps
- Message input at bottom
- Send button

### 7. Create Post Screen
- Text input (multiline)
- Image picker button
- Selected images preview (removable)
- Privacy selector (public/friends/private)
- Post button

## Navigation Flow

```
LoginScreen
    ↓ (on successful login)
MainScreen (Bottom Navigation)
    ├── FeedScreen
    │   ├── CreatePostScreen
    │   └── PostDetailScreen (optional)
    ├── FriendsScreen
    │   ├── FriendSearchScreen
    │   └── FriendProfileScreen (optional)
    ├── MessagesScreen
    │   └── ConversationScreen
    ├── ProfileScreen
    │   └── EditProfileScreen
    └── SettingsScreen
```

## State Management

### UI State Pattern

```kotlin
sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}
```

### ViewModel Example

```kotlin
class FeedViewModel @Inject constructor(
    private val postRepository: PostRepository
) : ViewModel() {
    
    private val _feedState = MutableStateFlow<UiState<List<Post>>>(UiState.Loading)
    val feedState: StateFlow<UiState<List<Post>>> = _feedState.asStateFlow()
    
    init {
        loadFeed()
    }
    
    fun loadFeed(refresh: Boolean = false) {
        viewModelScope.launch {
            _feedState.value = UiState.Loading
            try {
                val posts = postRepository.getFeed(refresh)
                _feedState.value = UiState.Success(posts)
            } catch (e: Exception) {
                _feedState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
    
    fun likePost(postId: String) {
        viewModelScope.launch {
            try {
                postRepository.likePost(postId)
                loadFeed() // Refresh to show updated state
            } catch (e: Exception) {
                // Show error
            }
        }
    }
}
```

## Repository Pattern

```kotlin
class PostRepository @Inject constructor(
    private val apiService: ApiService,
    private val postDao: PostDao
) {
    suspend fun getFeed(refresh: Boolean = false): List<Post> {
        return if (refresh) {
            // Fetch from API
            val posts = apiService.getFeed(limit = 50, offset = 0)
            val entities = posts.map { it.toEntity() }
            postDao.insertAll(entities)
            entities.map { it.toDomain() }
        } else {
            // Try cache first
            val cached = postDao.getAll()
            if (cached.isNotEmpty()) {
                cached.map { it.toDomain() }
            } else {
                getFeed(refresh = true)
            }
        }
    }
    
    suspend fun likePost(postId: String) {
        apiService.likePost(postId)
    }
}
```

## Offline Support

### Caching Strategy
1. **Posts**: Cache for 24 hours, show cached on offline
2. **Friends**: Cache indefinitely, sync on app start
3. **Messages**: Cache all, sync on conversation open
4. **Profile**: Cache for 7 days

### Sync Strategy
- On app start: Sync friends list
- On pull-to-refresh: Sync feed
- On screen open: Sync relevant data
- Background sync: Not implemented (requires WorkManager)

## Security

### Credential Storage
```kotlin
// Use encrypted DataStore
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(
    name = "secure_prefs",
    produceMigration = { EncryptedPreferencesMigration(it) }
)
```

### HTTPS Only
```kotlin
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor { chain ->
        val request = chain.request()
        if (request.url.scheme != "https") {
            throw SecurityException("Only HTTPS allowed")
        }
        chain.proceed(request)
    }
    .build()
```

## Performance Optimizations

1. **Image Loading**: Use Coil with memory/disk cache
2. **List Rendering**: Use LazyColumn with keys
3. **Pagination**: Load 20 posts at a time
4. **Database**: Index frequently queried columns
5. **Network**: Use OkHttp connection pooling

## Error Handling

### Error Types
- Network errors (no connection, timeout)
- API errors (4xx, 5xx)
- Authentication errors (401)
- Validation errors

### Error Display
- Toast for quick actions
- Snackbar for recoverable errors
- Dialog for critical errors
- Inline errors for form validation

## Testing Strategy

### Unit Tests
- ViewModels: Test state transitions
- Repositories: Test data flow
- Mappers: Test DTO to domain conversion

### Integration Tests
- API client: Test with mock server
- Database: Test CRUD operations

### UI Tests
- Critical flows: Login, create post, send message
- Navigation: Test screen transitions

## Build Configuration

### Gradle Dependencies
```kotlin
dependencies {
    // Core
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    
    // Compose
    implementation(platform("androidx.compose:compose-bom:2024.01.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.activity:activity-compose:1.8.2")
    implementation("androidx.navigation:navigation-compose:2.7.6")
    
    // Hilt
    implementation("com.google.dagger:hilt-android:2.50")
    kapt("com.google.dagger:hilt-compiler:2.50")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")
    
    // Retrofit
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-moshi:2.9.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    
    // Moshi
    implementation("com.squareup.moshi:moshi-kotlin:1.15.0")
    kapt("com.squareup.moshi:moshi-kotlin-codegen:1.15.0")
    
    // Room
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")
    
    // Coil
    implementation("io.coil-kt:coil-compose:2.5.0")
    
    // DataStore
    implementation("androidx.datastore:datastore-preferences:1.0.0")
    implementation("androidx.security:security-crypto:1.1.0-alpha06")
    
    // Testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
}
```

## Deployment

### Release Build
- ProGuard enabled
- Code obfuscation
- Resource shrinking
- APK signing with release keystore

### Distribution
- GitHub Releases
- F-Droid (optional)
- Direct APK download

## Future Enhancements

1. **Push Notifications**: Requires backend WebSocket support
2. **Multiple Accounts**: Switch between accounts
3. **Dark Mode**: Already supported by Material 3
4. **Widgets**: Home screen widget for quick post
5. **Shortcuts**: Deep links to specific screens
6. **Accessibility**: TalkBack support, content descriptions
