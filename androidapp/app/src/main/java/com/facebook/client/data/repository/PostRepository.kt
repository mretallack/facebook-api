package com.facebook.client.data.repository

import com.facebook.client.data.model.*
import com.facebook.client.data.remote.ApiService
import com.facebook.client.data.remote.dto.CreatePostRequest
import com.facebook.client.data.remote.dto.CommentRequest
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PostRepository @Inject constructor(
    private val apiService: ApiService,
    private val authRepository: AuthRepository
) {
    suspend fun getFeed(limit: Int, fresh: Boolean = false): Result<List<Post>> {
        return try {
            android.util.Log.d("PostRepository", "Fetching feed: limit=$limit, fresh=$fresh")
            val response = apiService.getFeed(limit, fresh)
            android.util.Log.d("PostRepository", "Response: count=${response.count}, cached=${response.cached}, posts=${response.posts.size}")
            
            val domainPosts = response.posts.map { dto ->
                android.util.Log.d("PostRepository", "Post: id=${dto.id}, author=${dto.author.name}, content=${dto.content.take(50)}")
                Post(
                    id = dto.id,
                    author = Author(dto.author.name, dto.author.profile_url),
                    content = dto.content,
                    timestamp = dto.timestamp,
                    postType = "text",
                    engagement = Engagement(0, 0, 0),
                    images = listOfNotNull(dto.image_url)
                )
            }
            android.util.Log.d("PostRepository", "Converted ${domainPosts.size} posts")
            Result.success(domainPosts)
        } catch (e: Exception) {
            android.util.Log.e("PostRepository", "Error fetching feed", e)
            Result.failure(e)
        }
    }

    suspend fun refreshFeed(limit: Int = 20): Result<Boolean> {
        return try {
            val response = apiService.refreshFeed(limit)
            Result.success(response.status == "refreshed")
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getFollowingPosts(limit: Int = 20): List<Post> {
        // Use same feed endpoint
        return getFeed(limit).getOrDefault(emptyList())
    }

    suspend fun createPost(content: String): Result<Boolean> {
        return try {
            val response = apiService.createPost(CreatePostRequest(content))
            Result.success(response.success)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun likePost(postId: String): Result<Boolean> {
        return try {
            val response = apiService.likePost(postId)
            Result.success(response.success)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun commentPost(postId: String, comment: String): Result<Boolean> {
        return try {
            val response = apiService.commentPost(postId, CommentRequest(comment))
            Result.success(response.success)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
