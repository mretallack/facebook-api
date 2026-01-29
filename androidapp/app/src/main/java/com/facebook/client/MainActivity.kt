package com.facebook.client

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import coil.compose.AsyncImage
import com.facebook.client.data.model.Friend
import com.facebook.client.ui.UiState
import com.facebook.client.ui.screens.*
import com.facebook.client.ui.theme.FacebookClientTheme
import com.facebook.client.ui.viewmodel.*
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            FacebookClientTheme {
                App()
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun App() {
    val navController = rememberNavController()
    val authViewModel: AuthViewModel = hiltViewModel()
    val loginState by authViewModel.loginState.collectAsStateWithLifecycle()

    when (loginState) {
        is UiState.Loading -> {
            // Show splash or loading
        }
        is UiState.Success -> {
            if ((loginState as UiState.Success).data) {
                // Logged in - show main app
                MainScreen(onLogout = { authViewModel.logout() })
            } else {
                // Not logged in - show login
                LoginScreen(
                    loginState = loginState,
                    onLogin = { url, email, password ->
                        authViewModel.login(url, email, password)
                    }
                )
            }
        }
        is UiState.Error -> {
            LoginScreen(
                loginState = loginState,
                onLogin = { url, email, password ->
                    authViewModel.login(url, email, password)
                }
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(onLogout: () -> Unit) {
    var selectedItem by remember { mutableStateOf(0) }
    var selectedFriend by remember { mutableStateOf<Friend?>(null) }
    val items = listOf("Feed", "Friends", "Profile")
    val icons = listOf(
        Icons.Default.Home,
        Icons.Default.Person,
        Icons.Default.AccountCircle
    )

    val feedViewModel: FeedViewModel = hiltViewModel()
    val friendsViewModel: FriendsViewModel = hiltViewModel()
    val profileViewModel: ProfileViewModel = hiltViewModel()

    val feedState by feedViewModel.feedState.collectAsStateWithLifecycle()
    val friendsState by friendsViewModel.friendsState.collectAsStateWithLifecycle()
    val requestsState by friendsViewModel.requestsState.collectAsStateWithLifecycle()
    val profileState by profileViewModel.profileState.collectAsStateWithLifecycle()

    if (selectedFriend != null) {
        AlertDialog(
            onDismissRequest = { selectedFriend = null },
            title = { Text(selectedFriend!!.name) },
            text = {
                Column {
                    if (selectedFriend!!.profilePicture.isNotEmpty()) {
                        AsyncImage(
                            model = selectedFriend!!.profilePicture,
                            contentDescription = "Profile picture",
                            modifier = Modifier.size(100.dp)
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                    }
                    Text("${selectedFriend!!.mutualFriends} mutual friends")
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(selectedFriend!!.url, style = MaterialTheme.typography.bodySmall)
                }
            },
            confirmButton = {
                TextButton(onClick = { selectedFriend = null }) {
                    Text("Close")
                }
            }
        )
    }

    Scaffold(
        bottomBar = {
            NavigationBar {
                items.forEachIndexed { index, item ->
                    NavigationBarItem(
                        icon = { Icon(icons[index], contentDescription = item) },
                        label = { Text(item) },
                        selected = selectedItem == index,
                        onClick = { selectedItem = index }
                    )
                }
            }
        }
    ) { padding ->
        Surface(modifier = Modifier.padding(padding)) {
            when (selectedItem) {
                0 -> FeedScreen(
                    feedState = feedState,
                    onRefresh = { feedViewModel.loadFeed(refresh = true) },
                    onLike = { feedViewModel.likePost(it) }
                )
                1 -> FriendsScreen(
                    friendsState = friendsState,
                    requestsState = requestsState,
                    onAcceptRequest = { friendsViewModel.acceptRequest(it) },
                    onFriendClick = { friend ->
                        selectedFriend = friend
                    }
                )
                2 -> ProfileScreen(
                    profileState = profileState,
                    onLogout = onLogout
                )
            }
        }
    }
}
