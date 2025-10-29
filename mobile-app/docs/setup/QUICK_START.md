## 🚀 How to Open the Project in Android Studio

### Method 1: Command Line (Find the correct app name)

First, try to find Android Studio on your system:

```bash
# Try common installation locations
ls /Applications/ | grep -i android
ls /Applications/ | grep -i studio

# Or search for it
mdfind "Android Studio" | grep -i "android studio"
```

Common app names to try:
```bash
# Try these one by one:
open -a "AndroidStudio" mobile-app/
open -a "AndroidStudio.app" mobile-app/
open -a "/Applications/Android Studio.app" mobile-app/
open -a "/Applications/AndroidStudio.app" mobile-app/
```

### Method 2: Manual Opening (Most Reliable)

1. **Find Android Studio:**
   - Open Finder
   - Go to **Applications** folder
   - Look for "Android Studio" or "AndroidStudio"
   - If you don't see it, Android Studio may not be installed

2. **If Android Studio is NOT installed:**
   
   **Option A: Download Android Studio**
   - Go to: https://developer.android.com/studio
   - Download for Mac
   - Install the .dmg file
   - Drag Android Studio to Applications folder
   
   **Option B: Use IntelliJ IDEA**
   - Android Studio is based on IntelliJ IDEA
   - Download: https://www.jetbrains.com/idea/download/
   - Install and open the project

3. **Open the project:**
   - Launch Android Studio
   - Click "Open" or "Open an Existing Project"
   - Navigate to: `/Users/jaybrantley/myenv/Hackathon/Billions_Bounty/mobile-app/`
   - Click "OK"

### Method 3: Command Line Tool (If Installed)

If you have Android Studio command line tools set up:

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
studio mobile-app/
```

Or if you have IntelliJ IDEA:

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
idea mobile-app/
```
