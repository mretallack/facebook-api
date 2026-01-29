package com.facebook.client.data.repository

import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import com.facebook.client.data.remote.ApiService
import com.facebook.client.data.remote.dto.AuthRequest
import com.facebook.client.util.Constants
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val dataStore: DataStore<Preferences>
) {
    private val API_URL_KEY = stringPreferencesKey("api_url")
    private val EMAIL_KEY = stringPreferencesKey("email")
    private val PASSWORD_KEY = stringPreferencesKey("password")
    private val IS_LOGGED_IN_KEY = stringPreferencesKey("is_logged_in")

    suspend fun login(apiUrl: String, email: String, password: String): Result<Boolean> {
        return try {
            // Ensure URL ends with /
            val normalizedUrl = if (apiUrl.endsWith("/")) apiUrl else "$apiUrl/"
            
            android.util.Log.d("AuthRepository", "Logging in with API URL: $normalizedUrl")
            
            // Save credentials
            saveCredentials(normalizedUrl, email, password)
            
            // Mark as logged in - API uses server-side browser session
            dataStore.edit { it[IS_LOGGED_IN_KEY] = "true" }
            
            Result.success(true)
        } catch (e: Exception) {
            android.util.Log.e("AuthRepository", "Login failed", e)
            Result.failure(e)
        }
    }

    suspend fun isLoggedIn(): Boolean {
        val loggedIn = dataStore.data.map { it[IS_LOGGED_IN_KEY] }.first()
        return loggedIn == "true"
    }

    suspend fun getApiUrl(): String {
        val url = dataStore.data.map { it[API_URL_KEY] ?: Constants.DEFAULT_API_URL }.first()
        android.util.Log.d("AuthRepository", "Retrieved API URL from DataStore: $url")
        return url
    }

    suspend fun logout() {
        dataStore.edit { it.clear() }
    }

    private suspend fun saveCredentials(apiUrl: String, email: String, password: String) {
        dataStore.edit {
            it[API_URL_KEY] = apiUrl
            it[EMAIL_KEY] = email
            it[PASSWORD_KEY] = password
        }
    }
}
