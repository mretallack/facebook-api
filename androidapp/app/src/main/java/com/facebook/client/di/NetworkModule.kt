package com.facebook.client.di

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.stringPreferencesKey
import com.facebook.client.data.api.SearchApi
import com.facebook.client.data.remote.ApiService
import com.facebook.client.util.Constants
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.runBlocking
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideMoshi(): Moshi {
        return Moshi.Builder()
            .add(KotlinJsonAdapterFactory())
            .build()
    }

    @Provides
    @Singleton
    fun provideOkHttpClient(
        @ApplicationContext context: Context,
        dataStore: DataStore<Preferences>
    ): OkHttpClient {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        // Interceptor to dynamically set base URL
        val baseUrlInterceptor = Interceptor { chain ->
            val originalRequest = chain.request()
            val originalUrl = originalRequest.url
            
            // Get saved API URL from DataStore
            val savedBaseUrl = runBlocking {
                val apiUrlKey = stringPreferencesKey("api_url")
                val url = dataStore.data.map { it[apiUrlKey] ?: Constants.DEFAULT_API_URL }.first()
                // Ensure it has trailing slash
                if (url.endsWith("/")) url else "$url/"
            }
            
            android.util.Log.d("NetworkModule", "Saved base URL: $savedBaseUrl")
            android.util.Log.d("NetworkModule", "Original request URL: $originalUrl")
            
            // Parse the saved base URL
            val newBaseUrl = savedBaseUrl.toHttpUrlOrNull()
            
            if (newBaseUrl == null) {
                android.util.Log.e("NetworkModule", "Failed to parse base URL: $savedBaseUrl")
                chain.proceed(originalRequest)
            } else {
                // Build new URL with saved base
                val newUrl = originalUrl.newBuilder()
                    .scheme(newBaseUrl.scheme)
                    .host(newBaseUrl.host)
                    .port(newBaseUrl.port)
                    .build()
                
                val newRequest = originalRequest.newBuilder()
                    .url(newUrl)
                    .build()
                
                android.util.Log.d("NetworkModule", "Final request URL: ${newRequest.url}")
                
                chain.proceed(newRequest)
            }
        }

        return OkHttpClient.Builder()
            .addInterceptor(baseUrlInterceptor)
            .addInterceptor(loggingInterceptor)
            .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
            .readTimeout(60, java.util.concurrent.TimeUnit.SECONDS)
            .writeTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient, moshi: Moshi): Retrofit {
        // Ensure base URL has trailing slash for Retrofit
        val baseUrl = if (Constants.DEFAULT_API_URL.endsWith("/")) {
            Constants.DEFAULT_API_URL
        } else {
            "${Constants.DEFAULT_API_URL}/"
        }
        
        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
    }

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideSearchApi(retrofit: Retrofit): SearchApi {
        return retrofit.create(SearchApi::class.java)
    }
}
