package com.billionsbounty.mobile.data.repository

import com.billionsbounty.mobile.data.api.ApiClient
import com.billionsbounty.mobile.data.api.NftStatusResponse
import com.billionsbounty.mobile.data.api.NftVerifyRequest
import com.billionsbounty.mobile.data.api.NftVerifyResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository for NFT verification operations
 * Now supports mock mode for testing
 */
@Singleton
class NftRepository @Inject constructor(
    private val apiClient: ApiClient
) {
    // Authorized NFT mint address
    companion object {
        const val AUTHORIZED_NFT_MINT = "9dBdXMB3WuTy638W1a1tTygWCzosUmALhRLksrX8oQVa"
    }

    /**
     * Check if wallet owns the required NFT
     * Backend will handle mock mode automatically
     */
    suspend fun checkNftOwnership(walletAddress: String): Result<NftStatusResponse> = withContext(Dispatchers.IO) {
        try {
            val response = apiClient.getNftStatus(walletAddress)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to check NFT ownership: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get NFT verification status for a wallet
     * Returns current verification status and questions remaining
     */
    suspend fun getNftStatus(walletAddress: String): Result<NftStatusResponse> = withContext(Dispatchers.IO) {
        try {
            val response = apiClient.getNftStatus(walletAddress)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to get NFT status: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Verify NFT ownership via smart contract (or mock mode)
     * Backend will automatically use mock mode if PAYMENT_MODE=mock
     */
    suspend fun verifyNftOwnership(
        walletAddress: String,
        signature: String
    ): Result<NftVerifyResponse> = withContext(Dispatchers.IO) {
        try {
            val request = NftVerifyRequest(
                wallet_address = walletAddress,
                signature = signature
            )
            
            val response = apiClient.verifyNft(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Verification failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
