# Official AI Model Logos Guide

## Download Official Logos

Please download the official PNG logos from these sources and save them in `/public/images/logos/`:

### 1. Claude AI (Anthropic)
- **Source**: https://www.anthropic.com/press-kit
- **File**: Save as `claude-ai.png`
- **Recommended size**: 64x64px or 128x128px

### 2. GPT-4 (OpenAI)
- **Source**: https://openai.com/press-kit
- **File**: Save as `gpt-4.png`
- **Recommended size**: 64x64px or 128x128px

### 3. Gemini (Google)
- **Source**: https://ai.google/press-kit
- **File**: Save as `gemini-ai.png`
- **Recommended size**: 64x64px or 128x128px

### 4. LLaMA (Meta)
- **Source**: https://ai.facebook.com/press-kit
- **File**: Save as `llama-ai.png`
- **Recommended size**: 64x64px or 128x128px

## File Structure
```
public/images/logos/
├── claude-ai.png
├── gpt-4.png
├── gemini-ai.png
└── llama-ai.png
```

## Usage in Components

The components are already configured to use these logos. Once you add the PNG files, they will automatically be used instead of the SVG placeholders.

### Current Implementation
- **Bounty Cards**: Uses logos in the header section
- **Scrolling Banner**: Uses logos in the banner slides
- **Model Difficulty**: Uses logos in the rankings display

### Image Optimization
- Use PNG format for best quality
- Optimize file sizes (aim for <50KB each)
- Ensure consistent dimensions across all logos
- Use transparent backgrounds where possible

## Legal Considerations
- Ensure you have permission to use these logos
- Follow each company's brand guidelines
- Use logos only for legitimate purposes
- Consider trademark and copyright restrictions
