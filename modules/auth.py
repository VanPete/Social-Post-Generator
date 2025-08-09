#!/usr/bin/env python3
"""
Enhanced authentication module for the Social Post Generator application.
Features: Session persistence, auto-logout, improved UX
"""

import streamlit as st
import hashlib
import time
from datetime import datetime, timedelta
from config.constants import get_app_password
from config.settings import SESSION_KEYS
from utils.helpers import clear_session_keys

# Session configuration
SESSION_TIMEOUT_HOURS = 24  # Remember login for 24 hours
INACTIVITY_TIMEOUT_MINUTES = 120  # Auto-logout after 2 hours of inactivity

def check_password() -> bool:
    """Enhanced password check with session persistence and auto-logout.
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    
    # Check if we have a valid remembered session
    if _is_session_valid():
        _update_last_activity()
        return True
    
    # Check for inactivity timeout
    if _check_inactivity_timeout():
        return False
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        app_password = get_app_password()
        if st.session_state["password"] == app_password:
            _create_authenticated_session()
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False
            st.session_state["login_attempts"] = st.session_state.get("login_attempts", 0) + 1

    if "password_correct" not in st.session_state:
        # First run, show input for password
        _show_login_form(password_entered)
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error
        _show_login_error(password_entered)
        return False
    else:
        # Password correct, but verify session is still valid
        if _is_session_valid():
            _update_last_activity()
            return True
        else:
            # Session expired, clear and re-authenticate
            _clear_authentication()
            _show_login_form(password_entered)
            return False

def _create_authenticated_session():
    """Create an authenticated session with timestamp and token."""
    current_time = datetime.now()
    
    # Create a simple session token (for session validation)
    session_data = f"{current_time.isoformat()}_{get_app_password()}"
    session_token = hashlib.md5(session_data.encode()).hexdigest()
    
    st.session_state["password_correct"] = True
    st.session_state["auth_timestamp"] = current_time.isoformat()
    st.session_state["session_token"] = session_token
    st.session_state["last_activity"] = current_time.isoformat()
    st.session_state["login_attempts"] = 0  # Reset attempts on successful login

def _is_session_valid() -> bool:
    """Check if the current session is valid and not expired."""
    if not st.session_state.get("password_correct", False):
        return False
    
    if not st.session_state.get("auth_timestamp") or not st.session_state.get("session_token"):
        return False
    
    try:
        auth_time = datetime.fromisoformat(st.session_state["auth_timestamp"])
        current_time = datetime.now()
        
        # Check if session has expired (24 hours)
        if current_time - auth_time > timedelta(hours=SESSION_TIMEOUT_HOURS):
            return False
        
        # Validate session token
        expected_data = f"{st.session_state['auth_timestamp']}_{get_app_password()}"
        expected_token = hashlib.md5(expected_data.encode()).hexdigest()
        
        return st.session_state["session_token"] == expected_token
        
    except (ValueError, KeyError):
        return False

def _check_inactivity_timeout() -> bool:
    """Check if user has been inactive for too long."""
    if not st.session_state.get("last_activity"):
        return False
    
    try:
        last_activity = datetime.fromisoformat(st.session_state["last_activity"])
        current_time = datetime.now()
        
        if current_time - last_activity > timedelta(minutes=INACTIVITY_TIMEOUT_MINUTES):
            _clear_authentication()
            st.warning(f"⏰ Session expired due to {INACTIVITY_TIMEOUT_MINUTES} minutes of inactivity. Please log in again.")
            st.rerun()
            return True
            
    except (ValueError, KeyError):
        pass
    
    return False

def _update_last_activity():
    """Update the last activity timestamp."""
    st.session_state["last_activity"] = datetime.now().isoformat()

def _clear_authentication():
    """Clear authentication-related session state."""
    auth_keys = ["password_correct", "auth_timestamp", "session_token", "last_activity"]
    for key in auth_keys:
        if key in st.session_state:
            del st.session_state[key]

def show_logout_option():
    """Show enhanced logout option with session info in sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔓 Session")
        
        # Show session info
        if st.session_state.get("auth_timestamp"):
            try:
                auth_time = datetime.fromisoformat(st.session_state["auth_timestamp"])
                hours_logged_in = (datetime.now() - auth_time).total_seconds() / 3600
                
                if hours_logged_in < 1:
                    session_info = f"Logged in {int(hours_logged_in * 60)} minutes ago"
                else:
                    session_info = f"Logged in {hours_logged_in:.1f} hours ago"
                    
                st.caption(f"✅ {session_info}")
                
                # Show remaining session time
                remaining_hours = SESSION_TIMEOUT_HOURS - hours_logged_in
                if remaining_hours > 1:
                    st.caption(f"🕒 Session expires in {remaining_hours:.1f} hours")
                else:
                    st.caption(f"🕒 Session expires in {int(remaining_hours * 60)} minutes")
                    
            except (ValueError, KeyError):
                st.caption("✅ Logged in")
        
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout_user()

