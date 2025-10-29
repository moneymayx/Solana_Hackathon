package com.billionsbounty.mobile.wallet

import android.net.Uri
import androidx.activity.ComponentActivity
import com.solana.mobilewalletadapter.clientlib.ActivityResultSender
import com.solana.mobilewalletadapter.clientlib.MobileWalletAdapter
import com.solana.mobilewalletadapter.clientlib.RpcCluster
import com.solana.mobilewalletadapter.clientlib.TransactionParams
import com.solana.mobilewalletadapter.clientlib.TransactionResult
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import org.bitcoinj.core.Base58
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Wallet adapter for managing Solana wallet connections using Mobile Wallet Adapter
 * Handles authorization, signing transactions, and wallet state management
 */
@Singleton
class WalletAdapter @Inject constructor() {
    
    private val _connectionState = MutableStateFlow<WalletConnectionState>(WalletConnectionState.Disconnected)
    val connectionState: StateFlow<WalletConnectionState> = _connectionState.asStateFlow()
    
    private val _walletAddress = MutableStateFlow<String?>(null)
    val walletAddress: StateFlow<String?> = _walletAddress.asStateFlow()
    
    private var authToken: String? = null
    
    // ActivityResultSender must be initialized early in the activity lifecycle
    private var activityResultSender: ActivityResultSender? = null
    
    companion object {
        private const val IDENTITY_NAME = "BILLION$"
        private const val IDENTITY_URI = "https://billionsbounty.com"
        private const val ICON_URI = "https://billionsbounty.com/favicon.ico"
    }
    
    /**
     * Initialize the wallet adapter with the activity
     * MUST be called in Activity.onCreate() before the activity is started
     */
    fun initialize(activity: ComponentActivity) {
        if (activityResultSender == null) {
            activityResultSender = ActivityResultSender(activity)
        }
    }
    
    /**
     * Authorize and connect to a Solana wallet
     * This will launch the wallet selector and request authorization
     */
    suspend fun authorize(activity: ComponentActivity): Result<String> {
        _connectionState.value = WalletConnectionState.Connecting
        
        return try {
            val sender = activityResultSender ?: throw IllegalStateException(
                "WalletAdapter not initialized. Call initialize(activity) in onCreate()"
            )
            
            val walletAdapter = MobileWalletAdapter()
            
            val result = walletAdapter.transact(sender) {
                val authResult = authorize(
                    identityUri = Uri.parse(IDENTITY_URI),
                    iconUri = Uri.parse(ICON_URI),
                    identityName = IDENTITY_NAME,
                    rpcCluster = RpcCluster.MainnetBeta
                )
                
                // Store auth token for future transactions
                authToken = authResult.authToken
                
                // Convert public key to Base58 string
                val pubKeyBase58 = Base58.encode(authResult.publicKey)
                
                _walletAddress.value = pubKeyBase58
                _connectionState.value = WalletConnectionState.Connected
                
                pubKeyBase58
            }
            
            // Convert TransactionResult to Kotlin Result
            when (result) {
                is TransactionResult.Success -> Result.success(result.payload)
                is TransactionResult.Failure -> {
                    _connectionState.value = WalletConnectionState.Error(result.message)
                    Result.failure(result.e)
                }
                is TransactionResult.NoWalletFound -> {
                    _connectionState.value = WalletConnectionState.Error(result.message)
                    Result.failure(Exception(result.message))
                }
            }
        } catch (e: Exception) {
            val errorMessage = e.message ?: "Failed to authorize wallet"
            _connectionState.value = WalletConnectionState.Error(errorMessage)
            Result.failure(e)
        }
    }
    
    /**
     * Reauthorize with an existing auth token
     * Use this for subsequent transactions after initial authorization
     */
    suspend fun reauthorize(activity: ComponentActivity): Result<String> {
        if (authToken == null) {
            return authorize(activity)
        }
        
        return try {
            val sender = activityResultSender ?: throw IllegalStateException(
                "WalletAdapter not initialized. Call initialize(activity) in onCreate()"
            )
            
            val walletAdapter = MobileWalletAdapter()
            
            val result = walletAdapter.transact(sender) {
                val reauthorizeResult = reauthorize(
                    identityUri = Uri.parse(IDENTITY_URI),
                    iconUri = Uri.parse(ICON_URI),
                    identityName = IDENTITY_NAME,
                    authToken = authToken!!
                )
                
                authToken = reauthorizeResult.authToken
                val pubKeyBase58 = Base58.encode(reauthorizeResult.publicKey)
                
                _walletAddress.value = pubKeyBase58
                _connectionState.value = WalletConnectionState.Connected
                
                pubKeyBase58
            }
            
            // Convert TransactionResult to Kotlin Result
            when (result) {
                is TransactionResult.Success -> Result.success(result.payload)
                is TransactionResult.Failure -> {
                    _connectionState.value = WalletConnectionState.Error(result.message)
                    Result.failure(result.e)
                }
                is TransactionResult.NoWalletFound -> {
                    _connectionState.value = WalletConnectionState.Error(result.message)
                    Result.failure(Exception(result.message))
                }
            }
        } catch (e: Exception) {
            // If reauthorization fails, fall back to full authorization
            authorize(activity)
        }
    }
    
