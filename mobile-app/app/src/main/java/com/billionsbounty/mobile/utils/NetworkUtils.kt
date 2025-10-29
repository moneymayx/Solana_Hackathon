package com.billionsbounty.mobile.utils

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject
import java.net.Inet4Address
import java.net.NetworkInterface
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Network utilities for IP detection and network information
 */
@Singleton
class NetworkUtils @Inject constructor() {
    
    private val httpClient = OkHttpClient()
    
    /**
     * Get the device's local IP address
     * Returns the first non-loopback IPv4 address
     */
    fun getLocalIPAddress(): String? {
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces()
            while (interfaces.hasMoreElements()) {
                val networkInterface = interfaces.nextElement()
                val addresses = networkInterface.inetAddresses
                
                while (addresses.hasMoreElements()) {
                    val address = addresses.nextElement()
                    
                    // Return first non-loopback IPv4 address
                    if (!address.isLoopbackAddress && address is Inet4Address) {
                        return address.hostAddress
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return null
    }
    
    /**
     * Get public IP address using external service
     * This is the IP that the backend will see
     */
    suspend fun getPublicIPAddress(): Result<String> = withContext(Dispatchers.IO) {
        try {
            // Try ipify first (most reliable)
            val result = fetchIPFromService("https://api.ipify.org?format=json", "ip")
            if (result.isSuccess) {
                return@withContext result
            }
            
            // Fallback to ip-api
            fetchIPFromService("https://ipapi.co/json/", "ip")
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Get detailed IP information including location
     * Useful for analytics and fraud detection
     */
    suspend fun getDetailedIPInfo(): Result<IPInfo> = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("https://ipapi.co/json/")
                .build()
            
            httpClient.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    return@withContext Result.failure(Exception("IP info request failed: ${response.code}"))
                }
                
                val body = response.body?.string()
                    ?: return@withContext Result.failure(Exception("Empty response body"))
                
                val json = JSONObject(body)
                val ipInfo = IPInfo(
                    ip = json.optString("ip", "Unknown"),
                    city = json.optString("city", "Unknown"),
                    region = json.optString("region", "Unknown"),
                    country = json.optString("country_name", "Unknown"),
                    countryCode = json.optString("country_code", "Unknown"),
                    timezone = json.optString("timezone", "UTC"),
                    org = json.optString("org", "Unknown")
                )
                
                Result.success(ipInfo)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Helper function to fetch IP from various services
     */
    private fun fetchIPFromService(url: String, jsonKey: String): Result<String> {
        return try {
            val request = Request.Builder()
                .url(url)
                .build()
            
            httpClient.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    return Result.failure(Exception("Request failed: ${response.code}"))
                }
                
                val body = response.body?.string()
                    ?: return Result.failure(Exception("Empty response"))
                
                val json = JSONObject(body)
                val ip = json.optString(jsonKey, null)
                
                if (ip.isNullOrEmpty()) {
                    Result.failure(Exception("No IP in response"))
                } else {
                    Result.success(ip)
                }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Check if device is connected to internet
     */
    suspend fun isConnectedToInternet(): Boolean = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("https://www.google.com")
                .head()
                .build()
            
            httpClient.newCall(request).execute().use { response ->
                response.isSuccessful
            }
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Check if device is on VPN
     * This is a heuristic check, not 100% accurate
     */
    fun isOnVPN(): Boolean {
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces()
            while (interfaces.hasMoreElements()) {
                val networkInterface = interfaces.nextElement()
                val name = networkInterface.name.lowercase()
                
                // Common VPN interface names
                if (name.contains("tun") || 
                    name.contains("ppp") || 
                    name.contains("pptp") ||
                    name.contains("l2tp") ||
                    name.contains("ipsec")) {
                    return true
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return false
    }
}

/**
 * Data class for detailed IP information
 */
data class IPInfo(
    val ip: String,
    val city: String,
    val region: String,
    val country: String,
    val countryCode: String,
    val timezone: String,
    val org: String
)



