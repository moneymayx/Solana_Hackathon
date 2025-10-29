# Wallet Adapter Lifecycle Fix

## Problem
The app was crashing with the error:
```
LifecycleOwner com.billionsbounty.mobile.MainActivity@e954f53 is attempting to register 
while current state is RESUMED. LifecycleOwners must call register before they are STARTED.
```

## Root Cause
The `ActivityResultSender` from the Solana Mobile Wallet Adapter SDK requires registration **before** the Activity reaches the STARTED state. Previously, we were creating a new `ActivityResultSender` instance inside each wallet method (authorize, signTransaction, etc.), which happened after the activity was already RESUMED.

## Solution
We refactored the `WalletAdapter` to:

1. **Store a single ActivityResultSender instance** as a property
2. **Initialize it early** in the MainActivity's `onCreate()` before `setContent()`
3. **Reuse the same instance** across all wallet operations

## Changes Made

### 1. WalletAdapter.kt
- Added `activityResultSender` property
- Added `initialize(activity: ComponentActivity)` method
- Updated all methods (`authorize`, `reauthorize`, `disconnect`, `signAndSendTransaction`, `signTransactions`, `signMessage`) to use the stored sender instead of creating new ones
- Added proper error handling when not initialized

### 2. MainActivity.kt
- Injected `WalletAdapter` using Hilt
- Called `walletAdapter.initialize(this)` in `onCreate()` before `setContent()`

## Usage Pattern

```kotlin
@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    
    @Inject
    lateinit var walletAdapter: WalletAdapter
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // ✅ Initialize WalletAdapter early - CRITICAL!
        walletAdapter.initialize(this)
        
        setContent {
            // ... your compose UI
        }
    }
}
```

## Why This Works
The `ActivityResultLauncher` used internally by `ActivityResultSender` must be registered before the activity is started. By initializing in `onCreate()` before `setContent()`, we ensure the registration happens at the right point in the activity lifecycle:

```
Activity Lifecycle:
  onCreate() ✅ <- Safe to register ActivityResultLauncher here
    ↓
  onStart()  ❌ <- Too late to register
    ↓
  onResume() ❌ <- Where the previous error occurred
```

## Testing
After rebuilding the app:
1. Open the app
2. Navigate to a bounty
3. Click "Connect Wallet"
4. The wallet selector should now open without the lifecycle error

## Related Files
- `/app/src/main/java/com/billionsbounty/mobile/wallet/WalletAdapter.kt`
- `/app/src/main/java/com/billionsbounty/mobile/MainActivity.kt`
- `/app/src/main/java/com/billionsbounty/mobile/di/AppModule.kt`

