package com.facebook.client.data.model

import com.squareup.moshi.Json

data class Person(
    val id: String,
    val name: String,
    @Json(name = "profile_url") val profileUrl: String,
    @Json(name = "profile_picture") val profilePicture: String,
    @Json(name = "mutual_friends") val mutualFriends: Int,
    val location: String,
    val work: String
)
