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
     * ⚠️ IMPORTANT: Choose the correct URL for your testing environment!
     * 
     * EMULATOR: Use "http://10.0.2.2:8000/"
     *   - 10.0.2.2 is Android emulator's special alias for localhost
     *   - Works for testing with backend running on development machine
     * 
     * PHYSICAL DEVICE: Use "http://YOUR_LOCAL_IP:8000/"
     *   - Your computer's IP: 192.168.0.206
     *   - Ensure device and computer are on same WiFi network
     *   - Backend must be started with: uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000
     * 
     * PRODUCTION: Use your deployed backend URL
     *   - Example: "https://api.billionsbounty.com/"
     *   - Ensure HTTPS is configured for production
     */
    
    // 🔧 CONFIGURATION: Uncomment the line you need based on your testing environment
    
    // For Android Emulator (default):
    // private const val BASE_URL = "http://10.0.2.2:8000/"
    
    // For Physical Device (CURRENT RECOMMENDED):
    private const val BASE_URL = "http://192.168.0.206:8000/"
    
    // For Production:
    // private const val BASE_URL = "https://api.billionsbounty.com/"
    
    /**
     * Payment Mode Configuration
     * 
     * "mock" - Use mock payments and NFT verification for testing (no real transactions)
     * "real" - Use real Solana transactions (requires funded wallet)
     * 
     * Note: Backend must also have PAYMENT_MODE=mock in its .env file for mock mode to work
     */
    private const val PAYMENT_MODE = "mock"  // Change to "real" for production

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

