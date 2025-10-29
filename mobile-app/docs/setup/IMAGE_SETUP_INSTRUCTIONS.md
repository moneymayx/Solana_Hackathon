# Image Assets Setup Instructions

## Overview
Copy these images from the web frontend to the Android app's drawable folder to ensure visual consistency between platforms.

## Source Directory
`/Users/jaybrantley/myenv/Hackathon/Billions_Bounty/frontend/public/images/`

## Destination Directory
`/Users/jaybrantley/myenv/Hackathon/Billions_Bounty/mobile-app/app/src/main/res/drawable/`

## Required Images

### 1. AI Logo
- **Source**: `ai-logo.PNG`
- **Destination**: `ai_logo.png`
- **Usage**: How It Works section illustration

### 2. Banner Images
- **Source**: `claude-champion-banner.jpg`
- **Destination**: `claude_champion_banner.jpg`
- **Usage**: Scrolling banner carousel

- **Source**: `billions-app-banner.JPEG`
- **Destination**: `billions_app_banner.jpg`
- **Usage**: Scrolling banner carousel

### 3. AI Provider Logos (SVG → PNG conversion needed)
Convert these SVG files to PNG format (recommend 128x128px or use vector drawable XML):

- **Source**: `logos/claude-ai.svg`
- **Destination**: `claude_ai.png`

- **Source**: `logos/gpt-4.svg`
- **Destination**: `gpt_4.png`

- **Source**: `logos/gemini-ai.svg`
- **Destination**: `gemini_ai.png`

- **Source**: `logos/llama-ai.svg`
- **Destination**: `llama_ai.png`

### 4. Winner Images
- **Source**: `winners/Claude-champ.png`
- **Destination**: `winner_claude_champ.png`

- **Source**: `winners/GPT-goon.png`
- **Destination**: `winner_gpt_goon.png`

- **Source**: `winners/Gemini_giant.png`
- **Destination**: `winner_gemini_giant.png`

- **Source**: `winners/llama-legend.png`
- **Destination**: `winner_llama_legend.png`

## Important Notes

1. **Naming Convention**: Android requires lowercase filenames with underscores (no hyphens, no uppercase)

2. **SVG Conversion**: 
   - Option A: Use online converter (https://cloudconvert.com/svg-to-png)
   - Option B: Use Android Studio's Vector Asset wizard to convert SVG to Vector Drawable XML
   - Option C: Use ImageMagick: `convert input.svg -resize 128x128 output.png`

3. **File Formats**: 
   - PNG files can be copied directly (just rename to lowercase with underscores)
   - JPEG/JPG files can be copied directly

4. **Create drawable folder if needed**:
   ```bash
   mkdir -p /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/mobile-app/app/src/main/res/drawable
   ```

## Quick Copy Commands

```bash
# Navigate to mobile app directory
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/mobile-app/app/src/main/res

# Create drawable directory if it doesn't exist
mkdir -p drawable

# Copy and rename images (adjust paths as needed)
cp ../../../../../../../frontend/public/images/ai-logo.PNG drawable/ai_logo.png
cp ../../../../../../../frontend/public/images/claude-champion-banner.jpg drawable/claude_champion_banner.jpg
cp ../../../../../../../frontend/public/images/billions-app-banner.JPEG drawable/billions_app_banner.jpg

# Copy winner images
cp ../../../../../../../frontend/public/images/winners/Claude-champ.png drawable/winner_claude_champ.png
cp ../../../../../../../frontend/public/images/winners/GPT-goon.png drawable/winner_gpt_goon.png
cp ../../../../../../../frontend/public/images/winners/Gemini_giant.png drawable/winner_gemini_giant.png
cp ../../../../../../../frontend/public/images/winners/llama-legend.png drawable/winner_llama_legend.png
```

## Verification

After copying, verify all files are in place:
```bash
ls -la /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/mobile-app/app/src/main/res/drawable/
```

You should see all the renamed image files listed above.



