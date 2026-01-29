package com.facebook.client.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.facebook.client.data.model.Friend
import com.facebook.client.ui.UiState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FriendsScreen(
    friendsState: UiState<List<Friend>>,
    requestsState: UiState<List<Friend>>,
    onAcceptRequest: (String) -> Unit,
    onFriendClick: (Friend) -> Unit = {}
) {
    var selectedTab by remember { mutableStateOf(0) }

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Friends") })
        }
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) {
            TabRow(selectedTabIndex = selectedTab) {
                Tab(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    text = { Text("Friends") }
                )
                Tab(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    text = { Text("Requests") }
                )
            }

            when (selectedTab) {
                0 -> FriendsList(friendsState, onFriendClick)
                1 -> RequestsList(requestsState, onAcceptRequest)
            }
        }
    }
}

@Composable
fun FriendsList(friendsState: UiState<List<Friend>>, onFriendClick: (Friend) -> Unit = {}) {
    when (friendsState) {
        is UiState.Loading -> {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        is UiState.Success -> {
            if (friendsState.data.isEmpty()) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text("No friends yet")
                }
            } else {
                LazyColumn {
                    items(friendsState.data) { friend ->
                        FriendItem(friend, onFriendClick)
                    }
                }
            }
        }
        is UiState.Error -> {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text(friendsState.message)
            }
        }
    }
}

@Composable
fun RequestsList(requestsState: UiState<List<Friend>>, onAccept: (String) -> Unit) {
    when (requestsState) {
        is UiState.Loading -> {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        is UiState.Success -> {
            LazyColumn {
                items(requestsState.data) { friend ->
                    RequestItem(friend, onAccept)
                }
            }
        }
        is UiState.Error -> {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text(requestsState.message)
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FriendItem(friend: Friend, onClick: (Friend) -> Unit = {}) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp),
        onClick = { onClick(friend) }
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            if (friend.profilePicture.isNotEmpty()) {
                AsyncImage(
                    model = friend.profilePicture,
                    contentDescription = "${friend.name} profile picture",
                    modifier = Modifier.size(48.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
            }
            Column(modifier = Modifier.weight(1f)) {
                Text(text = friend.name, style = MaterialTheme.typography.titleMedium)
                Text(
                    text = "${friend.mutualFriends} mutual friends",
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

@Composable
fun RequestItem(friend: Friend, onAccept: (String) -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(text = friend.name, style = MaterialTheme.typography.titleMedium)
                Text(
                    text = "${friend.mutualFriends} mutual friends",
                    style = MaterialTheme.typography.bodySmall
                )
            }
            Button(onClick = { friend.id?.let { onAccept(it) } }) {
                Text("Accept")
            }
        }
    }
}
