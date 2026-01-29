package com.facebook.client.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.facebook.client.data.model.Post
import com.facebook.client.ui.UiState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FollowingScreen(
    followingState: UiState<List<Post>>,
    onRefresh: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Following") })
        }
    ) { padding ->
        when (followingState) {
            is UiState.Loading -> {
                Box(modifier = Modifier.fillMaxSize().padding(padding)) {
                    CircularProgressIndicator()
                }
            }
            is UiState.Success -> {
                val posts = followingState.data
                if (posts.isEmpty()) {
                    Box(modifier = Modifier.fillMaxSize().padding(padding)) {
                        Text("No posts from following")
                    }
                } else {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize().padding(padding),
                        contentPadding = PaddingValues(16.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        items(posts) { post ->
                            PostCard(post)
                        }
                    }
                }
            }
            is UiState.Error -> {
                Box(modifier = Modifier.fillMaxSize().padding(padding)) {
                    Text("Error: ${followingState.message}")
                }
            }
        }
    }
}

@Composable
fun PostCard(post: Post) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = post.author.name, style = MaterialTheme.typography.titleMedium)
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = post.content)
            
            // Display images if available
            if (post.images.isNotEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))
                post.images.forEach { imageUrl ->
                    AsyncImage(
                        model = imageUrl,
                        contentDescription = "Post image",
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(200.dp)
                            .padding(vertical = 4.dp)
                    )
                }
            }
        }
    }
}
