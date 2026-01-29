package com.facebook.client.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.facebook.client.data.model.Post
import com.facebook.client.data.repository.PostRepository
import com.facebook.client.ui.UiState
import com.facebook.client.util.Constants
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class FeedViewModel @Inject constructor(
    private val postRepository: PostRepository
) : ViewModel() {

    private val _feedState = MutableStateFlow<UiState<List<Post>>>(UiState.Loading)
    val feedState: StateFlow<UiState<List<Post>>> = _feedState

    private var currentOffset = 0

    init {
        loadFeed()
        // Refresh cache every 15 minutes
        viewModelScope.launch {
            while (true) {
                kotlinx.coroutines.delay(15 * 60 * 1000L) // 15 minutes
                refreshCache()
            }
        }
    }

    fun loadFeed(refresh: Boolean = false) {
        viewModelScope.launch {
            android.util.Log.d("FeedViewModel", "loadFeed called: refresh=$refresh")
            _feedState.value = UiState.Loading
            
            postRepository.getFeed(Constants.POSTS_PAGE_SIZE, fresh = refresh)
                .onSuccess { 
                    android.util.Log.d("FeedViewModel", "Feed loaded successfully: ${it.size} posts")
                    _feedState.value = UiState.Success(it)
                }
                .onFailure { 
                    android.util.Log.e("FeedViewModel", "Feed load failed", it)
                    _feedState.value = UiState.Error(it.message ?: "Failed to load feed") 
                }
        }
    }

    private fun refreshCache() {
        viewModelScope.launch {
            postRepository.refreshFeed(Constants.POSTS_PAGE_SIZE)
        }
    }

    fun likePost(postId: String) {
        viewModelScope.launch {
            postRepository.likePost(postId)
            loadFeed(refresh = true)
        }
    }

    fun createPost(content: String, onSuccess: () -> Unit) {
        viewModelScope.launch {
            postRepository.createPost(content)
                .onSuccess { 
                    loadFeed(refresh = true)
                    onSuccess()
                }
        }
    }
}
