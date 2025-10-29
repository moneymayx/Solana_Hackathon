# SVG to PNG Conversion Guide for Android

## Why Convert SVG to PNG?

Android's `drawable` folder typically uses PNG images or XML vector drawables. The AI provider logos in the web frontend are SVG files, which need to be converted for Android use.

## Option 1: Quick Online Conversion (Easiest)

### CloudConvert (Recommended)
1. Visit: https://cloudconvert.com/svg-to-png
2. Upload the SVG file
3. Set dimensions: 128x128 or 256x256 pixels
4. Click "Convert"
5. Download the PNG
6. Rename to lowercase with underscores (e.g., `claude_ai.png`)

### Alternative Online Tools
- https://svgtopng.com/
- https://convertio.co/svg-png/
- https://www.zamzar.com/convert/svg-to-png/

## Option 2: Using Command Line (Mac/Linux)

### Install ImageMagick (if not installed)
```bash
# Mac
brew install imagemagick

# Ubuntu/Debian
sudo apt-get install imagemagick
```

### Convert SVGs to PNG
```bash
# Navigate to the logos directory
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/frontend/public/images/logos

# Convert all SVGs at once (128x128 size)
for file in *.svg; do
    convert "$file" -resize 128x128 "${file%.svg}.png"
done

# Or convert individually
convert claude-ai.svg -resize 128x128 claude-ai.png
convert gpt-4.svg -resize 128x128 gpt-4.png
convert gemini-ai.svg -resize 128x128 gemini-ai.png
convert llama-ai.svg -resize 128x128 llama-ai.png
```

### Then rename for Android
```bash
# Rename to Android-friendly names
mv claude-ai.png claude_ai.png
mv gpt-4.png gpt_4.png
mv gemini-ai.png gemini_ai.png
mv llama-ai.png llama_ai.png
```

## Option 3: Using Android Studio (Best for Vector Drawables)

This creates XML vector drawables instead of PNGs, which scale better:

1. Open Android Studio
2. Right-click on `res/drawable` folder
3. Select **New → Vector Asset**
4. Choose **Local file (SVG, PSD)**
5. Browse to your SVG file
6. Click **Next**, then **Finish**
7. Android Studio creates an XML vector drawable

**Advantages**:
- Scalable to any size without quality loss
- Smaller file size
- Native Android format

**Note**: This only works if the SVG is simple. Complex SVGs may need PNG conversion instead.

## Recommended Sizes

For Android app icons/logos:
- **Small icons**: 48x48 or 64x64 dp
- **Medium icons**: 128x128 dp (recommended for this project)
- **Large icons**: 256x256 dp

Use `@2x` or `@3x` versions for high-DPI screens if desired.

## Quick Batch Conversion Script

Save this as `convert_svgs.sh`:

```bash
#!/bin/bash

# Directories
SOURCE_DIR="/Users/jaybrantley/myenv/Hackathon/Billions_Bounty/frontend/public/images/logos"
DEST_DIR="/Users/jaybrantley/myenv/Hackathon/Billions_Bounty/mobile-app/app/src/main/res/drawable"

# Create destination if it doesn't exist
mkdir -p "$DEST_DIR"

# Convert and rename
convert "$SOURCE_DIR/claude-ai.svg" -resize 128x128 "$DEST_DIR/claude_ai.png"
convert "$SOURCE_DIR/gpt-4.svg" -resize 128x128 "$DEST_DIR/gpt_4.png"
convert "$SOURCE_DIR/gemini-ai.svg" -resize 128x128 "$DEST_DIR/gemini_ai.png"
convert "$SOURCE_DIR/llama-ai.svg" -resize 128x128 "$DEST_DIR/llama_ai.png"

echo "✓ SVG to PNG conversion complete!"
echo "Files created in: $DEST_DIR"
```

Make executable and run:
```bash
chmod +x convert_svgs.sh
./convert_svgs.sh
```

## Verification

After conversion, verify the files:

```bash
ls -lh /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/mobile-app/app/src/main/res/drawable/

# You should see:
# claude_ai.png
# gpt_4.png
# gemini_ai.png
# llama_ai.png
```

## Alternative: Use Fallback Icons

If SVG conversion is problematic, the app code can fall back to:
- Material Icons from Compose
- Colored boxes with text
- Unicode emoji representations

The current implementation will work without these images (showing placeholders).

## Troubleshooting

### ImageMagick "no decode delegate" error
```bash
# Install librsvg
brew install librsvg  # Mac
sudo apt-get install librsvg2-bin  # Linux
```

### File too large
Reduce dimensions:
```bash
convert input.svg -resize 64x64 output.png
```

### Transparent background becomes black
Add this flag:
```bash
convert input.svg -resize 128x128 -background none output.png
```

## Summary

**Easiest Method**: Use CloudConvert online tool (no installation required)
**Best Quality**: Use Android Studio's Vector Asset tool
**Most Automated**: Use the bash script above (requires ImageMagick)

Choose the method that works best for your setup!



