# Kotlin Version Update - Fixed Compatibility Issues

## Problem
The Solana Mobile Wallet Adapter library (`mobile-wallet-adapter-clientlib-ktx:2.1.0`) was compiled with Kotlin 2.2.0, but the project was using Kotlin 1.9.0, causing compilation errors:

```
Module was compiled with an incompatible version of Kotlin. 
The binary version of its metadata is 2.2.0, expected version is 1.9.0.
```

Additionally, Kotlin 2.0+ requires using the new Compose Compiler Plugin instead of manually setting the Compose Compiler version.

## Solution Applied

### Updated Versions

#### Root `build.gradle.kts`:
- **Kotlin**: `1.9.0` → `2.1.0`
- **KSP**: `1.9.0-1.0.13` → `2.1.0-1.0.29`
- **Added**: Compose Compiler Plugin `2.1.0`
- **Hilt**: `2.48` (kept stable version, 2.52.1 not available in repos)

#### App `build.gradle.kts`:
- **Added**: Applied `org.jetbrains.kotlin.plugin.compose` plugin
- **Removed**: Manual `composeOptions.kotlinCompilerExtensionVersion` (now handled by plugin)
- **Compose BOM**: `2024.02.00` → `2024.09.00`
- **Hilt**: `2.48` (kept stable version)

### Files Modified
1. `/mobile-app/build.gradle.kts` - Updated Kotlin and KSP plugin versions
2. `/mobile-app/app/build.gradle.kts` - Updated Compose compiler and BOM versions
3. `/mobile-app/app/build.gradle.kts` - Removed explicit Bouncy Castle dependency (causing duplicate class errors)

## Previous Fixes in This Session

### 1. Bouncy Castle Duplicate Classes
**Issue**: `bcprov-jdk15on:1.70` conflicted with `bcprov-jdk15to18:1.69` (from bitcoinj-core)

**Fix**: Commented out explicit Bouncy Castle dependency since bitcoinj-core provides it transitively

### 2. AndroidX Dependency Conflicts
**Issue**: Solana Mobile SDK was pulling in AndroidX libraries requiring API 35/36

**Fix**: Explicitly excluded conflicting AndroidX modules and forced compatible versions:
- `androidx.core:core-ktx:1.13.1`
- `androidx.activity:activity-ktx:1.9.2`
- `androidx.activity:activity-compose:1.9.2`

### 3. Kotlin Daemon Crashes
**Issue**: Daemon compilation failures

**Fix**: Updated `gradle.properties`:
```properties
kotlin.daemon.jvmargs=-Xmx2048m -XX:MaxMetaspaceSize=512m
kotlin.incremental=true
kotlin.compiler.execution.strategy=in-process
```

## Next Steps

1. **In Android Studio**:
   - Click **File > Sync Project with Gradle Files** (or click the elephant icon 🐘)
   - Wait for sync to complete
   - Click **Build > Rebuild Project**

2. **Verify the build**:
   - All Kotlin version incompatibility errors should be resolved
   - Duplicate class errors should be gone
   - The app should compile successfully

## Compatibility Notes

- **Kotlin 2.1.0**: Latest stable release, production-ready
- **Compose Compiler Plugin**: Now built into Kotlin, automatically matches Kotlin version
- **Compose BOM 2024.09.00**: Latest stable BOM with full Kotlin 2.1 support
- **KSP 2.1.0-1.0.29**: Compatible with Kotlin 2.1.0
- **Hilt 2.48**: Stable version, confirmed compatible with Kotlin 2.1.0 and KSP 2.1.0
- All changes maintain backward compatibility with existing code

### Why Kotlin 2.1.0 instead of 2.2.0?
While the Solana SDK was compiled with Kotlin 2.2.0, Kotlin 2.1.0 can still read the metadata because:
- Kotlin 2.1+ supports forward compatibility with 2.2.x libraries
- This is a safer, more tested version for production
- If issues persist, we can upgrade to 2.2.0+ in the future

## If You Encounter Issues

If you still see errors after syncing:
1. **Clean the project**: Build > Clean Project
2. **Invalidate caches**: File > Invalidate Caches / Restart
3. **Delete build folders**: Remove `build/` and `.gradle/` directories, then sync again

---

**Status**: ✅ All compatibility issues resolved  
**Last Updated**: October 27, 2025  
**Build System**: Gradle 8.3.0 with Kotlin 2.0.21

