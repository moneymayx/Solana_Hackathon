# Banner Images Management

## 📁 Files Created

1. **`BANNER_IMAGES_GUIDE.md`** - Comprehensive guide with detailed instructions
2. **`QUICK_IMAGE_REFERENCE.md`** - Quick reference for common tasks
3. **`update-banner-images.sh`** - Automated script for easy image updates
4. **`README_BANNER_IMAGES.md`** - This summary file

## 🚀 Quick Start

### Method 1: Direct File Replacement (Simplest)
```bash
# Navigate to images directory
cd frontend/public/images/

# Replace any image (keep the same filename)
cp your-new-claude-image.svg claude-ai.svg
cp your-new-mobile-image.svg mobile-app.svg
# ... etc for other images
```

### Method 2: Using the Script (Recommended)
```bash
# Navigate to frontend directory
cd frontend

# Update a specific slide
./update-banner-images.sh update 1 your-new-claude-image.svg

# Interactive mode
./update-banner-images.sh interactive

# List available slides
./update-banner-images.sh list
```

## 📋 Available Slides

| # | File | Description | Type |
|---|------|-------------|------|
| 1 | `claude-ai.svg` | Claude Challenge | Jackpot Game |
| 2 | `mobile-app.svg` | Download App | Download |
| 3 | `referral-bonus.svg` | Referral Program | Special Offer |
| 4 | `gpt-4.svg` | GPT-4 Bounty | Jackpot Game |
| 5 | `gemini-ai.svg` | Gemini Quest | Jackpot Game |
| 6 | `llama-ai.svg` | Llama Legend | Jackpot Game |

## 🎨 Image Requirements

- **Format:** SVG preferred, JPG/PNG accepted
- **Size:** 400x300px (4:3 aspect ratio)
- **File Size:** Under 500KB
- **Location:** `frontend/public/images/`
- **Style:** Should work with dark overlay (opacity 20%)

## 🔧 Script Commands

```bash
# Show help
./update-banner-images.sh help

# List all slides
./update-banner-images.sh list

# Update slide 1 (Claude) with new image
./update-banner-images.sh update 1 /path/to/new/image.svg

# Restore slide 1 from backup
./update-banner-images.sh restore 1

# List all backups
./update-banner-images.sh backups

# Interactive mode
./update-banner-images.sh interactive
```

## 📖 Documentation

- **Full Guide:** `BANNER_IMAGES_GUIDE.md` - Complete instructions with examples
- **Quick Reference:** `QUICK_IMAGE_REFERENCE.md` - Fast lookup for common tasks
- **This File:** `README_BANNER_IMAGES.md` - Overview and quick start

## 🐛 Troubleshooting

**Image not showing?**
- Check file is in `frontend/public/images/`
- Verify filename matches exactly
- Refresh browser (Ctrl+F5 or Cmd+Shift+R)

**Script not working?**
- Make sure you're in the `frontend/` directory
- Check file permissions: `chmod +x update-banner-images.sh`
- Verify bash version supports the script

**Wrong image size/quality?**
- Use 400x300px images
- SVG format for best quality
- Check file size < 500KB

## 🎯 Next Steps

1. **Test the current setup:**
   ```bash
   cd frontend
   npm run dev
   # Open http://localhost:3001 and check the banner
   ```

2. **Update images as needed:**
   - Use the script for easy updates
   - Or directly replace files in `public/images/`

3. **Customize content:**
   - Edit `src/components/ScrollingBanner.tsx` to change text
   - Modify slide titles, descriptions, and prizes

4. **Add new slides:**
   - Add image to `public/images/`
   - Update the `slides` array in `ScrollingBanner.tsx`

---

**Created:** January 2025  
**Last Updated:** January 2025  
**Status:** Ready to use ✅
