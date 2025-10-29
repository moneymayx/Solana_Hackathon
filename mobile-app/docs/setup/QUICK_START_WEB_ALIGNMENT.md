# 🚀 Quick Start: Android App Web Alignment

Your Android app has been updated to match the web frontend! Follow these simple steps to get started.

## ⚡ Fast Track (3 Steps)

### Step 1: Copy Images (2 minutes)
```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/mobile-app
./copy_images.sh
```

This automated script copies all required images from the frontend to the Android app.

### Step 2: Convert SVG Logos (2 minutes)
The AI provider logos need conversion from SVG to PNG:

**Option A - Online (Easiest)**:
1. Go to https://cloudconvert.com/svg-to-png
2. Upload `frontend/public/images/logos/claude-ai.svg`
3. Set size to 128x128, convert, download as `claude_ai.png`
4. Repeat for `gpt-4.svg`, `gemini-ai.svg`, `llama-ai.svg`
5. Save to `mobile-app/app/src/main/res/drawable/`

**Option B - Command Line** (if you have ImageMagick):
```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/frontend/public/images/logos
convert claude-ai.svg -resize 128x128 -background none ../../../../mobile-app/app/src/main/res/drawable/claude_ai.png
convert gpt-4.svg -resize 128x128 -background none ../../../../mobile-app/app/src/main/res/drawable/gpt_4.png
convert gemini-ai.svg -resize 128x128 -background none ../../../../mobile-app/app/src/main/res/drawable/gemini_ai.png
convert llama-ai.svg -resize 128x128 -background none ../../../../mobile-app/app/src/main/res/drawable/llama_ai.png
```

### Step 3: Test the App
```bash
# Terminal 1: Start backend
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate
python3 -m uvicorn apps.backend.main:app --reload --port 8000

# Terminal 2: Open in Android Studio and run
# The app will connect to your backend automatically
```

## ✅ What's New

Your Android app now matches the website with:

### 🎨 Visual Design
- ✅ White header with gray border
- ✅ Yellow accent colors (#EAB308)
- ✅ Crown/Star logo
- ✅ Clean, modern typography

### 📱 Layout Structure
- ✅ **Hero**: "Beat the Bot, Win the Pot" above banner
- ✅ **Banner**: Auto-sliding carousel (4 sec intervals)
- ✅ **Bounties**: Grid with live API data
- ✅ **How It Works**: 5 steps + 3 feature cards
- ✅ **Winners**: Dark gradient with carousel
- ✅ **FAQ**: 6 collapsible items
- ✅ **Footer**: Educational disclaimer

### 🔧 Technical Features
- ✅ API integration (`http://localhost:8000/api/bounties`)
- ✅ Loading states and error handling
- ✅ Auto-scroll animations
- ✅ Collapsible FAQ items
- ✅ Bounty cards with provider colors
- ✅ Difficulty badges (Easy, Medium, Hard, Expert)

## 🎯 Testing Physical Device

To test on your phone instead of emulator:

1. Find your computer's local IP:
   ```bash
   # Mac
   ipconfig getifaddr en0
   
   # Output example: 192.168.1.100
   ```

2. Update the API endpoint in Android Studio:
   - Open: `mobile-app/app/src/main/java/com/billionsbounty/mobile/di/NetworkModule.kt`
   - Change line 36:
     ```kotlin
     private const val BASE_URL = "http://192.168.1.100:8000/"  // Use your IP
     ```

3. Make sure your phone and computer are on the same WiFi network

4. Run the app on your phone

## 📚 Documentation

Detailed guides available:
- **ANDROID_WEB_ALIGNMENT_COMPLETE.md** - Full implementation details
- **IMAGE_SETUP_INSTRUCTIONS.md** - Manual image copying guide
- **SVG_TO_PNG_CONVERSION_GUIDE.md** - SVG conversion options
- **copy_images.sh** - Automated image copy script

## 🔍 Verify Installation

After running `copy_images.sh`, check you have these files:
```bash
ls -1 app/src/main/res/drawable/

# Should show:
# ai_logo.png
# billions_app_banner.jpg
# claude_champion_banner.jpg
# winner_claude_champ.png
# winner_gemini_giant.png
# winner_gpt_goon.png
# winner_llama_legend.png
# (plus the 4 converted SVG logos once you add them)
```

## ⚠️ Troubleshooting

### App won't connect to backend
- Check backend is running: `curl http://localhost:8000/api/bounties`
- For emulator, use: `http://10.0.2.2:8000/`
- For device, use your computer's IP: `http://192.168.X.X:8000/`

### Images not showing
- Run `./copy_images.sh` again
- Check images are in `app/src/main/res/drawable/`
- File names must be lowercase with underscores (no hyphens)

### Build errors in Android Studio
- Click "Sync Project with Gradle Files"
- Clean build: **Build → Clean Project**
- Rebuild: **Build → Rebuild Project**

### SVG conversion issues
- See **SVG_TO_PNG_CONVERSION_GUIDE.md** for multiple methods
- Or use online tool: https://cloudconvert.com/svg-to-png
- App works without logos (shows placeholders)

## 🎉 Success Indicators

You'll know it's working when you see:
1. ✅ White header at top with "BILLION$" text
2. ✅ "Beat the Bot, Win the Pot" centered above banner
3. ✅ Auto-sliding banner changing every 4 seconds
4. ✅ Bounty cards loading from API with colors and amounts
5. ✅ "How It Works" section with 5 numbered steps
6. ✅ Dark blue/green gradient Winners section
7. ✅ FAQ items that expand when tapped
8. ✅ Footer with legal disclaimer

## 🚦 Quick Status Check

Run this command to verify your setup:
```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/mobile-app

echo "Checking setup..."
echo ""

# Check drawable folder exists
if [ -d "app/src/main/res/drawable" ]; then
    echo "✓ Drawable folder exists"
    echo "  Files found: $(ls -1 app/src/main/res/drawable | wc -l)"
else
    echo "✗ Drawable folder missing"
fi

# Check backend
if curl -s http://localhost:8000/api/bounties > /dev/null; then
    echo "✓ Backend is running"
else
    echo "✗ Backend not responding (start it first)"
fi

# Check required files
if [ -f "copy_images.sh" ]; then
    echo "✓ copy_images.sh ready"
else
    echo "✗ copy_images.sh missing"
fi

echo ""
echo "Ready to go? Run: ./copy_images.sh"
```

## 📱 Need Help?

1. Check **ANDROID_WEB_ALIGNMENT_COMPLETE.md** for detailed explanations
2. Review Android Studio build output for specific errors
3. Verify backend logs for API connection issues
4. Check that images are properly named (lowercase, underscores only)

---

**That's it!** Your Android app now looks and feels like the website. 🎊

