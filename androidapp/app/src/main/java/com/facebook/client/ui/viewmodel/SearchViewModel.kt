package com.facebook.client.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.facebook.client.data.model.Person
import com.facebook.client.data.model.ProfileDetails
import com.facebook.client.data.repository.SearchRepository
import com.facebook.client.ui.UiState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class SearchViewModel @Inject constructor(
    private val searchRepository: SearchRepository
) : ViewModel() {

    private val _searchResults = MutableStateFlow<UiState<List<Person>>>(UiState.Success(emptyList()))
    val searchResults: StateFlow<UiState<List<Person>>> = _searchResults

    fun searchPeople(query: String) {
        android.util.Log.d("SearchViewModel", "searchPeople called with: $query")
        if (query.isBlank()) {
            _searchResults.value = UiState.Success(emptyList())
            return
        }

        viewModelScope.launch {
            _searchResults.value = UiState.Loading
            android.util.Log.d("SearchViewModel", "Setting Loading state")
            try {
                val results = searchRepository.searchPeople(query)
                android.util.Log.d("SearchViewModel", "Got ${results.size} results, setting Success state")
                _searchResults.value = UiState.Success(results)
            } catch (e: Exception) {
                android.util.Log.e("SearchViewModel", "Error: ${e.message}", e)
                _searchResults.value = UiState.Error(e.message ?: "Search failed")
            }
        }
    }
    
    suspend fun getProfileDetails(url: String): ProfileDetails? {
        return searchRepository.getProfileDetails(url)
    }
}
