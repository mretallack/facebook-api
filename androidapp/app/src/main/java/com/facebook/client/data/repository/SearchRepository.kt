package com.facebook.client.data.repository

import com.facebook.client.data.api.SearchApi
import com.facebook.client.data.model.Person
import com.facebook.client.data.model.ProfileDetails
import javax.inject.Inject

class SearchRepository @Inject constructor(
    private val searchApi: SearchApi
) {
    suspend fun searchPeople(query: String): List<Person> {
        android.util.Log.d("SearchRepository", "Searching for: $query")
        return try {
            val results = searchApi.searchPeople(query)
            android.util.Log.d("SearchRepository", "Got ${results.size} results: ${results.take(2)}")
            results
        } catch (e: Exception) {
            android.util.Log.e("SearchRepository", "Search failed: ${e.message}", e)
            emptyList()
        }
    }
    
    suspend fun getProfileDetails(url: String): ProfileDetails? {
        return try {
            searchApi.getProfileDetails(url)
        } catch (e: Exception) {
            android.util.Log.e("SearchRepository", "Failed to get profile: ${e.message}", e)
            null
        }
    }
}
