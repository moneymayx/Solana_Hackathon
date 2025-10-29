package com.billionsbounty.mobile.data.preferences

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

/**
 * DataStore for persisting wallet connection state
 * Stores connected wallet address across app restarts
 */

private val Context.walletDataStore: DataStore<Preferences> by preferencesDataStore(name = "wallet_prefs")

@Singleton
class WalletPreferences @Inject constructor(
    @ApplicationContext private val context: Context
) {
    
    companion object {
        private val WALLET_ADDRESS_KEY = stringPreferencesKey("wallet_address")
        private val AUTH_TOKEN_KEY = stringPreferencesKey("auth_token")
        private val LAST_CONNECTED_KEY = stringPreferencesKey("last_connected_timestamp")
    }
    
    /**
     * Get the stored wallet address
     */
    val walletAddress: Flow<String?> = context.walletDataStore.data
        .map { preferences ->
            preferences[WALLET_ADDRESS_KEY]
        }
    
    /**
     * Save wallet connection info
     * @param address Wallet public key in Base58 format
     * @param authToken Optional auth token from MWA
     */
    suspend fun saveWalletConnection(address: String, authToken: String? = null) {
        context.walletDataStore.edit { preferences ->
            preferences[WALLET_ADDRESS_KEY] = address
            if (authToken != null) {
                preferences[AUTH_TOKEN_KEY] = authToken
            }
            preferences[LAST_CONNECTED_KEY] = System.currentTimeMillis().toString()
        }
    }
    
    /**
     * Get stored auth token
     */
    suspend fun getAuthToken(): String? {
        var token: String? = null
        context.walletDataStore.data.collect { preferences ->
            token = preferences[AUTH_TOKEN_KEY]
        }
        return token
    }
    
    /**
     * Clear wallet connection (disconnect)
     */
    suspend fun clearWalletConnection() {
        context.walletDataStore.edit { preferences ->
            preferences.remove(WALLET_ADDRESS_KEY)
            preferences.remove(AUTH_TOKEN_KEY)
            preferences.remove(LAST_CONNECTED_KEY)
        }
    }
    
    /**
     * Check if wallet was recently connected (within 7 days)
     * Useful for determining if we should try to reconnect
     */
    suspend fun isRecentlyConnected(): Boolean {
        var isRecent = false
        context.walletDataStore.data.collect { preferences ->
            val lastConnected = preferences[LAST_CONNECTED_KEY]?.toLongOrNull()
            if (lastConnected != null) {
                val sevenDaysInMillis = 7 * 24 * 60 * 60 * 1000L
                isRecent = (System.currentTimeMillis() - lastConnected) < sevenDaysInMillis
            }
        }
        return isRecent
    }
}



