# Wallet Connection Testing Guide

## Overview

Since mobile emulators can't fully simulate wallet app connections, we've created multiple testing approaches to verify wallet connection flows work correctly.

---

## Testing Methods

### 1. Unit Tests ✅ (Automated)

**Location:** `app/src/test/java/com/billionsbounty/mobile/ui/viewmodel/WalletViewModelTest.kt`

**Coverage:** 17 comprehensive tests

#### What's Tested:
- ✅ Initial state verification
- ✅ Successful wallet connection
- ✅ Failed wallet connection handling
- ✅ Wallet disconnection
- ✅ Balance fetching on connection
- ✅ Balance fetch error handling
- ✅ Manual balance refresh
- ✅ Network switching (mainnet/devnet)
- ✅ Connection state management
- ✅ Full integration flow
- ✅ State persistence

#### Run Tests:
```bash
cd Billions_Bounty/mobile-app
./gradlew test --tests "*.WalletViewModelTest"
```

---

### 2. UI Instrumented Tests ✅ (Semi-Automated)

**Location:** `app/src/androidTest/java/com/billionsbounty/mobile/ui/WalletConnectionFlowTest.kt`

**Coverage:** 5 UI interaction tests

#### What's Tested:
- ✅ Dialog displays correctly
- ✅ Connect button exists and is enabled
- ✅ Connected state displays correctly
- ✅ Address truncation works
- ✅ Dialog UI elements are visible

#### Run Tests:
```bash
cd Billions_Bounty/mobile-app

# Start emulator first
emulator -avd Pixel_5_API_31 &

# Run instrumented tests
./gradlew connectedAndroidTest
```

---

### 3. Python Test Script ✅ (Manual + Verification)

**Location:** `mobile-app/test_wallet_flows.py`

**Purpose:** Automates device checks and provides manual testing workflow

#### Features:
- ✅ Verifies device/emulator connection
- ✅ Checks app installation status
- ✅ Detects installed Solana wallets
- ✅ Launches the app
- ✅ Provides step-by-step manual test instructions
- ✅ Generates test report

#### Usage:
```bash
cd Billions_Bounty/mobile-app

# Basic usage (uses first connected device)
python3 test_wallet_flows.py

# Specify device ID
python3 test_wallet_flows.py --device emulator-5554

# Output JSON results
python3 test_wallet_flows.py --json

# Skip wait period
python3 test_wallet_flows.py --skip-wait
```

#### Example Output:
```
🤖 Mobile Wallet Flow Tester
============================================================
🔍 Checking device connection...
✅ Found 1 device(s)
   - emulator-5554    device

📱 Checking app installation status...
✅ App is installed: com.billionsbounty.mobile

🔍 Checking for installed Solana wallets...
✅ Phantom: installed
❌ Solflare: not installed
❌ Sollet: not installed
❌ Backpack: not installed

🚀 Launching app...
✅ App launched successfully

============================================================
📋 MANUAL TESTING INSTRUCTIONS
============================================================

1. Navigate to a bounty in the app
2. Look for the 'Connect Wallet' button
3. Click the 'Connect Wallet' button
4. Observe what happens:
   ✅ Wallet selector should open
   ✅ Available wallets should be listed
   ✅ You can select a wallet
   ✅ After approval, wallet address should appear

5. After connection, check that:
   ✅ Wallet address is displayed
   ✅ Balance is fetched
   ✅ UI updates correctly

============================================================
📊 TEST RESULTS
============================================================

✅ PASS Device Connected
✅ PASS App Installed
✅ PASS App Launched
✅ PASS Wallets Available
✅ PASS Flow Completed
------------------------------------------------------------
Pass Rate: 100.0% (5/5)
============================================================
```

---

## Manual Testing Checklist

Since actual wallet connections require interaction with real wallet apps, use this checklist:

### Pre-Testing Setup
- [ ] Emulator is running
- [ ] App is installed and launches successfully
- [ ] At least one Solana wallet is installed (Phantom, Solflare, etc.)

### Wallet Connection Flow
- [ ] Navigate to a bounty detail page
- [ ] Click "Connect Wallet" button
- [ ] Wallet selector opens
- [ ] Select a wallet from the list
- [ ] Approve connection in wallet app
- [ ] Return to Billions Bounty app
- [ ] Wallet address is displayed (truncated)
- [ ] "Wallet Connected" message appears
- [ ] Balance is fetched and displayed
- [ ] No errors are shown

