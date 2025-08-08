---
applyTo: '**'
---

# Copilot Instructions for Social Post Generator

## Core Development Principles
- **Clean, intuitive UI**: Minimize clutter, avoid popups, focus on streamlined workflow
- **Modular architecture**: Maintain current module-based structure
- **Professional appearance**: No emojis in UI, clean business-focused design
- **Mobile responsive**: Ensure all features work on mobile devices
- **Performance focused**: Efficient code with proper error handling

## Default Settings & Behavior
- **Default AI Model**: Always default to GPT-4o-mini (cost-effective)
- **Caption Length**: Default to "2-3 sentences" 
- **Caption Style**: Generate clean, engaging content without hashtags or emojis
- **UI Layout**: Single page with collapsible sections to reduce clutter

## Required Feature Implementation

### 1. AI Model Settings (Left Sidebar - 3rd section)
- Add "AI Model" as third section in sidebar (below Company, above Actions)
- Hard default to GPT-4o-mini
- Allow switching to GPT-4o for premium quality
- Show current model selection clearly

### 2. Image Processing Integration (Main Page)
- **Collapsible section**: "Image Upload & Processing" 
- **Features to include**:
  - Image upload with drag & drop
  - Real-time image preview
  - Batch processing capabilities
- **Location**: Right after business details section
- **Default state**: Collapsed to reduce clutter

### 3. Platform Character Limits (Caption Generation Section)
- **Dropdown selector** in "Generate Social Media Captions" section
- **Options**:
  - "2-3 sentences (default)" 
  - "Twitter/X (≤280 chars)"
  - "Instagram (≤2,200 chars)"
  - "LinkedIn (≤3,000 chars)"
  - "Facebook (longer form)"
- **Real-time character counting** for generated captions
- **Visual indicators** when caption exceeds platform limits (clean design)
- **Platform presets**: Automatically adjust both caption length AND image dimensions

### 4. Optimal User Workflow
1. Enter website URL → auto-populate business info
2. Fill in business details
3. Optionally add/edit image in collapsible section
4. Adjust caption settings if needed (platform limits, style)
5. Generate captions with real-time character feedback
6. Copy/download results

## UI Layout Requirements
- **Single page design**: No popup windows or modals
- **Collapsible sections**: Use st.expander for optional features (reset each session)
- **Clean hierarchy**: Website → Business Info → Image (optional) → Generate
- **Intuitive defaults**: Everything should work with minimal configuration
- **Clean character counting**: Visual indicators that don't clutter the interface

## Code Integration Notes
- Image processing classes exist in `modules/image_processing.py` but need UI integration
- Add clipboard functionality using available streamlit libraries (remove if problematic)
- Implement character counting with platform-specific color coding
- Maintain current modular structure while adding UI components
- Collapsible sections should reset state each session

## Prohibited Elements
- No emojis in UI elements (buttons, headers, messages)
- No automatic hashtag generation
- No popup windows or complex modal dialogs
- Avoid feature creep that clutters the interface