#!/usr/bin/env python3
"""
Social Post Generator - AI-Powered Social Media Content Creation
"""

import os
import uuid
import streamlit as st
import openai
from dotenv import load_dotenv

# --- SESSION ID INITIALIZATION (MUST BE FIRST) ---
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

# Load environment variables
load_dotenv()

# Core module imports
from modules.auth import check_password, show_logout_option
from modules.companies import get_session_manager, get_company_manager
from modules.image_processing import show_image_upload_section, clear_uploaded_images
from modules.ui_components import get_ui_components
from modules.business_info import business_info_section
from modules.caption_generator import trigger_caption_generation
from config.constants import OPENAI_MODELS

# Enhanced UI components with fallbacks
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
    page_title="Social Post Generator",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CORE FUNCTIONS ===

def get_api_key():
    """Get OpenAI API key from environment variables or Streamlit secrets."""
    try:
        return st.secrets["OPENAI_API_KEY"]
    except (KeyError, FileNotFoundError, AttributeError):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            st.error("⚠️ **OPENAI_API_KEY not found!**\n\n"
                    "**For local development:** Add to your `.env` file:\n"
                    "```\nOPENAI_API_KEY=your_api_key_here\n```\n\n"
                    "**For Streamlit Cloud:** Add to app secrets:\n"
                    "```toml\nOPENAI_API_KEY = \"your_api_key_here\"\n```")
            st.stop()
        return api_key

@st.cache_resource
def initialize_openai_client():
    """Initialize OpenAI client with API key."""
    api_key = get_api_key()
    if not api_key:
        st.error("OPENAI_API_KEY configuration error. Please check your setup.")
        st.stop()
    return openai.OpenAI(api_key=api_key)

def start_over():
    """Clear current session data while preserving saved company profiles."""
    keys_to_preserve = [
        'session_id', 
        'password_correct',  # Keep authentication
        'auth_timestamp',    # Keep authentication timestamp
        'session_token',     # Keep session token
        'last_activity',     # Keep last activity timestamp
        'login_attempts',    # Keep login attempt counter
        'company_profiles',  # Keep saved company data
        'company_image_presets',  # Keep company image settings
        'file_uploader_key_counter',  # Keep the counter for image uploader reset
        'ignore_uploaded_files'  # Keep the flag to ignore uploaded files
    ]
    
    # Clear uploaded images first (before clearing session state)
    clear_uploaded_images()
    
    # Store preserved data
    preserved_data = {}
    for key in keys_to_preserve:
        if key in st.session_state:
            preserved_data[key] = st.session_state[key]
    
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Restore preserved data
    for key, value in preserved_data.items():
        st.session_state[key] = value
    
    st.success("Started over! Current data cleared, saved companies preserved.")
    st.rerun()

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    default_values = {
        'generated_captions': [],
        'uploaded_images': [],
        'image_count': 0,
        'business_name': None,
        'business_type': None,
        'target_audience': None,
        'product_name': None,
        'call_to_action': True,
        'website_url': None,
        'openai_model': OPENAI_MODELS["standard"],
        'website_analysis_results': None
    }
    
    for key, default_value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def create_sidebar():
    """Create the enhanced sidebar with company, AI model, and actions."""
    with st.sidebar:
        st.markdown("# Navigation")
        
        # Start Over button at the top, always visible
        st.markdown("### Quick Actions")
        if st.button("🔄 Start Over", use_container_width=True, type="secondary", help="Clear current data while keeping saved profiles"):
            start_over()
        
        st.markdown("---")
        
        # Create navigation menu
        selected_section = _create_navigation_menu()
        
        # Handle different sections
        if selected_section == "Company":
            _handle_company_section()
        elif selected_section == "AI Model":
            _handle_ai_model_section()
        elif selected_section == "Actions":
            _handle_actions_section()
        
        # Show logout option at bottom
        show_logout_option()