### Disconnection Flow
- [ ] Click "Disconnect" button
- [ ] Wallet address is cleared
- [ ] Balance is cleared
- [ ] Connection state returns to disconnected

### Error Handling
- [ ] Reject connection in wallet app → error message shown
- [ ] No wallet installed → appropriate message shown
- [ ] Network error → balance fetch fails gracefully

### Persistence
- [ ] Close and reopen app
- [ ] Previously connected wallet is remembered
- [ ] User can reconnect with single tap

---

## Running All Tests

### Full Test Suite
```bash
cd Billions_Bounty/mobile-app

# Run all unit tests
./gradlew test

# Run all instrumented tests (requires emulator)
./gradlew connectedAndroidTest

# Run Python test script
python3 test_wallet_flows.py

# Generate test report
./gradlew test connectedAndroidTest
```

### Specific Test Classes
```bash
# Only wallet tests
./gradlew test --tests "*Wallet*"

# Only payment tests
./gradlew test --tests "*Payment*"

# Only chat tests
./gradlew test --tests "*Chat*"
```

---

## Test Coverage Summary

| Component | Unit Tests | UI Tests | Integration Tests | Total |
|-----------|------------|----------|-------------------|-------|
| **WalletViewModel** | 17 ✅ | - | 1 ✅ | **18** |
| **WalletAdapter** | (via mock) | - | - | - |
| **SolanaClient** | (via mock) | - | - | - |
| **WalletConnectionDialog** | - | 5 ✅ | 1 ✅ | **6** |
| **WalletPreferences** | (via mock) | - | - | - |
| **TOTAL** | **17** | **5** | **2** | **24** |

---

## Known Limitations

### What We Can Test
✅ Business logic and state management  
✅ UI rendering and display  
✅ Error handling flows  
✅ State transitions  
✅ Data persistence patterns  
✅ Mock wallet interactions  

### What We Cannot Test
❌ Actual wallet app launches  
❌ Real blockchain signatures  
❌ Live network connections  
❌ Physical wallet hardware  
❌ Real transaction signing  

### Why?
- Mobile Wallet Adapter requires actual wallet apps installed
- Emulators don't fully simulate Android's intent resolution
- Real blockchain connections require network access
- Security prevents full SDK mocking in instrumented tests

---

## Troubleshooting

### Tests Fail to Run

**Issue:** "No tests found"
```bash
# Solution: Clean and rebuild
./gradlew clean
./gradlew test
```

**Issue:** "Gradle daemon issues"
```bash
# Solution: Stop gradle and retry
./gradlew --stop
./gradlew test
```

### Python Script Fails

**Issue:** "adb: command not found"
```bash
# Solution: Add Android SDK platform-tools to PATH
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

**Issue:** "No devices found"
```bash
# Solution: Start emulator or connect device
emulator -avd Pixel_5_API_31 &
# or connect physical device via USB
```

### App Won't Launch on Emulator

**Issue:** "App crashes on launch"
```bash
# Solution: Check logs
adb logcat | grep -i error

# Reinstall app
./gradlew uninstallAll
./gradlew installDebug
```

---

## Future Enhancements

### Short-term
- [ ] Add unit tests for `WalletAdapter` with more mocking
- [ ] Create UI tests for payment flow with wallet
- [ ] Add accessibility testing for wallet dialogs

### Medium-term
- [ ] Set up CI/CD with GitHub Actions
- [ ] Add screenshot comparison tests
- [ ] Create performance benchmarks

### Long-term
- [ ] Integrate with Solana testnet for real transactions
- [ ] Add end-to-end tests with Appium
- [ ] Create automated visual regression tests

---

## Related Documentation

- [Wallet Integration Complete](docs/guides/WALLET_INTEGRATION_COMPLETE.md)
- [Wallet Integration Status](docs/guides/WALLET_INTEGRATION_STATUS.md)
- [Testing Guide](TESTING_GUIDE.md)
- [Test Results Summary](TEST_RESULTS_SUMMARY.md)

---

## Questions?

If you have questions or issues with wallet testing:
1. Check the main [Testing Guide](TESTING_GUIDE.md)
2. Review [Test Results Summary](TEST_RESULTS_SUMMARY.md)
3. Run tests with `--info` flag for verbose output
4. Check device logs with `adb logcat`

