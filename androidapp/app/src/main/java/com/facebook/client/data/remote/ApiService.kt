package com.facebook.client.data.remote

import com.facebook.client.data.remote.dto.*
import retrofit2.http.*

interface ApiService {
    @POST("auth")
    suspend fun authenticate(@Body request: AuthRequest): AuthResponse

    @GET("posts/feed")
    suspend fun getFeed(
        @Query("limit") limit: Int,
        @Query("fresh") fresh: Boolean = false
    ): FeedResponse

    @POST("posts/feed/refresh")
    suspend fun refreshFeed(
        @Query("limit") limit: Int = 20
    ): RefreshResponse

    @GET("posts/following")
    suspend fun getFollowingPosts(@Query("limit") limit: Int = 20): List<PostDto>

    @POST("posts/create")
    suspend fun createPost(@Body request: CreatePostRequest): ActionResponse

    @POST("posts/{id}/like")
    suspend fun likePost(@Path("id") postId: String): ActionResponse

    @POST("posts/{id}/comment")
    suspend fun commentPost(
        @Path("id") postId: String,
        @Body request: CommentRequest
    ): ActionResponse

    @GET("friends/search")
    suspend fun searchFriends(
        @Query("q") query: String,
        @Query("limit") limit: Int = 20
    ): List<FriendDto>

    @GET("friends/list")
    suspend fun getFriendsList(@Query("limit") limit: Int = 50): List<FriendDto>

    @GET("friends/requests")
    suspend fun getFriendRequests(): List<FriendDto>

    @POST("friends/request")
    suspend fun sendFriendRequest(@Body request: FriendRequestData): ActionResponse

    @POST("friends/accept/{id}")
    suspend fun acceptFriendRequest(@Path("id") requestId: String): ActionResponse

    @GET("profile/me")
    suspend fun getProfile(): ProfileDto

    @GET("messages/conversations")
    suspend fun getConversations(@Query("limit") limit: Int = 20): List<ConversationDto>

    @GET("messages/{id}")
    suspend fun getMessages(
        @Path("id") conversationId: String,
        @Query("limit") limit: Int = 50
    ): List<MessageDto>

    @POST("messages/send/{id}")
    suspend fun sendMessage(
        @Path("id") conversationId: String,
        @Body request: SendMessageRequest
    ): ActionResponse
}
