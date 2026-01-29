package com.facebook.client.data.repository

import com.facebook.client.data.model.Conversation
import com.facebook.client.data.model.Message
import com.facebook.client.data.remote.ApiService
import com.facebook.client.data.remote.dto.SendMessageRequest
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class MessageRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun getConversations(): Result<List<Conversation>> {
        return try {
            val conversations = apiService.getConversations().map {
                Conversation(it.id, it.name, it.preview)
            }
            Result.success(conversations)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getMessages(conversationId: String): Result<List<Message>> {
        return try {
            val messages = apiService.getMessages(conversationId).map {
                Message(it.text, it.time, it.is_outgoing)
            }
            Result.success(messages)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun sendMessage(conversationId: String, message: String): Result<Boolean> {
        return try {
            val response = apiService.sendMessage(conversationId, SendMessageRequest(message))
            Result.success(response.success)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