def logout_user():
    """Enhanced logout with confirmation and better UX."""
    # Clear authentication and related session state
    _clear_authentication()
    cleared_count = clear_session_keys(SESSION_KEYS["AUTH_KEYS"])
    
    # Show success message
    st.success("🚪 Logged out successfully! Your work has been saved.")
    st.info("💡 Your login will be remembered for 24 hours when you log back in.")
    
    st.rerun()

def _show_login_form(password_callback):
    """Show enhanced login form with better UX."""
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🔐 Welcome Back")
        st.markdown("---")
        
        # Show session persistence info
        st.info("🔒 **Secure Access Required**\n\n"
               "• Your login will be remembered for 24 hours\n"
               "• Sessions auto-expire after 2 hours of inactivity\n"
               "• Contact Maddie Stitt for access credentials")
        
        # Show login attempts warning if applicable
        attempts = st.session_state.get("login_attempts", 0)
        if attempts > 0:
            if attempts >= 3:
                st.error(f"⚠️ **{attempts} failed login attempts detected.**\n\n"
                        "Please verify your password or contact support.")
            else:
                st.warning(f"❌ Incorrect password. **{attempts} attempt(s)** failed.")
        
        # Password input
        st.text_input(
            "Enter Password", 
            type="password", 
            on_change=password_callback, 
            key="password",
            help="Enter the application password",
            placeholder="Password"
        )
        
        # Additional security info
        st.markdown("---")
        st.caption("🛡️ This application uses secure session management")

def _show_login_error(password_callback):
    """Show the login form with enhanced error messaging."""
    _show_login_form(password_callback)

def is_authenticated() -> bool:
    """Check if user is currently authenticated with enhanced validation.
    
    Returns:
        bool: True if authenticated and session valid, False otherwise
    """
    return _is_session_valid()

def get_session_info() -> dict:
    """Get current session information for debugging/monitoring.
    
    Returns:
        dict: Session information
    """
    if not st.session_state.get("password_correct", False):
        return {"authenticated": False}
    
    try:
        auth_time = datetime.fromisoformat(st.session_state.get("auth_timestamp", ""))
        last_activity = datetime.fromisoformat(st.session_state.get("last_activity", ""))
        current_time = datetime.now()
        
        return {
            "authenticated": True,
            "login_time": auth_time.strftime("%Y-%m-%d %H:%M:%S"),
            "session_duration_hours": (current_time - auth_time).total_seconds() / 3600,
            "last_activity": last_activity.strftime("%Y-%m-%d %H:%M:%S"),
            "minutes_since_activity": (current_time - last_activity).total_seconds() / 60,
            "expires_in_hours": SESSION_TIMEOUT_HOURS - ((current_time - auth_time).total_seconds() / 3600)
        }
    except (ValueError, KeyError):
        return {"authenticated": False, "error": "Invalid session data"}

def force_logout(reason: str = "Manual logout"):
    """Force logout with specified reason."""
    _clear_authentication()
    st.warning(f"🚪 Logged out: {reason}")
    st.rerun()
