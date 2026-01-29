package com.facebook.client.data.repository

import com.facebook.client.data.model.Friend
import com.facebook.client.data.remote.ApiService
import com.facebook.client.data.remote.dto.FriendRequestData
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class FriendRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun getFriends(): Result<List<Friend>> {
        return try {
            android.util.Log.d("FriendRepository", "Fetching friends list")
            val response = apiService.getFriendsList()
            android.util.Log.d("FriendRepository", "Got ${response.size} friends from API")
            val friends = response.map {
                android.util.Log.d("FriendRepository", "Friend: id=${it.id}, name=${it.name}")
                Friend(it.id ?: "", it.name, it.url, it.mutual_friends, it.profile_picture)
            }
            Result.success(friends)
        } catch (e: Exception) {
            android.util.Log.e("FriendRepository", "Error fetching friends", e)
            Result.failure(e)
        }
    }

    suspend fun searchFriends(query: String): Result<List<Friend>> {
        return try {
            val friends = apiService.searchFriends(query).map {
                Friend(it.id, it.name, it.url, it.mutual_friends, it.profile_picture)
            }
            Result.success(friends)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getFriendRequests(): Result<List<Friend>> {
        return try {
            val requests = apiService.getFriendRequests().map {
                Friend(it.id, it.name, it.url, it.mutual_friends, it.profile_picture)
            }
            Result.success(requests)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun sendFriendRequest(profileUrl: String): Result<Boolean> {
        return try {
            val response = apiService.sendFriendRequest(FriendRequestData(profileUrl))
            Result.success(response.success)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun acceptFriendRequest(requestId: String): Result<Boolean> {
        return try {
            val response = apiService.acceptFriendRequest(requestId)
            Result.success(response.success)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
