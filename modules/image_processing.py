#!/usr/bin/env python3
"""
Simplified image processing module for uploading images as caption references.
"""

import io
from typing import List, Optional, Tuple, Any
from PIL import Image
import streamlit as st

class ImageUploader:
    """Simple class for handling image uploads for caption reference."""
    
    def __init__(self):
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.allowed_formats = ["png", "jpg", "jpeg", "webp"]
    
    def validate_uploaded_file(self, uploaded_file) -> Tuple[bool, str]:
        """Validate a single uploaded file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if uploaded_file is None:
            return False, "No file uploaded"
        
        # Check file size
        if uploaded_file.size > self.max_file_size:
            size_mb = uploaded_file.size / (1024 * 1024)
            return False, f"File too large: {size_mb:.1f}MB (max 5MB)"
        
        # Check file format
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in self.allowed_formats:
            return False, f"Unsupported format: {file_extension}. Use: {', '.join(self.allowed_formats)}"
        
        try:
            # Try to open as image
            image = Image.open(uploaded_file)
            image.verify()  # Verify it's a valid image
            return True, ""
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    def process_uploaded_files(self, uploaded_files) -> Tuple[List[Any], List[str]]:
        """Process multiple uploaded files.
        
        Args:
            uploaded_files: List of Streamlit uploaded file objects
            
        Returns:
            Tuple of (valid_files, error_messages)
        """
        valid_files = []
        error_messages = []
        
        if not uploaded_files:
            return valid_files, error_messages
        
        for uploaded_file in uploaded_files:
            is_valid, error_msg = self.validate_uploaded_file(uploaded_file)
            
            if is_valid:
                valid_files.append(uploaded_file)
            else:
                error_messages.append(f"{uploaded_file.name}: {error_msg}")
        
        return valid_files, error_messages

# --- UI Section: Image Upload ---
def show_image_upload_section():
    """Display simple image upload UI for caption reference."""
    st.markdown("#### Upload Images (Optional)")
    st.markdown("*Upload images to help generate more targeted captions*")
    
    # Get dynamic key for file uploader to enable proper clearing
    if 'file_uploader_key_counter' not in st.session_state:
        st.session_state.file_uploader_key_counter = 0
    uploader_key = f"image_uploader_{st.session_state.file_uploader_key_counter}"
    
    uploaded_files = st.file_uploader(
        "Choose images",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        help="Drag and drop or select images. These will be used as reference for caption generation.",
        key=uploader_key
    )
    
    # Check if we should ignore uploaded files (after Start Over)
    if 'ignore_uploaded_files' in st.session_state and st.session_state.ignore_uploaded_files:
        uploaded_files = None
        # Reset the ignore flag after one render cycle
        del st.session_state.ignore_uploaded_files
    
    if uploaded_files:
        uploader = ImageUploader()
        valid_files, error_messages = uploader.process_uploaded_files(uploaded_files)
        
        # Show errors if any
        if error_messages:
            st.error("Some files couldn't be processed:")
            for error in error_messages:
                st.text(f"• {error}")
        
        # Show valid files with previews
        if valid_files:
            st.success(f"Successfully uploaded {len(valid_files)} image(s)")
            
            # Store in session state for caption generation
            if 'uploaded_images' not in st.session_state:
                st.session_state.uploaded_images = []
            st.session_state.uploaded_images = valid_files
            
            # Show preview of uploaded images
            cols = st.columns(min(3, len(valid_files)))
            for i, uploaded_file in enumerate(valid_files[:3]):  # Show max 3 previews
                with cols[i]:
                    try:
                        image = Image.open(uploaded_file)
                        st.image(image, caption=uploaded_file.name, use_container_width=True)
                    except Exception as e:
                        st.error(f"Can't preview {uploaded_file.name}")
            
            if len(valid_files) > 3:
                st.info(f"+ {len(valid_files) - 3} more images uploaded")
    
    return uploaded_files

def get_uploaded_images():
    """Get currently uploaded images from session state."""
    return st.session_state.get('uploaded_images', [])

def clear_uploaded_images():
    """Clear uploaded images and related data from session state."""
    # Clear uploaded images
    if 'uploaded_images' in st.session_state:
        del st.session_state.uploaded_images
    
    # Clear generated captions when images are cleared
    if 'generated_captions' in st.session_state:
        del st.session_state.generated_captions
    
    # Clear debug logs
    if 'debug_logs' in st.session_state:
        del st.session_state.debug_logs
    
    # Force file uploader to reset by incrementing its key counter
    if 'file_uploader_key_counter' not in st.session_state:
        st.session_state.file_uploader_key_counter = 0
    st.session_state.file_uploader_key_counter += 1
    
    # Set flag to ignore uploaded files on next render
    st.session_state.ignore_uploaded_files = True

# Legacy compatibility functions (simplified)
def get_image_processor():
    """Get an ImageUploader instance for compatibility."""
    return ImageUploader()

def get_image_validator():
    """Get an ImageUploader instance for compatibility.""" 
    return ImageUploader()

def get_batch_processor():
    """Get an ImageUploader instance for compatibility."""
    return ImageUploader()
