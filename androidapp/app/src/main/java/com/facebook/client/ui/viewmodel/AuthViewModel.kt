package com.facebook.client.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.facebook.client.data.repository.AuthRepository
import com.facebook.client.ui.UiState
import com.facebook.client.util.Constants
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _loginState = MutableStateFlow<UiState<Boolean>>(UiState.Loading)
    val loginState: StateFlow<UiState<Boolean>> = _loginState

    init {
        viewModelScope.launch {
            val isLoggedIn = authRepository.isLoggedIn()
            _loginState.value = UiState.Success(isLoggedIn)
        }
    }

    fun login(apiUrl: String, email: String, password: String) {
        viewModelScope.launch {
            _loginState.value = UiState.Loading
            authRepository.login(apiUrl, email, password)
                .onSuccess { _loginState.value = UiState.Success(true) }
                .onFailure { _loginState.value = UiState.Error(it.message ?: "Login failed") }
        }
    }

    fun logout() {
        viewModelScope.launch {
            authRepository.logout()
            _loginState.value = UiState.Success(false)
        }
    }
}
