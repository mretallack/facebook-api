package com.facebook.client.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.facebook.client.data.model.Friend
import com.facebook.client.data.repository.FriendRepository
import com.facebook.client.ui.UiState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class FriendsViewModel @Inject constructor(
    private val friendRepository: FriendRepository
) : ViewModel() {

    private val _friendsState = MutableStateFlow<UiState<List<Friend>>>(UiState.Loading)
    val friendsState: StateFlow<UiState<List<Friend>>> = _friendsState

    private val _requestsState = MutableStateFlow<UiState<List<Friend>>>(UiState.Loading)
    val requestsState: StateFlow<UiState<List<Friend>>> = _requestsState

    init {
        loadFriends()
        loadRequests()
    }

    fun loadFriends() {
        viewModelScope.launch {
            android.util.Log.d("FriendsViewModel", "Loading friends...")
            _friendsState.value = UiState.Loading
            friendRepository.getFriends()
                .onSuccess { 
                    android.util.Log.d("FriendsViewModel", "Loaded ${it.size} friends")
                    _friendsState.value = UiState.Success(it) 
                }
                .onFailure { 
                    android.util.Log.e("FriendsViewModel", "Failed to load friends: ${it.message}", it)
                    _friendsState.value = UiState.Error(it.message ?: "Failed to load friends") 
                }
        }
    }

    fun loadRequests() {
        viewModelScope.launch {
            _requestsState.value = UiState.Loading
            friendRepository.getFriendRequests()
                .onSuccess { _requestsState.value = UiState.Success(it) }
                .onFailure { _requestsState.value = UiState.Error(it.message ?: "Failed to load requests") }
        }
    }

    fun searchFriends(query: String, onResult: (List<Friend>) -> Unit) {
        viewModelScope.launch {
            friendRepository.searchFriends(query)
                .onSuccess { onResult(it) }
        }
    }

    fun sendFriendRequest(profileUrl: String) {
        viewModelScope.launch {
            friendRepository.sendFriendRequest(profileUrl)
        }
    }

    fun acceptRequest(requestId: String) {
        viewModelScope.launch {
            friendRepository.acceptFriendRequest(requestId)
            loadRequests()
            loadFriends()
        }
    }
}