    /**
     * Disconnect from the wallet
     * Clears stored auth token and wallet address
     */
    suspend fun disconnect(activity: ComponentActivity) {
        try {
            if (authToken != null) {
                val sender = activityResultSender ?: throw IllegalStateException(
                    "WalletAdapter not initialized. Call initialize(activity) in onCreate()"
                )
                
                val walletAdapter = MobileWalletAdapter()
                walletAdapter.transact(sender) {
                    deauthorize(authToken!!)
                }
            }
        } catch (e: Exception) {
            // Log error but continue with local cleanup
        } finally {
            _walletAddress.value = null
            authToken = null
            _connectionState.value = WalletConnectionState.Disconnected
        }
    }
    
    /**
     * Sign and send a transaction
     * @param activity The activity to launch wallet for signing
     * @param transaction Serialized transaction bytes
     * @return Result containing transaction signature or error
     */
    suspend fun signAndSendTransaction(
        activity: ComponentActivity,
        transaction: ByteArray
    ): Result<String> {
        if (authToken == null) {
            return Result.failure(Exception("Not authorized. Please connect wallet first."))
        }
        
        return try {
            val sender = activityResultSender ?: throw IllegalStateException(
                "WalletAdapter not initialized. Call initialize(activity) in onCreate()"
            )
            
            val walletAdapter = MobileWalletAdapter()
            
            val result = walletAdapter.transact(sender) {
                val signResult = signAndSendTransactions(
                    transactions = arrayOf(transaction),
                    params = TransactionParams(minContextSlot = null)
                )
                
                // Get the transaction signature
                val signature = signResult.signatures.firstOrNull()
                    ?: throw Exception("No signature returned")
                
                Base58.encode(signature)
            }
            
            // Convert TransactionResult to Kotlin Result
            when (result) {
                is TransactionResult.Success -> Result.success(result.payload)
                is TransactionResult.Failure -> Result.failure(result.e)
                is TransactionResult.NoWalletFound -> Result.failure(Exception(result.message))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Sign multiple transactions
     * @param activity The activity to launch wallet for signing
     * @param transactions Array of serialized transaction bytes
     * @return Result containing array of signed transactions or error
     */
    suspend fun signTransactions(
        activity: ComponentActivity,
        transactions: Array<ByteArray>
    ): Result<Array<ByteArray>> {
        if (authToken == null) {
            return Result.failure(Exception("Not authorized. Please connect wallet first."))
        }
        
        return try {
            val sender = activityResultSender ?: throw IllegalStateException(
                "WalletAdapter not initialized. Call initialize(activity) in onCreate()"
            )
            
            val walletAdapter = MobileWalletAdapter()
            
            val result = walletAdapter.transact(sender) {
                val signResult = signTransactions(transactions)
                signResult.signedPayloads
            }
            
            // Convert TransactionResult to Kotlin Result
            when (result) {
                is TransactionResult.Success -> Result.success(result.payload)
                is TransactionResult.Failure -> Result.failure(result.e)
                is TransactionResult.NoWalletFound -> Result.failure(Exception(result.message))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Sign a message with the wallet's private key
     * @param activity The activity to launch wallet for signing
     * @param message Message bytes to sign
     * @return Result containing signature bytes or error
     */
    suspend fun signMessage(
        activity: ComponentActivity,
        message: ByteArray
    ): Result<ByteArray> {
        if (authToken == null) {
            return Result.failure(Exception("Not authorized. Please connect wallet first."))
        }
        
        return try {
            val sender = activityResultSender ?: throw IllegalStateException(
                "WalletAdapter not initialized. Call initialize(activity) in onCreate()"
            )
            
            val walletAdapter = MobileWalletAdapter()
            
            val result = walletAdapter.transact(sender) {
                // Get the wallet's public key (address) as bytes
                val walletPublicKey = _walletAddress.value?.let { Base58.decode(it) }
                    ?: throw Exception("Wallet address not available")
                
                val signResult = signMessages(
                    messages = arrayOf(message),
                    addresses = arrayOf(walletPublicKey)
                )
                
                signResult.signedPayloads.firstOrNull() 
                    ?: throw Exception("No signature returned")
            }
            
            // Convert TransactionResult to Kotlin Result
            when (result) {
                is TransactionResult.Success -> Result.success(result.payload)
                is TransactionResult.Failure -> Result.failure(result.e)
                is TransactionResult.NoWalletFound -> Result.failure(Exception(result.message))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Get the current wallet's public key
     */
    fun getPublicKey(): String? {
        return _walletAddress.value
    }
    
    /**
     * Check if wallet is connected
     */
    fun isConnected(): Boolean {
        return _walletAddress.value != null && 
               _connectionState.value == WalletConnectionState.Connected &&
               authToken != null
    }
    
    /**
     * Get current connection state
     */
    fun getConnectionState(): WalletConnectionState {
        return _connectionState.value
    }
}

/**
 * States for wallet connection
 */
sealed class WalletConnectionState {
    object Disconnected : WalletConnectionState()
    object Connecting : WalletConnectionState()
    object Connected : WalletConnectionState()
    data class Error(val message: String) : WalletConnectionState()
}
