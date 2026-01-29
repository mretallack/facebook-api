package com.facebook.client.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.facebook.client.data.model.Post
import com.facebook.client.data.repository.PostRepository
import com.facebook.client.ui.UiState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class FollowingViewModel @Inject constructor(
    private val postRepository: PostRepository
) : ViewModel() {

    private val _followingState = MutableStateFlow<UiState<List<Post>>>(UiState.Loading)
    val followingState: StateFlow<UiState<List<Post>>> = _followingState

    init {
        loadFollowing()
    }

    fun loadFollowing(refresh: Boolean = false) {
        viewModelScope.launch {
            _followingState.value = UiState.Loading
            try {
                val posts = postRepository.getFollowingPosts(limit = 20)
                _followingState.value = UiState.Success(posts)
            } catch (e: Exception) {
                _followingState.value = UiState.Error(e.message ?: "Failed to load following posts")
            }
        }
    }
}
