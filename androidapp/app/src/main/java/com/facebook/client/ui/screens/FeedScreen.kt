package com.facebook.client.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.facebook.client.data.model.Post
import com.facebook.client.ui.UiState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FeedScreen(
    feedState: UiState<List<Post>>,
    onRefresh: () -> Unit,
    onLike: (String) -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Feed") })
        }
    ) { padding ->
        when (feedState) {
            is UiState.Loading -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
            is UiState.Success -> {
                val validPosts = feedState.data.filter { it.author.name.isNotEmpty() }
                if (validPosts.isEmpty()) {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("No posts available")
                    }
                } else {
                    LazyColumn(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(padding)
                    ) {
                        items(validPosts) { post ->
                            PostCard(post = post, onLike = { onLike(post.id) })
                        }
                    }
                }
            }
            is UiState.Error -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text(feedState.message)
                }
            }
        }
    }
}

@Composable
fun PostCard(post: Post, onLike: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = post.author.name,
                style = MaterialTheme.typography.titleMedium
            )
            Text(
                text = post.timestamp,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = post.content)
            
            // Display images if available
            if (post.images.isNotEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))
                post.images.forEach { imageUrl ->
                    // Debug logging
                    android.util.Log.d("FeedScreen", "Loading image: $imageUrl")
                    
                    AsyncImage(
                        model = imageUrl,
                        contentDescription = "Post image",
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(200.dp)
                            .padding(vertical = 4.dp),
                        onError = { error ->
                            android.util.Log.e("FeedScreen", "Image load error: ${error.result.throwable}")
                        },
                        onSuccess = {
                            android.util.Log.d("FeedScreen", "Image loaded successfully")
                        }
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            Row {
                TextButton(onClick = onLike) {
                    Text("Like (${post.engagement.likes})")
                }
                TextButton(onClick = {}) {
                    Text("Comment (${post.engagement.comments})")
                }
                TextButton(onClick = {}) {
                    Text("Share (${post.engagement.shares})")
                }
            }
        }
    }
}

@Composable
fun CreatePostDialog(onDismiss: () -> Unit, onCreate: (String) -> Unit) {
    var content by remember { mutableStateOf("") }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Create Post") },
        text = {
            OutlinedTextField(
                value = content,
                onValueChange = { content = it },
                label = { Text("What's on your mind?") },
                modifier = Modifier.fillMaxWidth()
            )
        },
        confirmButton = {
            Button(onClick = { onCreate(content) }) {
                Text("Post")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}
