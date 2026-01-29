package com.facebook.client.data.api

import com.facebook.client.data.model.Person
import com.facebook.client.data.model.ProfileDetails
import retrofit2.http.GET
import retrofit2.http.Query

interface SearchApi {
    @GET("search/people")
    suspend fun searchPeople(
        @Query("q") query: String,
        @Query("limit") limit: Int = 20
    ): List<Person>
    
    @GET("search/profile")
    suspend fun getProfileDetails(
        @Query("url") url: String
    ): ProfileDetails
}
