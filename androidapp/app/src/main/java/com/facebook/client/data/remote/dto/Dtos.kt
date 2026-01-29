package com.facebook.client.data.remote.dto

import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class AuthRequest(
    val email: String,
    val password: String
)

@JsonClass(generateAdapter = true)
data class AuthResponse(
    val success: Boolean,
    val message: String
)

@JsonClass(generateAdapter = true)
data class PostDto(
    val id: String,
    val author: AuthorDto,
    val content: String,
    val url: String,
    val timestamp: String,
    val image_url: String?
)

@JsonClass(generateAdapter = true)
data class FeedResponse(
    val count: Int,
    val posts: List<PostDto>,
    val cached: Boolean
)

@JsonClass(generateAdapter = true)
data class RefreshResponse(
    val status: String,
    val count: Int,
    val cached: Boolean
)

@JsonClass(generateAdapter = true)
data class AuthorDto(
    val name: String,
    val profile_url: String
)

@JsonClass(generateAdapter = true)
data class EngagementDto(
    val likes: Int,
    val comments: Int,
    val shares: Int
)

@JsonClass(generateAdapter = true)
data class MediaDto(
    val images: List<String>,
    val videos: List<String>
)

@JsonClass(generateAdapter = true)
data class FriendDto(
    val id: String?,
    val name: String,
    val url: String,
    val mutual_friends: Int = 0,
    val profile_picture: String = ""
)

@JsonClass(generateAdapter = true)
data class ProfileDto(
    val name: String?,
    val bio: String?,
    val url: String?
)

@JsonClass(generateAdapter = true)
data class ConversationDto(
    val id: String,
    val name: String,
    val preview: String?
)

@JsonClass(generateAdapter = true)
data class MessageDto(
    val text: String,
    val time: String?,
    val is_outgoing: Boolean
)

@JsonClass(generateAdapter = true)
data class CreatePostRequest(
    val content: String,
    val privacy: String = "public"
)

@JsonClass(generateAdapter = true)
data class CommentRequest(
    val comment: String
)

@JsonClass(generateAdapter = true)
data class SendMessageRequest(
    val message: String
)

@JsonClass(generateAdapter = true)
data class FriendRequestData(
    val profile_url: String
)

@JsonClass(generateAdapter = true)
data class ActionResponse(
    val success: Boolean,
    val message: String?
)
