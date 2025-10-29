# Quick Image Reference

## 🚀 Quick Commands

### Update a single image:
```bash
# Method 1: Direct file replacement
cp your-new-image.svg frontend/public/images/claude-ai.svg

# Method 2: Using the script
cd frontend
./update-banner-images.sh update 1 your-new-image.svg
```

### Interactive mode:
```bash
cd frontend
./update-banner-images.sh interactive
```

## 📁 Image Files

| Slide | File | Description |
|-------|------|-------------|
| 1 | `claude-ai.svg` | Claude Challenge |
| 2 | `mobile-app.svg` | Download App |
| 3 | `referral-bonus.svg` | Referral Program |
| 4 | `gpt-4.svg` | GPT-4 Bounty |
| 5 | `gemini-ai.svg` | Gemini Quest |
| 6 | `llama-ai.svg` | Llama Legend |

## 🎨 Image Specs

- **Size:** 400x300px (4:3 ratio)
- **Format:** SVG preferred, JPG/PNG OK
- **Location:** `frontend/public/images/`
- **Max Size:** 500KB

## 🔧 Common Tasks

### Replace all images at once:
```bash
cd frontend/public/images/
cp /path/to/new/claude.svg claude-ai.svg
cp /path/to/new/mobile.svg mobile-app.svg
cp /path/to/new/referral.svg referral-bonus.svg
cp /path/to/new/gpt4.svg gpt-4.svg
cp /path/to/new/gemini.svg gemini-ai.svg
cp /path/to/new/llama.svg llama-ai.svg
```

### Create backup before changes:
```bash
cd frontend/public/images/
cp claude-ai.svg claude-ai.svg.backup
cp mobile-app.svg mobile-app.svg.backup
# ... repeat for other images
```

### Restore from backup:
```bash
cd frontend/public/images/
cp claude-ai.svg.backup claude-ai.svg
```

## 🐛 Troubleshooting

**Image not showing?**
- Check file is in `frontend/public/images/`
- Verify filename matches exactly
- Refresh browser (Ctrl+F5)

**Wrong size/quality?**
- Use 400x300px images
- SVG format for best quality
- Check file size < 500KB

**Need to change text?**
- Edit `frontend/src/components/ScrollingBanner.tsx`
- Look for the `slides` array around line 15
