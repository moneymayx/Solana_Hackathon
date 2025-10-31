package com.billionsbounty.mobile.di

import com.billionsbounty.mobile.data.repository.ApiRepository
import dagger.hilt.EntryPoint
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent

/**
 * EntryPoint for accessing ApiRepository in Composables
 * Used when direct injection is not possible
 */
@EntryPoint
@InstallIn(SingletonComponent::class)
interface ApiRepositoryEntryPoint {
    fun apiRepository(): ApiRepository
}
