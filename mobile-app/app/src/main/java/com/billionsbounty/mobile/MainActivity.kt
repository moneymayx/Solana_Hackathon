package com.billionsbounty.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.billionsbounty.mobile.navigation.NavGraph
import com.billionsbounty.mobile.ui.theme.BillionsBountyTheme
import com.billionsbounty.mobile.wallet.WalletAdapter
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    
    @Inject
    lateinit var walletAdapter: WalletAdapter
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize WalletAdapter early in the lifecycle
        // This MUST be done before the activity is started
        walletAdapter.initialize(this)
        
        setContent {
            BillionsBountyTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    NavGraph()
                }
            }
        }
    }
}
