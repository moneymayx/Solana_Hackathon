package com.billionsbounty.mobile.solana

import com.google.gson.Gson
import com.google.gson.JsonObject
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.bitcoinj.core.Base58
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Solana client for interacting with the blockchain via JSON-RPC
 * Handles balance queries, transaction sending, and account data retrieval
 */
@Singleton
class SolanaClient @Inject constructor() {
    
    private val mainnetRpcUrl = "https://api.mainnet-beta.solana.com"
    private val devnetRpcUrl = "https://api.devnet.solana.com"
    
    // Use mainnet by default, can be changed for testing
    private var currentRpcUrl = mainnetRpcUrl
    
    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val gson = Gson()
    
    companion object {
        private const val LAMPORTS_PER_SOL = 1_000_000_000L
        
        // ==============================================================================
        // V2 SMART CONTRACT CONFIGURATION (ACTIVE - Production)
        // ==============================================================================
        // V1 (Deprecated): 4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK
        // V2 (Active): HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm
        
        /**
         * V2 Program ID (Devnet)
         * All payments flow through V2 smart contracts on-chain
         * Backend only provides API endpoints - no fund routing in backend code
         */
        val V2_PROGRAM_ID = "HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm"
        
        /**
         * V2 USDC Mint (Devnet Test Token)
         */
        val V2_USDC_MINT = "JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh"
        
        /**
         * V2 Wallet Addresses (legacy 4-Way Split: 60/20/10/10)
         *
         * NOTE: V3 now uses a 2-way 60/40 jackpot/buyback split enforced by the
         * lottery contract. The mobile app follows the same economics as the web
         * by talking to the shared backend, even though these V2 constants are
         * still present for compatibility and historical reference.
         */
        val V2_BOUNTY_POOL_WALLET = "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF"
        val V2_OPERATIONAL_WALLET = "46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D"
        val V2_BUYBACK_WALLET = "7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya"
        val V2_STAKING_WALLET = "Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX"
        
        /**
         * V2 Program Derived Addresses (PDAs)
         * These are derived from the program ID using seeds
         */
        // Global PDA seed: [b"global"]
        // Bounty PDA seed: [b"bounty", bounty_id.to_bytes(8, "little")]
        // Buyback Tracker PDA seed: [b"buyback_tracker"]
        
        /**
         * Legacy V1 Program ID (Deprecated - For Rollback Only)
         */
        @Deprecated("Use V2_PROGRAM_ID instead", ReplaceWith("V2_PROGRAM_ID"))
        val V1_PROGRAM_ID = "4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK"
    }
    
    /**
     * Switch between mainnet and devnet
     */
    fun useDevnet(useDevnet: Boolean = true) {
        currentRpcUrl = if (useDevnet) devnetRpcUrl else mainnetRpcUrl
    }
    
