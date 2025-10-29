# Installing Android Studio

## ❌ Android Studio Not Found

Android Studio is not installed on your system. Here's how to install it:

---

## 📥 Installation Steps

### Step 1: Download Android Studio

1. Go to: **https://developer.android.com/studio**
2. Click **"Download Android Studio"**
3. Select **Mac** as your platform
4. Download the `.dmg` file (about 800MB)
5. Wait for download to complete

### Step 2: Install Android Studio

1. **Open the downloaded .dmg file**
2. **Drag Android Studio** to the Applications folder
3. **Open Applications** folder
4. **Launch Android Studio** (first launch takes time)
5. Follow the setup wizard

### Step 3: First Launch Setup

1. **Import Settings:** Choose "Do not import settings"
2. **Welcome Screen:** Click "Next"
3. **SDK Components:** Click "Next" (defaults are fine)
4. **Emulator:** Click "Next" (optional, can install later)
5. **License Agreement:** Accept all licenses
6. **Click "Finish"** and wait for installation

---

## ⚡ Quick Install Command

Alternatively, if you have Homebrew installed:

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Android Studio
brew install --cask android-studio
```

Then launch Android Studio and complete the setup wizard.

---

## 🚀 After Installation

Once Android Studio is installed:

### 1. Open the Project

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
open -a "Android Studio" mobile-app/
```

### 2. Initial Setup

- **Gradle Sync:** Android Studio will automatically sync Gradle files
- **Download Dependencies:** Wait for dependencies to download (first time can take 10-15 minutes)
- **Indexing:** Wait for code indexing to complete

### 3. Configure JDK

Android Studio should automatically find JDK 17, but if it doesn't:

1. Go to **File** → **Project Structure** → **SDK Location**
2. Set **JDK location** to Java 17 (usually auto-detected)
3. Click **OK**

---

## 📋 System Requirements

Make sure your Mac meets these requirements:

- **macOS:** 10.14 or newer
- **RAM:** 8GB minimum (16GB recommended)
- **Disk Space:** 4GB for Android Studio + 1GB for Android SDK
- **Screen:** 1280x800 minimum resolution

---

## ⏱️ Installation Time

- **Download:** 5-15 minutes (depending on internet speed)
- **Install:** 5-10 minutes
- **First Launch Setup:** 10-20 minutes
- **First Project Sync:** 10-15 minutes
- **Total:** ~40-60 minutes

---

## 🔧 Alternative: Use IntelliJ IDEA

If you don't want to install Android Studio, you can use IntelliJ IDEA (which Android Studio is based on):

### Install IntelliJ IDEA

```bash
brew install --cask intellij-idea-ce
```

### Open Project

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
idea mobile-app/
```

**Note:** You may need to install Android plugin:
1. Go to **File** → **Settings** → **Plugins**
2. Search for "Android Support"
3. Install and restart

---

## ✅ Verification

After installation, verify everything works:

1. **Launch Android Studio**
2. **Open the project** in mobile-app/
3. **Check for errors** in the Build tab
4. **Wait for sync** to complete
5. **Check that you can see the project files** in the Project view

If everything looks good, you're ready to go! 🎉

---

## 🆘 Troubleshooting

### "JDK not found"
- Download JDK 17 from: https://adoptium.net/
- Install it
- Restart Android Studio

### "SDK not found"
- In Android Studio: **File** → **Settings** → **Appearance & Behavior** → **System Settings** → **Android SDK**
- Select an SDK location
- Android Studio will download the SDK

### "Gradle sync failed"
- Check internet connection
- Try: **File** → **Invalidate Caches** → **Invalidate and Restart**
- Or manually sync: **File** → **Sync Project with Gradle Files**

---

## 📚 Next Steps

Once Android Studio is installed:

1. Follow [QUICK_START.md](../setup/QUICK_START.md) to open the project
2. Configure BASE_URL for your backend
3. Create/start an emulator
4. Run the app!

---

**Need Help?**
- Android Studio Install Guide: https://developer.android.com/studio/install
- Community Support: https://stackoverflow.com/questions/tagged/android-studio
