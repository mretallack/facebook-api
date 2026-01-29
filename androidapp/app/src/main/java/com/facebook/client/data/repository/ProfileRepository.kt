package com.facebook.client.data.repository

import com.facebook.client.data.model.Profile
import com.facebook.client.data.remote.ApiService
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ProfileRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun getProfile(): Result<Profile> {
        return try {
            val profile = apiService.getProfile()
            Result.success(Profile(profile.name, profile.bio, profile.url))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
