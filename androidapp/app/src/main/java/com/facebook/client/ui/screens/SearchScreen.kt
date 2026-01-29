package com.facebook.client.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import coil.compose.AsyncImage
import com.facebook.client.data.model.Person
import com.facebook.client.data.model.ProfileDetails
import com.facebook.client.ui.UiState
import com.facebook.client.ui.viewmodel.SearchViewModel
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SearchScreen(
    viewModel: SearchViewModel = hiltViewModel()
) {
    var searchQuery by remember { mutableStateOf("") }
    var selectedPersonUrl by remember { mutableStateOf<String?>(null) }
    var showProfileDetail by remember { mutableStateOf(false) }
    var profileDetails by remember { mutableStateOf<ProfileDetails?>(null) }
    var isLoadingProfile by remember { mutableStateOf(false) }
    
    val searchResults by viewModel.searchResults.collectAsState()
    val coroutineScope = rememberCoroutineScope()

    LaunchedEffect(searchQuery) {
        if (searchQuery.length >= 3) {
            kotlinx.coroutines.delay(500) // Debounce
            viewModel.searchPeople(searchQuery)
        }
    }
    
    if (showProfileDetail) {
        ProfileDetailScreen(
            profileDetails = profileDetails,
            isLoading = isLoadingProfile,
            onBack = { 
                showProfileDetail = false
                profileDetails = null
            }
        )
    } else {
        Column(modifier = Modifier.fillMaxSize()) {
        // Search bar
        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            placeholder = { Text("Search people...") },
            leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
            singleLine = true
        )

        // Results
        when (searchResults) {
            is UiState.Loading -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text("Searching...")
                }
            }
            is UiState.Success -> {
                val people = (searchResults as UiState.Success<List<Person>>).data
                if (people.isEmpty() && searchQuery.isNotEmpty()) {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("No results found")
                    }
                } else {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        items(people) { person ->
                            PersonCard(
                                person = person,
                                onClick = {
                                    isLoadingProfile = true
                                    showProfileDetail = true
                                    coroutineScope.launch {
                                        profileDetails = viewModel.getProfileDetails(person.profileUrl)
                                        isLoadingProfile = false
                                    }
                                }
                            )
                        }
                    }
                }
            }
            is UiState.Error -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text((searchResults as UiState.Error).message)
                }
            }
        }
    }
    }
}

@Composable
fun PersonCard(person: Person, onClick: () -> Unit = {}) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            AsyncImage(
                model = person.profilePicture,
                contentDescription = null,
                modifier = Modifier
                    .size(56.dp)
                    .clip(CircleShape)
            )
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = person.name,
                    style = MaterialTheme.typography.titleMedium
                )
                
                if (person.mutualFriends > 0) {
                    Text(
                        text = "${person.mutualFriends} mutual friends",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                if (person.work.isNotEmpty()) {
                    Text(
                        text = person.work,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                if (person.location.isNotEmpty()) {
                    Text(
                        text = person.location,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

