# Fix Android Studio Build Errors

## Issue
Android Studio shows errors for `PaymentAmountSelectionDialogTest.kt`:
- Unresolved reference 'screens'
- Unresolved reference 'PaymentAmountSelectionDialog'
- Unresolved reference 'it'
- Hilt nested class error

However, **command line builds work fine**, indicating this is an IDE cache issue.

## Solution Steps

### Step 1: Invalidate Android Studio Caches
1. In Android Studio, go to: **File → Invalidate Caches...**
2. Check all boxes:
   - Clear file system cache and Local History
   - Clear downloaded shared indexes
   - Clear VCS Log caches and indexes
3. Click **Invalidate and Restart**

### Step 2: Clean and Rebuild
After Android Studio restarts:
1. Go to: **Build → Clean Project**
2. Wait for it to complete
3. Go to: **Build → Rebuild Project**

### Step 3: Sync Gradle
1. Go to: **File → Sync Project with Gradle Files**
2. Wait for sync to complete

### Step 4: Verify Build Configuration
Make sure Android Studio is using the correct JDK:
1. Go to: **File → Project Structure → SDK Location**
2. Ensure **JDK location** points to Java 17
3. Go to: **File → Settings → Build, Execution, Deployment → Build Tools → Gradle**
4. Ensure **Gradle JDK** is set to Java 17

### Step 5: If Still Failing
If errors persist after cache invalidation:

1. **Close Android Studio**
2. Delete these directories manually:
   ```bash
   cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/mobile-app
   rm -rf .idea/caches
   rm -rf .idea/gradle
   rm -rf app/build
   rm -rf build
   ```
3. **Reopen Android Studio**
4. Let it re-index and sync Gradle

### Step 6: Verify Build Works
Run from terminal to confirm:
```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/mobile-app
./gradlew clean
./gradlew compileDebugAndroidTestKotlin
```

If this succeeds, Android Studio should work after cache invalidation.

## Root Cause
The Hilt nested class error (`BillionsApplication_HiltComponents$ServiceCBuilderModule`) occurs when:
- Android Studio's internal build cache is stale
- Generated Hilt files aren't being recognized by the IDE
- Build order is incorrect in IDE vs command line

The command line build works because it uses a fresh Gradle daemon process.

## Prevention
- Always sync Gradle after dependency changes
- Invalidate caches if you see persistent errors that don't match command line builds
- Use command line builds (`./gradlew`) as the source of truth for build issues