def _create_navigation_menu():
    """Create navigation menu with fallback options."""
    if OPTION_MENU_AVAILABLE:
        return option_menu(
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
        return st.selectbox(
            "Navigation",
            ["Company", "AI Model", "Actions"],
            index=0
        )

def _handle_company_section():
    """Handle company profile management section."""
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
            session_manager = get_session_manager()
            
            # Find profile by name (since old system used names)
            profiles = session_manager.company_manager.list_profiles()
            target_profile = None
            for profile in profiles:
                if profile.name == selected_company:
                    target_profile = profile
                    break
            
            if target_profile:
                if session_manager.load_company_to_session(target_profile.company_id):
                    st.success(f"Loaded profile for {selected_company}")
                    st.rerun()
                else:
                    st.error("Failed to load profile")
            else:
                st.error("Profile not found")
    
    if st.session_state.get('business_name'):
        if st.button("Save Current Profile", use_container_width=True):
            session_manager = get_session_manager()
            
            # Create a new profile with current session data
            new_profile = session_manager.company_manager.create_profile(st.session_state.get('business_name', ''))
            
            # Save current session data to the new profile
            if session_manager.save_session_to_company(new_profile.company_id):
                st.success("Profile saved successfully!")
            else:
                st.error("Error saving profile")

def _handle_ai_model_section():
    """Handle AI model selection section."""
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

def _handle_actions_section():
    """Handle additional actions section."""
    st.markdown("### Additional Actions")
    
    # Session information (for debugging/monitoring)
    if st.checkbox("Show Session Info", value=False, help="Display authentication session details"):
        from modules.auth import get_session_info
        session_info = get_session_info()
        
        if session_info.get("authenticated"):
            st.json({
                "🟢 Status": "Authenticated",
                "⏰ Login Time": session_info.get("login_time", "Unknown"),
                "📊 Session Duration": f"{session_info.get('session_duration_hours', 0):.1f} hours",
                "🔄 Last Activity": session_info.get("last_activity", "Unknown"),
                "⏳ Minutes Since Activity": f"{session_info.get('minutes_since_activity', 0):.1f}",
                "⏱️ Expires In": f"{session_info.get('expires_in_hours', 0):.1f} hours"
            })
        else:
            st.json({"🔴 Status": "Not Authenticated"})
    
    st.markdown("---")
    
    st.warning("Reset All clears everything including saved profiles.")
    if st.button("Reset All", use_container_width=True):
        # Clear session state
        for key in list(st.session_state.keys()):
            if key not in ['session_id', 'password_correct']:
                del st.session_state[key]
        
        # Clear all saved company profiles
        try:
            session_manager = get_session_manager()
            if session_manager.clear_all_profiles():
                st.success("All data and saved profiles cleared!")
            else:
                st.warning("Session data cleared, but there was an issue clearing saved profiles.")
        except Exception as e:
            st.warning(f"Session data cleared, but error clearing profiles: {str(e)}")
        
        st.rerun()

def display_page_header():
    """Display the main page header."""
    if STREAMLIT_EXTRAS_AVAILABLE:
        colored_header(
            label="Social Post Generator",
            description="AI-Powered Social Media Content Creation",
            color_name="violet-70"
        )
        add_vertical_space(2)
    else:
        st.markdown("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; margin-bottom: 30px; color: white; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
            <h1 style='margin: 0; font-size: 2.5em; font-weight: 700;'>Social Post Generator</h1>
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
    
    st.markdown("## Social Post Generator")
    st.caption("AI-Powered Social Media Content Creation")
    
    st.session_state['call_to_action'] = st.checkbox(
        "Include a call-to-action in captions?", 
        value=bool(st.session_state.get('call_to_action', True))
    )
    st.session_state['include_cta'] = st.session_state['call_to_action']
    
    if can_generate:
        selected_platform, char_limit = ui.create_platform_selector()
        st.session_state['platform_char_limit'] = char_limit
        st.session_state['selected_platform'] = selected_platform
        
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
    
    # Display debug log if available
    if st.session_state.get('debug_log'):
        with st.expander("🔍 Debug Log (Click to expand)", expanded=False):
            for debug_msg in st.session_state.debug_log:
                st.text(debug_msg)
    
    # Website analysis debug log
    if st.session_state.get('website_debug_log'):
        with st.expander("🌐 Website Analysis Debug Log", expanded=False):
            for debug_msg in st.session_state.website_debug_log:
                st.text(debug_msg)
            if st.button("Clear Website Debug Log"):
                st.session_state.website_debug_log = []
                st.rerun()

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
