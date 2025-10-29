package com.billionsbounty.mobile.di

import android.content.Context
import com.billionsbounty.mobile.data.api.ApiClient
import com.billionsbounty.mobile.data.repository.ApiRepository
import com.billionsbounty.mobile.solana.SolanaClient
import com.billionsbounty.mobile.wallet.WalletAdapter
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideApiRepository(apiClient: ApiClient): ApiRepository {
        return ApiRepository(apiClient)
    }

    @Provides
    @Singleton
    fun provideSolanaClient(): SolanaClient {
        return SolanaClient()
    }

    @Provides
    @Singleton
    fun provideWalletAdapter(): WalletAdapter {
        return WalletAdapter()
    }
}



