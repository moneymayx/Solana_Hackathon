package com.billionsbounty.mobile

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class BillionsApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // Hilt handles dependency injection
    }
}
