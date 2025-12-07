package com.billionsbounty.mobile.wallet

import androidx.activity.ComponentActivity
import kotlinx.coroutines.delay
import kotlin.random.Random

/**
 * Mock wallet adapter used exclusively for emulator testing.
 * Generates deterministic-looking Base58 wallet addresses so flows that depend on a wallet
 * can run end-to-end without the Solana Mobile stack.
 */
class MockWalletAdapter {
    
    private val base58Alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    
    /**
     * Pretend to authorize a wallet connection by returning a synthetic address.
     * The activity parameter mirrors the real adapter signature so we can reuse the same code paths.
     */
    suspend fun authorize(@Suppress("UNUSED_PARAMETER") activity: ComponentActivity): Result<String> {
        delay(300) // Small delay to mimic network round-trip for clearer UX cues.
        return Result.success(generateWalletAddress())
    }
    
    private fun generateWalletAddress(length: Int = 44): String {
        val rng = Random(System.currentTimeMillis())
        return buildString(length) {
            repeat(length) {
                append(base58Alphabet[rng.nextInt(base58Alphabet.length)])
            }
        }
    }
}





