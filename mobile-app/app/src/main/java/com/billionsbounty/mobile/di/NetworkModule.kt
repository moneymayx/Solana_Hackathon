package com.billionsbounty.mobile.di

import com.billionsbounty.mobile.data.api.ApiClient
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    /**
     * Backend API Configuration
     * 
     * EMULATOR (Default): Use "http://10.0.2.2:8000/"
     *   - 10.0.2.2 is Android emulator's special alias for localhost
     *   - Works for testing with backend running on development machine
     * 
     * PHYSICAL DEVICE: Use "http://YOUR_LOCAL_IP:8000/"
     *   - Find your local IP: Run `ipconfig getifaddr en0` (Mac) or `ipconfig` (Windows)
     *   - Example: "http://192.168.1.100:8000/"
     *   - Ensure device and computer are on same WiFi network
     *   - Update firewall to allow port 8000 connections
     * 
     * PRODUCTION: Use your deployed backend URL
     *   - Example: "https://api.billionsbounty.com/"
     *   - Ensure HTTPS is configured for production
     */
    private const val BASE_URL = "http://10.0.2.2:8000/"
    
    /**
     * Payment Mode Configuration
     * 
     * "mock" - Use mock payments and NFT verification for testing (no real transactions)
     * "real" - Use real Solana transactions (requires funded wallet)
     * 
     * Note: Backend must also have PAYMENT_MODE=mock in its .env file for mock mode to work
     */
    private const val PAYMENT_MODE = "mock"  // Change to "real" for production
    
    // Alternative configurations (uncomment to use):
    // private const val BASE_URL = "http://192.168.1.100:8000/"  // Physical device example
    // private const val BASE_URL = "https://api.billionsbounty.com/"  // Production example

    @Provides
    @Singleton
    fun provideHttpClient(): OkHttpClient {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        return OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .addInterceptor { chain ->
                val request = chain.request().newBuilder()
                    .addHeader("User-Agent", "BillionsBounty-Mobile/1.0")
                    .build()
                chain.proceed(request)
            }
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideApiClient(retrofit: Retrofit): ApiClient {
        return retrofit.create(ApiClient::class.java)
    }
    
    /**
     * Provides payment mode configuration
     * Used by repositories to determine if mock or real payments should be used
     */
    @Provides
    @Singleton
    @javax.inject.Named("PaymentMode")
    fun providePaymentMode(): String {
        return PAYMENT_MODE
    }
}

