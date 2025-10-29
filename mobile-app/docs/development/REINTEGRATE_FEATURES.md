# Reintegrating Removed Features

## 🔧 Features We Temporarily Removed

### 1. Hilt (Dependency Injection) ✅ Critical
- **Status**: Removed to fix Gradle sync
- **Impact**: No dependency injection currently
- **Files affected**: ViewModels, Repositories, NetworkModule, AppModule

### 2. Solana Mobile SDK ✅ Planned
- **Status**: Removed due to dependency issues
- **Impact**: Wallet functionality is placeholder
- **Files affected**: WalletAdapter, SolanaClient

---

## 🚀 How to Reintegrate

### Step 1: Add Hilt Back

#### 1.1 Update build.gradle.kts (top-level):
```kotlin
plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.22" apply false
    id("com.google.dagger.hilt.android") version "2.48" apply false  // ADD THIS
}
```

#### 1.2 Update app/build.gradle.kts:
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("kotlin-kapt")
    id("com.google.dagger.hilt.android")  // ADD THIS
}

dependencies {
    // ... existing dependencies ...
    
    // ADD THESE:
    implementation("com.google.dagger:hilt-android:2.48")
    kapt("com.google.dagger:hilt-compiler:2.48")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")
}

// ADD THIS AT THE END:
kapt {
    correctErrorTypes = true
}
```

#### 1.3 Update ViewModels:
Already annotated with `@HiltViewModel` - should work once Hilt is added back!

#### 1.4 Update BillionsApplication.kt:
Already has `@HiltAndroidApp` annotation!

#### 1.5 Update MainActivity.kt:
Already has `@AndroidEntryPoint` annotation!

---

### Step 2: Add Solana Mobile SDK Back

#### 2.1 Add to app/build.gradle.kts:
```kotlin
dependencies {
    // ... existing dependencies ...
    
    // Solana Mobile SDK
    implementation("com.solanamobile:mobile-wallet-adapter-clientlib-ktx:1.0.2")
}
```

#### 2.2 Restore WalletAdapter.kt:
The original version with actual Solana Mobile SDK imports

---

## 📝 Recommended Order

### Priority 1: Add Hilt
1. Uncomment Hilt plugin in build.gradle.kts
2. Uncomment Hilt dependency in app/build.gradle.kts
3. Sync Gradle
4. Build project
5. Test that ViewModels work

### Priority 2: Add Solana Mobile SDK
1. Add Solana dependency
2. Restore original WalletAdapter code
3. Sync Gradle
4. Build project
5. Test wallet functionality

---

## ⚠️ Potential Issues

### If Hilt still doesn't work:
1. Try a different Hilt version (2.44, 2.46, 2.48)
2. Check internet connection
3. Clean project: Build → Clean Project

### If Solana SDK doesn't work:
1. Use placeholder implementation for now
2. Add real Solana integration later when stable SDK is available

---

## 🎯 Current Status

- ✅ Gradle sync: WORKING
- ✅ Project structure: COMPLETE
- ⏳ Hilt: PENDING (easy to add back)
- ⏳ Solana SDK: PENDING (needs testing)

---

**Ready to add Hilt back? Let me know and I'll guide you through it!**


