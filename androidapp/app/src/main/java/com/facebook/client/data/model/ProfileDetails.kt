package com.facebook.client.data.model

import com.squareup.moshi.Json

data class ProfileDetails(
    val name: String,
    val bio: String,
    @Json(name = "profile_picture") val profilePicture: String,
    @Json(name = "cover_photo") val coverPhoto: String,
    @Json(name = "friends_count") val friendsCount: String,
    @Json(name = "followers_count") val followersCount: String,
    val location: String,
    val work: String,
    val education: String,
    val relationship: String,
    val joined: String
)
