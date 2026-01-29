package com.facebook.client.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.facebook.client.data.model.ProfileDetails

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileDetailScreen(
    profileDetails: ProfileDetails?,
    isLoading: Boolean,
    onBack: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Profile") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        when {
            isLoading -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text("Loading...")
                }
            }
            profileDetails != null -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding)
                        .verticalScroll(rememberScrollState())
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    // Profile Picture
                    if (profileDetails.profilePicture.isNotEmpty()) {
                        AsyncImage(
                            model = profileDetails.profilePicture,
                            contentDescription = null,
                            modifier = Modifier
                                .size(120.dp)
                                .clip(CircleShape)
                                .align(Alignment.CenterHorizontally)
                        )
                    }
                    
                    // Name - always show
                    Text(
                        text = profileDetails.name.ifEmpty { "Unknown" },
                        style = MaterialTheme.typography.headlineMedium,
                        modifier = Modifier.align(Alignment.CenterHorizontally)
                    )
                    
                    // Bio
                    if (profileDetails.bio.isNotEmpty()) {
                        Card(modifier = Modifier.fillMaxWidth()) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text("Bio", style = MaterialTheme.typography.titleMedium)
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(profileDetails.bio)
                            }
                        }
                    }
                    
                    // Stats
                    if (profileDetails.friendsCount.isNotEmpty() || profileDetails.followersCount.isNotEmpty()) {
                        Card(modifier = Modifier.fillMaxWidth()) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(16.dp),
                                horizontalArrangement = Arrangement.SpaceEvenly
                            ) {
                                if (profileDetails.friendsCount.isNotEmpty()) {
                                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                        Text(
                                            profileDetails.friendsCount,
                                            style = MaterialTheme.typography.titleLarge
                                        )
                                        Text("Friends", style = MaterialTheme.typography.bodySmall)
                                    }
                                }
                                if (profileDetails.followersCount.isNotEmpty()) {
                                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                        Text(
                                            profileDetails.followersCount,
                                            style = MaterialTheme.typography.titleLarge
                                        )
                                        Text("Followers", style = MaterialTheme.typography.bodySmall)
                                    }
                                }
                            }
                        }
                    }
                    
                    // Info
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text("Info", style = MaterialTheme.typography.titleMedium)
                            
                            val hasInfo = profileDetails.work.isNotEmpty() || 
                                         profileDetails.education.isNotEmpty() || 
                                         profileDetails.location.isNotEmpty() || 
                                         profileDetails.relationship.isNotEmpty()
                            
                            if (!hasInfo) {
                                Text(
                                    "No additional information available",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                            
                            if (profileDetails.work.isNotEmpty()) {
                                InfoRow("Work", profileDetails.work)
                            }
                            if (profileDetails.education.isNotEmpty()) {
                                InfoRow("Education", profileDetails.education)
                            }
                            if (profileDetails.location.isNotEmpty()) {
                                InfoRow("Location", profileDetails.location)
                            }
                            if (profileDetails.relationship.isNotEmpty()) {
                                InfoRow("Relationship", profileDetails.relationship)
                            }
                        }
                    }
                }
            }
            else -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text("Failed to load profile")
                }
            }
        }
    }
}

@Composable
fun InfoRow(label: String, value: String) {
    Row {
        Text(
            text = "$label: ",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(text = value, style = MaterialTheme.typography.bodyMedium)
    }
}
