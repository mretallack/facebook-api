package com.facebook.client.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.facebook.client.data.model.Conversation
import com.facebook.client.data.model.Message
import com.facebook.client.data.repository.MessageRepository
import com.facebook.client.ui.UiState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class MessagesViewModel @Inject constructor(
    private val messageRepository: MessageRepository
) : ViewModel() {

    private val _conversationsState = MutableStateFlow<UiState<List<Conversation>>>(UiState.Success(emptyList()))
    val conversationsState: StateFlow<UiState<List<Conversation>>> = _conversationsState

    private val _messagesState = MutableStateFlow<UiState<List<Message>>>(UiState.Success(emptyList()))
    val messagesState: StateFlow<UiState<List<Message>>> = _messagesState

    fun loadConversations() {
        viewModelScope.launch {
            try {
                _conversationsState.value = UiState.Loading
                messageRepository.getConversations()
                    .onSuccess { _conversationsState.value = UiState.Success(it) }
                    .onFailure { _conversationsState.value = UiState.Success(emptyList()) }
            } catch (e: Exception) {
                _conversationsState.value = UiState.Success(emptyList())
            }
        }
    }

    fun loadMessages(conversationId: String) {
        viewModelScope.launch {
            _messagesState.value = UiState.Loading
            messageRepository.getMessages(conversationId)
                .onSuccess { _messagesState.value = UiState.Success(it) }
                .onFailure { _messagesState.value = UiState.Error(it.message ?: "Failed to load messages") }
        }
    }

    fun sendMessage(conversationId: String, message: String) {
        viewModelScope.launch {
            messageRepository.sendMessage(conversationId, message)
            loadMessages(conversationId)
        }
    }
}
