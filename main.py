#!/usr/bin/env python3
"""
Social Post Generator - AI-Powered Social Media Content Creation
"""

import os
import uuid
from datetime import datetime
import streamlit as st
import openai
from dotenv import load_dotenv

# --- SESSION ID INITIALIZATION (MUST BE FIRST) ---
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

# Load environment variables
load_dotenv()

# Import modules
from modules.auth import check_password, show_logout_option
from config.constants import OPENAI_MODELS
from modules.companies import get_company_manager, get_session_manager
from modules.website_analysis import get_website_analyzer
from modules.image_processing import show_image_upload_section, clear_uploaded_images
from modules.ui_components import get_ui_components
from modules.business_info import business_info_section
from modules.caption_generator import get_caption_generator, trigger_caption_generation

# Enhanced Streamlit UI components (with fallbacks)
try:
    from streamlit_extras.colored_header import colored_header
    from streamlit_extras.add_vertical_space import add_vertical_space
    STREAMLIT_EXTRAS_AVAILABLE = True
except ImportError:
    STREAMLIT_EXTRAS_AVAILABLE = False

try:
    from streamlit_option_menu import option_menu
    OPTION_MENU_AVAILABLE = True
except ImportError:
    OPTION_MENU_AVAILABLE = False

# Set Streamlit page configuration
st.set_page_config(
    page_title="Social Caption Generator",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
@st.cache_resource
def initialize_openai_client():
    """Initialize OpenAI client with API key."""
    if not OPENAI_API_KEY:
        st.error("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
        st.stop()
    
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    return client

def start_over():
    """Clear current session data while preserving saved company profiles."""
    keys_to_preserve = [
        'session_id', 
        'password_correct',  # Keep authentication
        'company_profiles',  # Keep saved company data
        'company_image_presets'  # Keep company image settings
    ]
    
    # Store preserved data
    preserved_data = {}
    for key in keys_to_preserve:
        if key in st.session_state:
            preserved_data[key] = st.session_state[key]
    
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Clear uploaded images
    clear_uploaded_images()
    
    # Restore preserved data
    for key, value in preserved_data.items():
        st.session_state[key] = value
    
    st.success("Started over! Current data cleared, saved companies preserved.")
    st.rerun()

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'generated_captions' not in st.session_state:
        st.session_state.generated_captions = []
    
    session_keys = [
        'business_name', 'business_type', 'target_audience', 'product_name', 
        'call_to_action', 'website_url', 'openai_model', 'website_analysis_results'
    ]
    
    if 'uploaded_images' not in st.session_state:
        st.session_state.uploaded_images = []
    if 'image_count' not in st.session_state:
        st.session_state.image_count = 0
    
    for key in session_keys:
        if key not in st.session_state:
            st.session_state[key] = None
    
    # Set default model to GPT-4o-mini
    if 'openai_model' not in st.session_state or st.session_state.openai_model is None:
        st.session_state.openai_model = OPENAI_MODELS["standard"]
    
    # Set call-to-action default to True
    if 'call_to_action' not in st.session_state or st.session_state.call_to_action is None:
        st.session_state.call_to_action = True

def create_sidebar():
    """Create the enhanced sidebar with company, AI model, and actions."""
    with st.sidebar:
        st.markdown("# Navigation")
        
        # Start Over button at the top, always visible
        st.markdown("### Quick Actions")
        if st.button("🔄 Start Over", use_container_width=True, type="secondary", help="Clear current data while keeping saved profiles"):
            start_over()
        
        st.markdown("---")
        
        if OPTION_MENU_AVAILABLE:
            selected_section = option_menu(
                menu_title=None,
                options=["Company", "AI Model", "Actions"],
                icons=["building", "robot", "lightning"],
                menu_icon="cast",
                default_index=0,
                orientation="vertical",
                styles={
                    "container": {"padding": "0!important", "background-color": "#fafafa"},
                    "icon": {"color": "#4ECDC4", "font-size": "18px"},
                    "nav-link": {
                        "font-size": "14px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "#eee",
                    },
                    "nav-link-selected": {"background-color": "#4ECDC4"},
                },
                key=f"sidebar_menu_{st.session_state['session_id']}"
            )
        else:
            selected_section = st.selectbox(
                "Navigation",
                ["Company", "AI Model", "Actions"],
                index=0
            )
        
        # Company Profile Management Section
        if selected_section == "Company":
            st.markdown("### Company Profile Management")
            company_manager = get_company_manager()
            
            recent_companies = company_manager.get_recent_companies(limit=10)
            if recent_companies:
                company_options = [""] + [f"{comp['name']}" for comp in recent_companies]
                selected_company = st.selectbox(
                    "Load Existing Profile:",
                    company_options,
                    help="Quickly load a previously saved company profile"
                )
                
                if selected_company and st.button("Load Profile", use_container_width=True):
                    profile_data = None
                    for comp in recent_companies:
                        if comp['name'] == selected_company:
                            profile_data = comp['profile']
                            break
                    
                    if profile_data:
                        if 'business_input' in profile_data:
                            st.session_state.business_name = profile_data.get('business_input', '')
                        if 'business_type' in profile_data:
                            st.session_state.business_type = profile_data.get('business_type', '')
                        if 'target_audience' in profile_data:
                            st.session_state.target_audience = profile_data.get('target_audience', '')
                        if 'website_url' in profile_data:
                            st.session_state.website_url = profile_data.get('website_url', '')
                        
                        st.success(f"Loaded profile for {selected_company}")
                        st.rerun()
            
            if st.session_state.get('business_name'):
                if st.button("Save Current Profile", use_container_width=True):
                    current_settings = {
                        'business_input': st.session_state.get('business_name', ''),
                        'business_type': st.session_state.get('business_type', ''),
                        'target_audience': st.session_state.get('target_audience', ''),
                        'website_url': st.session_state.get('website_url', ''),
                        'product_name': st.session_state.get('product_name', ''),
                        'website_analysis': st.session_state.get('website_analysis_results')
                    }
                    
                    if company_manager.save_company_profile(st.session_state.business_name, current_settings):
                        st.success("Profile saved successfully!")
                    else:
                        st.error("Error saving profile")
        
        # AI Model Selection Section
        elif selected_section == "AI Model":
            st.markdown("### AI Model Selection")
            default_choice = "GPT-4o-mini"
            if st.session_state.get('openai_model') == OPENAI_MODELS["premium"]:
                default_choice = "GPT-4o"
            
            model_choice = st.radio(
                "Choose AI Model:",
                ["GPT-4o-mini (Standard - Cost Effective)", "GPT-4o (Premium - Best Quality)"],
                index=0 if "mini" in default_choice else 1,
                help="GPT-4o-mini is faster and more cost-effective. GPT-4o provides higher quality."
            )
            st.session_state.openai_model = OPENAI_MODELS["premium"] if "Premium" in model_choice else OPENAI_MODELS["standard"]
            
            current_model = st.session_state.get('openai_model', OPENAI_MODELS["standard"])
            st.caption(f"Currently using: {current_model}")
            
            if "mini" in current_model:
                st.info("Cost-effective choice - great for most social media captions")
            else:
                st.info("Premium choice - highest quality output")
        
        # Quick Actions Section
        elif selected_section == "Actions":
            st.markdown("### Additional Actions")
            
            st.warning("Reset All clears everything including saved profiles.")
            if st.button("Reset All", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key not in ['session_id', 'password_correct']:
                        del st.session_state[key]
                st.success("All data reset!")
                st.rerun()
        
        # Show logout option at bottom
        show_logout_option()

def display_page_header():
    """Display the main page header."""
    if STREAMLIT_EXTRAS_AVAILABLE:
        colored_header(
            label="Social Caption Generator",
            description="AI-Powered Social Media Content Creation",
            color_name="violet-70"
        )
        add_vertical_space(2)
    else:
        st.markdown("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; margin-bottom: 30px; color: white; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
            <h1 style='margin: 0; font-size: 2.5em; font-weight: 700;'>Social Caption Generator</h1>
            <h3 style='margin: 10px 0 0 0; font-weight: 300; opacity: 0.9;'>AI-Powered Social Media Content Creation</h3>
        </div>
        """, unsafe_allow_html=True)

def handle_main_content():
    """Handle the main single-page layout."""
    if STREAMLIT_EXTRAS_AVAILABLE:
        colored_header(
            label="Business Information",
            description="Enter your website URL or business details.",
            color_name="blue-70"
        )
    else:
        st.markdown("### Business Information")

    ui = get_ui_components()
    business_info_section(ui)

    # Images section (collapsible)
    with st.expander("Images (Optional)", expanded=False):
        show_image_upload_section()

    # Caption Generator section
    st.markdown("---")
    
    required_fields = [
        st.session_state.get('business_name'), 
        st.session_state.get('business_type'), 
        st.session_state.get('target_audience')
    ]
    can_generate = all(field and str(field).strip() for field in required_fields)
    
    st.markdown("## Social Caption Generator")
    st.caption("AI-Powered Social Media Content Creation")
    
    st.session_state['call_to_action'] = st.checkbox(
        "Include a call-to-action in captions?", 
        value=bool(st.session_state.get('call_to_action', True))
    )
    
    if can_generate:
        selected_platform, char_limit = ui.create_platform_selector()
        st.session_state['platform_char_limit'] = char_limit
        
        generate_clicked = st.button(
            "Generate Captions", 
            type="primary", 
            use_container_width=True, 
            key="generate_captions_main"
        )
        
        if generate_clicked:
            progress_placeholder = st.empty()
            with progress_placeholder:
                with st.spinner("Generating captions..."):
                    st.session_state['trigger_generate_captions'] = True
                    success = trigger_caption_generation(st)
                    
            progress_placeholder.empty()
            
            if success:
                st.rerun()
    else:
        st.warning("Please fill in all required business details above to enable caption generation.")
    
    # Display generated captions
    if st.session_state.get('generated_captions'):
        if STREAMLIT_EXTRAS_AVAILABLE:
            add_vertical_space(2)
            colored_header(
                label="Generated Captions",
                description="Your AI-powered social media content",
                color_name="green-70"
            )
        else:
            st.markdown("### Generated Captions")
        
        ui.display_caption_results(st.session_state.generated_captions)

def main():
    """Main application entry point."""
    # Check authentication first
    if not check_password():
        return
    
    # Initialize session state
    initialize_session_state()
    
    # Create sidebar
    create_sidebar()
    
    # Display main content
    display_page_header()
    handle_main_content()

if __name__ == "__main__":
    main()