    /**
     * Get SOL balance for a wallet address
     * @param publicKey Wallet public key in Base58 format
     * @return Balance in SOL (not lamports)
     */
    suspend fun getBalance(publicKey: String): Result<Double> = withContext(Dispatchers.IO) {
        try {
            val requestBody = buildJsonRpcRequest("getBalance", listOf(publicKey))
            val response = makeRpcCall(requestBody)
            
            val lamports = response.getAsJsonObject("result")
                ?.getAsJsonObject("value")
                ?.get("value")?.asLong ?: 0L
            
            val solBalance = lamports.toDouble() / LAMPORTS_PER_SOL
            Result.success(solBalance)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Get account info for any Solana account
     * @param publicKey Account public key in Base58 format
     * @return Account data as JSON object
     */
    suspend fun getAccountInfo(publicKey: String): Result<JsonObject> = withContext(Dispatchers.IO) {
        try {
            val params = mapOf(
                "encoding" to "base64",
                "commitment" to "confirmed"
            )
            val requestBody = buildJsonRpcRequest("getAccountInfo", listOf(publicKey, params))
            val response = makeRpcCall(requestBody)
            
            val accountInfo = response.getAsJsonObject("result")?.getAsJsonObject("value")
                ?: return@withContext Result.failure(Exception("Account not found"))
            
            Result.success(accountInfo)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Send a signed transaction to the blockchain
     * @param signedTransaction Base58-encoded signed transaction
     * @return Transaction signature
     */
    suspend fun sendTransaction(signedTransaction: ByteArray): Result<String> = withContext(Dispatchers.IO) {
        try {
            val base58Transaction = Base58.encode(signedTransaction)
            val params = listOf(
                base58Transaction,
                mapOf(
                    "encoding" to "base58",
                    "skipPreflight" to false,
                    "preflightCommitment" to "confirmed",
                    "maxRetries" to 5
                )
            )
            
            val requestBody = buildJsonRpcRequest("sendTransaction", params)
            val response = makeRpcCall(requestBody)
            
            val signature = response.getAsJsonPrimitive("result")?.asString
                ?: return@withContext Result.failure(Exception("No signature returned"))
            
            Result.success(signature)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Get transaction status/confirmation
     * @param signature Transaction signature to check
     * @return Transaction confirmation status
     */
    suspend fun getTransactionStatus(signature: String): Result<TransactionStatus> = withContext(Dispatchers.IO) {
        try {
            val params = listOf(
                signature,
                mapOf("encoding" to "json")
            )
            val requestBody = buildJsonRpcRequest("getTransaction", params)
            val response = makeRpcCall(requestBody)
            
            val result = response.getAsJsonObject("result")
            if (result == null || result.isJsonNull) {
                return@withContext Result.success(TransactionStatus.NotFound)
            }
            
            val meta = result.getAsJsonObject("meta")
            val err = meta?.get("err")
            
            val status = if (err == null || err.isJsonNull) {
                TransactionStatus.Success
            } else {
                TransactionStatus.Failed(err.toString())
            }
            
            Result.success(status)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Get recent blockhash for transaction creation
     * @return Recent blockhash and last valid block height
     */
    suspend fun getRecentBlockhash(): Result<BlockhashInfo> = withContext(Dispatchers.IO) {
        try {
            val params = listOf(mapOf("commitment" to "finalized"))
            val requestBody = buildJsonRpcRequest("getLatestBlockhash", params)
            val response = makeRpcCall(requestBody)
            
            val result = response.getAsJsonObject("result")?.getAsJsonObject("value")
                ?: return@withContext Result.failure(Exception("No blockhash returned"))
            
            val blockhash = result.get("blockhash")?.asString
                ?: return@withContext Result.failure(Exception("Invalid blockhash"))
            
            val lastValidBlockHeight = result.get("lastValidBlockHeight")?.asLong
                ?: return@withContext Result.failure(Exception("Invalid block height"))
            
            Result.success(BlockhashInfo(blockhash, lastValidBlockHeight))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Get minimum balance for rent exemption
     * @param dataLength Size of account data in bytes
     * @return Minimum balance in lamports
     */
    suspend fun getMinimumBalanceForRentExemption(dataLength: Int): Result<Long> = withContext(Dispatchers.IO) {
        try {
            val requestBody = buildJsonRpcRequest("getMinimumBalanceForRentExemption", listOf(dataLength))
            val response = makeRpcCall(requestBody)
            
            val lamports = response.getAsJsonPrimitive("result")?.asLong
                ?: return@withContext Result.failure(Exception("No result returned"))
            
            Result.success(lamports)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Get program accounts (e.g., all lottery accounts)
     * @param programId Program public key
     * @return List of accounts owned by the program
     */
    suspend fun getProgramAccounts(programId: String): Result<List<JsonObject>> = withContext(Dispatchers.IO) {
        try {
            val params = listOf(
                programId,
                mapOf(
                    "encoding" to "base64",
                    "commitment" to "confirmed"
                )
            )
            val requestBody = buildJsonRpcRequest("getProgramAccounts", params)
            val response = makeRpcCall(requestBody)
            
            val accounts = mutableListOf<JsonObject>()
            val result = response.getAsJsonArray("result")
            
            result?.forEach { element ->
                val accountObj = element.asJsonObject
                accounts.add(accountObj)
            }
            
            Result.success(accounts)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Helper function to build JSON-RPC request
     */
    private fun buildJsonRpcRequest(method: String, params: List<Any>): String {
        val request = mapOf(
            "jsonrpc" to "2.0",
            "id" to 1,
            "method" to method,
            "params" to params
        )
        return gson.toJson(request)
    }
    
    /**
     * Make RPC call to Solana network
     */
    private fun makeRpcCall(requestBody: String): JsonObject {
        val mediaType = "application/json; charset=utf-8".toMediaType()
        val request = Request.Builder()
            .url(currentRpcUrl)
            .post(requestBody.toRequestBody(mediaType))
            .build()
        
        httpClient.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw Exception("RPC call failed: ${response.code} ${response.message}")
            }
            
            val responseBody = response.body?.string()
                ?: throw Exception("Empty response body")
            
            val jsonResponse = gson.fromJson(responseBody, JsonObject::class.java)
            
            // Check for RPC errors
            val error = jsonResponse.getAsJsonObject("error")
            if (error != null) {
                val errorMessage = error.get("message")?.asString ?: "Unknown RPC error"
                throw Exception("RPC error: $errorMessage")
            }
            
            return jsonResponse
        }
    }
    
    /**
     * Convert lamports to SOL
     */
    fun lamportsToSol(lamports: Long): Double {
        return lamports.toDouble() / LAMPORTS_PER_SOL
    }
    
    /**
     * Convert SOL to lamports
     */
    fun solToLamports(sol: Double): Long {
        return (sol * LAMPORTS_PER_SOL).toLong()
    }
}

/**
 * Data class for blockhash information
 */
data class BlockhashInfo(
    val blockhash: String,
    val lastValidBlockHeight: Long
)

/**
 * Transaction status enum
 */
sealed class TransactionStatus {
    object NotFound : TransactionStatus()
    object Success : TransactionStatus()
    data class Failed(val error: String) : TransactionStatus()
}

/**
 * Lottery account data (matches the Rust struct)
 */
data class LotteryAccount(
    val currentJackpot: Long,
    val totalEntries: Int,
    val isActive: Boolean,
    val researchFundFloor: Long,
    val researchFee: Double
)
