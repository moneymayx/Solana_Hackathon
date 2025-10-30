# Mobile App 500 Error - Fix Guide

## Problem
The mobile app shows "Error 500 - Internal Server Error" when trying to load bounty boxes, even though the website works fine.

## Root Cause
The mobile app is configured to connect to `http://10.0.2.2:8000/` which only works for Android emulator. If you're testing on a physical device or if there are network connectivity issues, this will fail.

## Solution

### Step 1: Identify Your Testing Environment

#### If using **Android Emulator**:
1. Your backend should be accessible at `http://10.0.2.2:8000/`
2. This is the special IP that emulator uses to connect to host machine's localhost

#### If using **Physical Android Device**:
1. You need to use your computer's local IP address
2. Your computer's IP is: **192.168.0.206**
3. Backend URL should be: `http://192.168.0.206:8000/`

### Step 2: Update Network Configuration

Edit the file: `mobile-app/app/src/main/java/com/billionsbounty/mobile/di/NetworkModule.kt`

**For Emulator (Line 36):**
```kotlin
private const val BASE_URL = "http://10.0.2.2:8000/"
```

**For Physical Device (Line 36):**
```kotlin
private const val BASE_URL = "http://192.168.0.206:8000/"
```

### Step 3: Ensure Backend is Running

1. Open a terminal in your project directory
2. Activate the virtual environment:
   ```bash
   cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
   source venv/bin/activate
   ```

3. Start the backend server:
   ```bash
   python3 -m uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   
   **Important:** Use `--host 0.0.0.0` to allow connections from other devices on your network!

### Step 4: Test the Connection

#### Test from Terminal:
```bash
# Test if backend is accessible
curl http://192.168.0.206:8000/api/bounties
```

This should return JSON data with bounties, not a 500 error.

#### Test from Mobile App:
1. Rebuild the app in Android Studio
2. Run on your device/emulator
3. Navigate to bounty boxes section
4. The bounties should now load

### Step 5: Check Firewall Settings (If Still Not Working)

If you're using a physical device and still getting errors:

1. **Mac Firewall:** System Preferences → Security & Privacy → Firewall → Allow incoming connections for Python
2. **Router:** Make sure both your computer and phone are on the same WiFi network

### Troubleshooting

#### Error: "Connection refused"
- Backend is not running
- Check if port 8000 is already in use: `lsof -i :8000`

#### Error: "Network unreachable" 
- Phone and computer are on different networks
- Try using emulator instead of physical device

#### Error: "500 Internal Server Error"
- Database issue - Run: `python3 -c "import asyncio; from src.database import create_tables; asyncio.run(create_tables())"`
- Check backend logs for specific error

#### Backend logs show SQLAlchemy errors:
- Make sure you're using the virtual environment:
  ```bash
  source venv/bin/activate
  pip3 install -r requirements.txt
  ```

## Quick Test Script

Create a test script to verify everything works:

```bash
#!/bin/bash
# Save as test_mobile_connection.sh

echo "Testing backend connection..."
curl -s http://192.168.0.206:8000/api/bounties | jq '.bounties[0]'

if [ $? -eq 0 ]; then
    echo "✅ Backend is accessible from network"
else
    echo "❌ Backend connection failed"
    echo "Make sure backend is running with: uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000"
fi
```

## Summary

The key differences:
- **Website:** Works because it's running on localhost (127.0.0.1 or localhost:3000)
- **Mobile Emulator:** Needs 10.0.2.2 (special emulator IP)
- **Mobile Physical Device:** Needs your computer's actual local IP (192.168.0.206)

**Action Required:**
1. Update `NetworkModule.kt` with correct IP
2. Start backend with `--host 0.0.0.0` 
3. Rebuild mobile app
4. Test connection

