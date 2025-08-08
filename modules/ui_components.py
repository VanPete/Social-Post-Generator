#!/usr/bin/env python3
"""
Core UI Components for Social Post Generator
Clean, business-focused interface components
"""

import streamlit as st
import uuid
from typing import Dict, Any, Tuple

class UIComponents:
    """Core UI components for the Social Post Generator."""
    
    def __init__(self):
        self.platform_limits = {
            "All Social Platforms (Default)": None,
            "2-3 sentences": None,
            "3-4 sentences": None,
            "Twitter/X": 280,
            "Instagram": 2200,
            "LinkedIn": 3000,
            "Facebook": None
        }
    
    def create_platform_selector(self) -> Tuple[str, int]:
        """Create platform selector with character limits."""
        platform_options = list(self.platform_limits.keys())
        default_index = 0
        
        selected_platform = st.selectbox(
            "Select Platform:",
            platform_options,
            index=default_index,
            help="Choose a platform to automatically apply character limits",
            key=f"platform_select_{uuid.uuid4()}"
        )
        
        char_limit = self.platform_limits[selected_platform]
        
        # Display character limit info
        if char_limit:
            st.markdown(f"**Character limit:** {char_limit}")
        else:
            st.markdown("**Length:** Character fitting for all social platforms")
        
        return selected_platform, char_limit
    
    def show_character_count(self, text: str, char_limit: int = None) -> str:
        """Display character count with visual indicators."""
        char_count = len(text)
        
        if char_limit:
            if char_count > char_limit:
                color = "#ff4444"  # Red for over limit
                status = f"{char_count}/{char_limit} (over limit)"
            elif char_count > char_limit * 0.9:
                color = "#ff8800"  # Orange for warning
                status = f"{char_count}/{char_limit} (near limit)"
            else:
                color = "#00aa00"  # Green for good
                status = f"{char_count}/{char_limit}"
        else:
            color = "#666666"
            status = f"{char_count} characters"
        
        return f'<span style="color: {color}; font-size: 12px;">{status}</span>'
    
    def create_business_form(self) -> Dict[str, Any]:
        """Create business information form with enhanced auto-fill support."""
        business_data = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Get value from either the input key or the base key (for autofill compatibility)
            business_name_value = st.session_state.get('business_name_input') or st.session_state.get('business_name') or ''
            business_data['business_name'] = st.text_input(
                "Business Name *",
                value=business_name_value,
                placeholder="Auto-filled from website or enter manually",
                help="This will be auto-filled when you analyze a website",
                key="business_name_input"
            ) or ''
            
            # Get value from either the input key or the base key (for autofill compatibility)
            business_type_value = st.session_state.get('business_type_input') or st.session_state.get('business_type') or ''
            business_data['business_type'] = st.text_input(
                "Business Type *",
                value=business_type_value,
                placeholder="e.g., Restaurant, Tech Startup, Marketing Agency",
                help="Auto-detected from website content",
                key="business_type_input"
            ) or ''
        
        with col2:
            # Get value from either the input key or the base key (for autofill compatibility)
            target_audience_value = st.session_state.get('target_audience_input') or st.session_state.get('target_audience') or ''
            business_data['target_audience'] = st.text_input(
                "Target Audience",
                value=target_audience_value,
                placeholder="e.g., Small business owners, Young professionals",
                help="AI will analyze your website to identify your target customers",
                key="target_audience_input"
            ) or ''
            
            # Get value from either the input key or the base key (for autofill compatibility)
            product_name_value = st.session_state.get('product_name_input') or st.session_state.get('product_name') or ''
            business_data['product_name'] = st.text_input(
                "Main Product/Service",
                value=product_name_value,
                placeholder="e.g., Social Media Management, Web Design",
                help="Primary offering - extracted from website services section",
                key="product_name_input"
            ) or ''
        
        # Update session state - ensure no None values
        for key, value in business_data.items():
            st.session_state[key] = value or ''
        
        return business_data
    
    def create_caption_settings(self) -> Dict[str, Any]:
        """Create caption generation settings."""
        settings = {}
        
        # Platform selector
        selected_platform, char_limit = self.create_platform_selector()
        settings['selected_platform'] = selected_platform
        settings['platform_char_limit'] = char_limit
        
        # Store in session state
        st.session_state['selected_platform'] = selected_platform
        st.session_state['platform_char_limit'] = char_limit
        
        # Include call-to-action option
        settings['include_cta'] = st.checkbox(
            "Include call-to-action in captions",
            value=st.session_state.get('include_cta', False),
            key="include_cta_checkbox"
        )
        st.session_state['include_cta'] = settings['include_cta']
        
        return settings
    
    def display_caption_results(self, captions: list) -> None:
        """Display generated captions with simple text area for editing and copying."""
        if not captions:
            st.info("No captions generated yet. Fill in business details and click Generate Captions.")
            return
        
        char_limit = st.session_state.get('platform_char_limit')
        
        for i, caption in enumerate(captions, 1):
            with st.container():
                st.markdown(f"**Caption {i}:**")
                
                # Character count display
                char_count_html = self.show_character_count(caption, char_limit)
                st.markdown(char_count_html, unsafe_allow_html=True)
                
                # Editable caption area - users can copy with Ctrl+A, Ctrl+C
                edited_caption = st.text_area(
                    f"Edit Caption {i}",
                    value=caption,
                    height=100,
                    label_visibility="collapsed",
                    key=f"caption_edit_{i}_{st.session_state.get('session_id', 'default')}"
                )
                
                # Show updated character count for edited caption if changed
                if edited_caption != caption:
                    updated_char_count_html = self.show_character_count(edited_caption, char_limit)
                    st.markdown(f"Updated: {updated_char_count_html}", unsafe_allow_html=True)
                
                if i < len(captions):
                    st.markdown("---")
    
    def create_ai_model_selector(self) -> str:
        """Create AI model selection component."""
        from config.constants import OPENAI_MODELS
        
        model_options = {
            "GPT-4o-mini (Recommended)": OPENAI_MODELS["standard"],
            "GPT-4o (Premium)": OPENAI_MODELS["premium"]
        }
        
        selected_model_display = st.selectbox(
            "AI Model",
            list(model_options.keys()),
            index=0,  # Default to GPT-4o-mini
            help="GPT-4o-mini is cost-effective for most use cases. GPT-4o provides premium quality.",
            key=f"ai_model_selector_{uuid.uuid4()}"
        )
        
        selected_model = model_options[selected_model_display]
        st.session_state['openai_model'] = selected_model
        
        return selected_model
    
    def show_generation_button(self) -> bool:
        """Show caption generation button and return if clicked."""
        return st.button(
            "Generate Captions",
            type="primary",
            use_container_width=True,
            key=f"generate_captions_{uuid.uuid4()}"
        )


def get_ui_components():
    """Get singleton instance of UIComponents."""
    if 'ui_components' not in st.session_state:
        st.session_state.ui_components = UIComponents()
    return st.session_state.ui_components
