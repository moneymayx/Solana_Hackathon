# Banner Images Guide

## Overview
This guide explains how to easily change the scrolling banner images in the Billions Bounty frontend application.

## Current Banner Images

The scrolling banner displays 6 different slides with the following images:

| Slide | Image File | Description | Display Text |
|-------|------------|-------------|--------------|
| 1 | `claude-ai.svg` | Claude Challenge | "The Smartest AI" |
| 2 | `mobile-app.svg` | Download App | "Play Anywhere" |
| 3 | `referral-bonus.svg` | Referral Program | "Win 5 Free Questions" |
| 4 | `gpt-4.svg` | GPT-4 Bounty | "The Creative Genius" |
| 5 | `gemini-ai.svg` | Gemini Quest | "The Multimodal Master" |
| 6 | `llama-ai.svg` | Llama Legend | "The Open Source Hero" |

## Image Location

All banner images are stored in:
```
frontend/public/images/
```

## How to Change Images

### Method 1: Replace Existing Images (Recommended)

1. **Navigate to the images directory:**
   ```bash
   cd frontend/public/images/
   ```

2. **Replace the image file:**
   - Keep the same filename (e.g., `claude-ai.svg`)
   - Replace the file content with your new image
   - Supported formats: `.svg`, `.jpg`, `.png`, `.webp`

3. **No code changes needed** - the application will automatically use the new image

### Method 2: Add New Images

1. **Add your new image file:**
   ```bash
   # Example: Adding a new Claude image
   cp your-new-claude-image.svg frontend/public/images/claude-ai-new.svg
   ```

2. **Update the component code:**
   - Open `frontend/src/components/ScrollingBanner.tsx`
   - Find the slides array (around line 15)
   - Update the `image` property for the desired slide:

   ```typescript
   // Example: Changing Claude's image
   {
     id: 1,
     type: 'jackpot',
     title: 'Claude Challenge',
     subtitle: 'The Smartest AI',
     description: 'Think you can outsmart the most advanced AI?',
     prize: '$1,000',
     image: '/images/claude-ai-new.svg', // ← Changed this line
     bgGradient: 'from-yellow-400 via-orange-500 to-red-500',
     textColor: 'text-slate-900'
   }
   ```

## Image Specifications

### Recommended Dimensions
- **Aspect Ratio:** 4:3 (400x300px or similar)
- **Format:** SVG preferred for scalability, but JPG/PNG work too
- **File Size:** Keep under 500KB for optimal loading

### Design Guidelines
- **Background:** Should work well with dark overlays (opacity 20%)
- **Content:** Should be visible when overlaid with semi-transparent dark background
- **Style:** Match the Jackpot.com lottery aesthetic with vibrant colors
- **Text Overlay:** Images will have text overlaid, so avoid busy backgrounds in the center

## Current Image Structure

Each SVG image follows this structure:
```svg
<svg width="400" height="300" viewBox="0 0 400 300">
  <!-- Gradient background -->
  <defs>
    <linearGradient id="uniqueGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#COLOR1;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#COLOR2;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#COLOR3;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background -->
  <rect width="400" height="300" fill="url(#uniqueGrad)"/>
  
  <!-- Main content circle -->
  <circle cx="200" cy="150" r="80" fill="white" opacity="0.9"/>
  
  <!-- Emoji or icon -->
  <text x="200" y="160" text-anchor="middle" font-size="60">🤖</text>
  
  <!-- Title -->
  <text x="200" y="200" text-anchor="middle" font-size="24" fill="white">Title</text>
  
  <!-- Subtitle -->
  <text x="200" y="230" text-anchor="middle" font-size="16" fill="white" opacity="0.9">Subtitle</text>
</svg>
```

## Quick Image Updates

### For Claude Challenge (Slide 1)
```bash
# Replace the image
cp your-claude-image.svg frontend/public/images/claude-ai.svg
```

### For Mobile App (Slide 2)
```bash
# Replace the image
cp your-mobile-image.svg frontend/public/images/mobile-app.svg
```

### For Referral Bonus (Slide 3)
```bash
# Replace the image
cp your-referral-image.svg frontend/public/images/referral-bonus.svg
```

### For GPT-4 Bounty (Slide 4)
```bash
# Replace the image
cp your-gpt4-image.svg frontend/public/images/gpt-4.svg
```

### For Gemini Quest (Slide 5)
```bash
# Replace the image
cp your-gemini-image.svg frontend/public/images/gemini-ai.svg
```

### For Llama Legend (Slide 6)
```bash
# Replace the image
cp your-llama-image.svg frontend/public/images/llama-ai.svg
```

## Testing Your Changes

1. **Start the development server:**
   ```bash
   cd frontend
   npm run dev
   ```

2. **View the changes:**
   - Open `http://localhost:3001` (or the port shown in terminal)
   - Scroll to the banner section
   - Wait for the auto-scroll to cycle through all slides
   - Click the slide indicators to manually navigate

3. **Check mobile view:**
   - Use browser dev tools to test mobile responsiveness
   - Ensure images scale properly on different screen sizes

## Troubleshooting

### Image Not Loading
- Check file path is correct: `frontend/public/images/`
- Verify file permissions
- Check browser console for 404 errors
- Ensure image format is supported

### Image Quality Issues
- Use higher resolution source images
- Optimize file size if loading is slow
- Check aspect ratio matches 4:3

### Styling Issues
- Ensure image works with dark overlay
- Test with different text overlays
- Verify colors match the overall theme

## Advanced Customization

### Changing Slide Content
To modify the text, titles, or descriptions, edit `frontend/src/components/ScrollingBanner.tsx`:

```typescript
const slides = [
  {
    id: 1,
    type: 'jackpot',
    title: 'Your Custom Title',        // ← Change this
    subtitle: 'Your Custom Subtitle',  // ← Change this
    description: 'Your custom description...', // ← Change this
    prize: '$1,000',                   // ← Change this
    image: '/images/your-image.svg',   // ← Change this
    bgGradient: 'from-yellow-400 via-orange-500 to-red-500', // ← Change this
    textColor: 'text-slate-900'        // ← Change this
  },
  // ... other slides
]
```

### Adding New Slides
1. Add a new image to `frontend/public/images/`
2. Add a new slide object to the `slides` array
3. Update the slide indicators and progress bar (handled automatically)

### Changing Animation Speed
Modify the auto-scroll interval in `ScrollingBanner.tsx`:
```typescript
// Change from 4000ms (4 seconds) to your preferred duration
const interval = setInterval(() => {
  setCurrentSlide((prev) => (prev + 1) % slides.length)
}, 3000) // ← 3 seconds instead of 4
```

## File Structure Reference

```
frontend/
├── public/
│   └── images/
│       ├── claude-ai.svg      # Slide 1: Claude Challenge
│       ├── mobile-app.svg     # Slide 2: Download App
│       ├── referral-bonus.svg # Slide 3: Referral Program
│       ├── gpt-4.svg          # Slide 4: GPT-4 Bounty
│       ├── gemini-ai.svg      # Slide 5: Gemini Quest
│       └── llama-ai.svg       # Slide 6: Llama Legend
└── src/
    └── components/
        └── ScrollingBanner.tsx # Main banner component
```

## Support

If you encounter issues:
1. Check the browser console for errors
2. Verify file paths and permissions
3. Test with different image formats
4. Ensure the development server is running
5. Check that images are in the correct `public/images/` directory

---

**Last Updated:** January 2025  
**Version:** 1.0  
**Maintainer:** Development Team
