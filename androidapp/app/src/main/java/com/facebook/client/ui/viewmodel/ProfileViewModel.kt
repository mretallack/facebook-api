package com.facebook.client.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.facebook.client.data.model.Profile
import com.facebook.client.data.repository.ProfileRepository
import com.facebook.client.ui.UiState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val profileRepository: ProfileRepository
) : ViewModel() {

    private val _profileState = MutableStateFlow<UiState<Profile>>(UiState.Loading)
    val profileState: StateFlow<UiState<Profile>> = _profileState

    init {
        loadProfile()
    }

    fun loadProfile() {
        viewModelScope.launch {
            _profileState.value = UiState.Loading
            profileRepository.getProfile()
                .onSuccess { _profileState.value = UiState.Success(it) }
                .onFailure { _profileState.value = UiState.Error(it.message ?: "Failed to load profile") }
        }
    }
}
