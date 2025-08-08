#!/usr/bin/env python3
"""
Configuration constants for the Social Post Generator application.
"""

import os

# === File Configurations ===
# Data file configurations - These files persist across all users and sessions
COMPANY_DATA_FILE = "company_profiles.json"  # Shared company directory across all users
USED_CAPTIONS_FILE = "used_captions.json" 
FEEDBACK_FILE = "user_feedback.json"
STATS_FILE = "app_statistics.json"

# === Security Configuration ===
APP_PASSWORD = os.getenv("APP_PASSWORD", "adcellerant2025")

# === Feature Flags ===
# Clipboard functionality removed for cleaner UI
CLIPBOARD_FEATURES_ENABLED = False

# === OpenAI Configuration ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === Page Configuration ===
PAGE_CONFIG = {
    "page_title": "🚀 Adcellerant Social Caption Generator",
    "page_icon": "📱",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# === Model Configuration ===
OPENAI_MODELS = {
    "standard": "gpt-4o-mini",  # Default cost-effective model
    "premium": "gpt-4o"        # Premium quality model
}

# Platform Settings
PLATFORM_SETTINGS = {
    "All Social Platforms (Default)": {
        "char_limit": None,
        "description": "Character fitting for all social platforms"
    },
    "2-3 sentences": {
        "char_limit": None,
        "description": "Short and engaging"
    },
    "3-4 sentences": {
        "char_limit": None,
        "description": "Medium length content"
    },
    "Twitter/X": {
        "char_limit": 280,
        "description": "Twitter character limit"
    },
    "Instagram": {
        "char_limit": 2200,
        "description": "Instagram caption limit"
    },
    "LinkedIn": {
        "char_limit": 3000,
        "description": "LinkedIn post limit"
    },
    "Facebook": {
        "char_limit": None,
        "description": "Longer form content"
    }
}

# Image Processing Settings
IMAGE_SETTINGS = {
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "max_resolution": (4000, 4000),
    "supported_formats": ['PNG', 'JPEG', 'JPG', 'WebP', 'GIF'],
    "social_presets": {
        "Instagram Square": (1080, 1080),
        "Instagram Story": (1080, 1920),
        "Instagram Post": (1080, 1350),
        "Facebook Post": (1200, 630),
        "Twitter/X Post": (1200, 675),
        "LinkedIn Post": (1200, 627),
        "YouTube Thumbnail": (1280, 720)
    }
}

# === Cache Configuration ===
WEBSITE_ANALYSIS_TTL = 300  # 5 minutes
IMAGE_EXTRACTION_TTL = 300  # 5 minutes

# === Request Configuration ===
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3

# === File Upload Limits ===
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MIN_RESOLUTION = (100, 100)  # Minimum 100x100 pixels
MAX_RESOLUTION = (10000, 10000)  # Maximum 10000x10000 pixels
ALLOWED_FORMATS = ['PNG', 'JPEG', 'JPG', 'WEBP']

# UI Settings
UI_SETTINGS = {
    "default_expanded_sections": [],  # All sections collapsed by default
    "sidebar_sections": ["Company Profiles", "AI Model", "Actions"],
    "main_sections": ["Business Details", "Image Processing", "Caption Generation"]
}

# Session State Keys
SESSION_KEYS = {
    "business": ["business_name", "business_type", "target_audience", "product_name"],
    "settings": ["openai_model", "selected_platform", "platform_char_limit", "include_cta"],
    "results": ["generated_captions", "processed_images", "website_analysis_results"],
    "company": ["selected_company", "company_profiles"]
}
