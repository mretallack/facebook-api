package com.facebook.client.data.model

data class Post(
    val id: String,
    val author: Author,
    val content: String,
    val timestamp: String,
    val postType: String,
    val engagement: Engagement,
    val images: List<String> = emptyList()
)

data class Author(
    val name: String,
    val profileUrl: String
)

data class Engagement(
    val likes: Int,
    val comments: Int,
    val shares: Int
)

data class Friend(
    val id: String?,
    val name: String,
    val url: String,
    val mutualFriends: Int = 0,
    val profilePicture: String = ""
)

data class Profile(
    val name: String?,
    val bio: String?,
    val url: String?
)

data class Message(
    val text: String,
    val time: String?,
    val isOutgoing: Boolean
)

data class Conversation(
    val id: String,
    val name: String,
    val preview: String?
)
