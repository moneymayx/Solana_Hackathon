#!/bin/bash

# ============================================================================
# Android App - Image Asset Copy Script
# ============================================================================
# This script copies and renames images from the web frontend to the Android
# app's drawable folder, following Android naming conventions.
# ============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
SOURCE_DIR="$PROJECT_ROOT/Billions_Bounty/frontend/public/images"
DEST_DIR="$SCRIPT_DIR/app/src/main/res/drawable"

echo "============================================================================"
echo "Android App - Image Asset Copy Script"
echo "============================================================================"
echo ""

# Create destination directory if it doesn't exist
echo -e "${YELLOW}Creating drawable directory...${NC}"
mkdir -p "$DEST_DIR"
echo -e "${GREEN}✓ Drawable directory ready${NC}"
echo ""

# Function to copy and rename file
copy_image() {
    local source_file="$1"
    local dest_name="$2"
    
    if [ -f "$source_file" ]; then
        cp "$source_file" "$DEST_DIR/$dest_name"
        echo -e "${GREEN}✓${NC} Copied: $dest_name"
        return 0
    else
        echo -e "${RED}✗${NC} Not found: $source_file"
        return 1
    fi
}

# Track statistics
total=0
success=0
failed=0

# Copy AI Logo
echo "Copying AI Logo..."
total=$((total + 1))
if copy_image "$SOURCE_DIR/ai-logo.PNG" "ai_logo.png"; then
    success=$((success + 1))
else
    failed=$((failed + 1))
fi
echo ""

# Copy Banner Images
echo "Copying Banner Images..."
total=$((total + 2))
if copy_image "$SOURCE_DIR/claude-champion-banner.jpg" "claude_champion_banner.jpg"; then
    success=$((success + 1))
else
    failed=$((failed + 1))
fi
if copy_image "$SOURCE_DIR/billions-app-banner.JPEG" "billions_app_banner.jpg"; then
    success=$((success + 1))
else
    failed=$((failed + 1))
fi
echo ""

# Copy Winner Images
echo "Copying Winner Images..."
total=$((total + 4))
if copy_image "$SOURCE_DIR/winners/Claude-champ.png" "winner_claude_champ.png"; then
    success=$((success + 1))
else
    failed=$((failed + 1))
fi
if copy_image "$SOURCE_DIR/winners/GPT-goon.png" "winner_gpt_goon.png"; then
    success=$((success + 1))
else
    failed=$((failed + 1))
fi
if copy_image "$SOURCE_DIR/winners/Gemini_giant.png" "winner_gemini_giant.png"; then
    success=$((success + 1))
else
    failed=$((failed + 1))
fi
if copy_image "$SOURCE_DIR/winners/llama-legend.png" "winner_llama_legend.png"; then
    success=$((success + 1))
else
    failed=$((failed + 1))
fi
echo ""

# SVG Files - Check if they exist
echo "============================================================================"
echo "SVG Files (AI Provider Logos)"
echo "============================================================================"
echo ""
echo -e "${YELLOW}Note: SVG files need to be converted to PNG format${NC}"
echo "The following SVG files were found and need conversion:"
echo ""

svg_found=0
if [ -f "$SOURCE_DIR/logos/claude-ai.svg" ]; then
    echo -e "${YELLOW}!${NC} Found: claude-ai.svg → needs conversion to claude_ai.png"
    svg_found=$((svg_found + 1))
fi
if [ -f "$SOURCE_DIR/logos/gpt-4.svg" ]; then
    echo -e "${YELLOW}!${NC} Found: gpt-4.svg → needs conversion to gpt_4.png"
    svg_found=$((svg_found + 1))
fi
if [ -f "$SOURCE_DIR/logos/gemini-ai.svg" ]; then
    echo -e "${YELLOW}!${NC} Found: gemini-ai.svg → needs conversion to gemini_ai.png"
    svg_found=$((svg_found + 1))
fi
if [ -f "$SOURCE_DIR/logos/llama-ai.svg" ]; then
    echo -e "${YELLOW}!${NC} Found: llama-ai.svg → needs conversion to llama_ai.png"
    svg_found=$((svg_found + 1))
fi

if [ $svg_found -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}Please convert these SVG files using one of these methods:${NC}"
    echo "  1. Use CloudConvert: https://cloudconvert.com/svg-to-png"
    echo "  2. Run: convert logo.svg -resize 128x128 logo.png (requires ImageMagick)"
    echo "  3. Use Android Studio's Vector Asset tool"
    echo ""
    echo "See SVG_TO_PNG_CONVERSION_GUIDE.md for detailed instructions"
fi

echo ""
echo "============================================================================"
echo "Summary"
echo "============================================================================"
echo ""
echo "Total files attempted: $total"
echo -e "${GREEN}Successfully copied: $success${NC}"
if [ $failed -gt 0 ]; then
    echo -e "${RED}Failed to copy: $failed${NC}"
fi
if [ $svg_found -gt 0 ]; then
    echo -e "${YELLOW}SVG files requiring conversion: $svg_found${NC}"
fi
echo ""

# List copied files
echo "Files in drawable folder:"
ls -lh "$DEST_DIR" 2>/dev/null || echo "No files yet"
echo ""

if [ $success -eq $total ]; then
    echo -e "${GREEN}✓ All PNG images copied successfully!${NC}"
    if [ $svg_found -gt 0 ]; then
        echo -e "${YELLOW}⚠ Don't forget to convert the SVG files${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Some files could not be copied${NC}"
    echo "Check that the source images exist in:"
    echo "$SOURCE_DIR"
fi

echo ""
echo "============================================================================"
echo "Next Steps:"
echo "============================================================================"
echo "1. Convert SVG logos to PNG (see SVG_TO_PNG_CONVERSION_GUIDE.md)"
echo "2. Start your backend server: python3 -m uvicorn apps.backend.main:app --reload"
echo "3. Open project in Android Studio"
echo "4. Run the app on emulator or device"
echo ""
echo "See ANDROID_WEB_ALIGNMENT_COMPLETE.md for full testing checklist"
echo "============================================================================"



