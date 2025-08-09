#!/usr/bin/env python3
"""
Company profile management for Social Post Generator
"""
import streamlit as st
import uuid
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

class CompanyProfile:
    """Represents a company profile with business information."""
    
    def __init__(self, company_id: str = None):
        self.company_id = company_id or str(uuid.uuid4())
        self.name = ""
        self.business_type = ""
        self.target_audience = ""
        self.product_name = ""  # Main Product/Service field
        self.website_url = ""
        self.description = ""
        self.created_at = None
        self.updated_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            'company_id': self.company_id,
            'name': self.name,
            'business_type': self.business_type,
            'target_audience': self.target_audience,
            'product_name': self.product_name,  # Include product_name field
            'website_url': self.website_url,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load profile from dictionary."""
        self.company_id = data.get('company_id', self.company_id)
        self.name = data.get('name', '')
        self.business_type = data.get('business_type', '')
        self.target_audience = data.get('target_audience', '')
        self.product_name = data.get('product_name', '')  # Load product_name field
        self.website_url = data.get('website_url', '')
        self.description = data.get('description', '')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        return self


class CompanyManager:
    """Manages company profiles with persistent file storage."""
    
    def __init__(self, profiles_file: str = "company_profiles.json"):
        self.profiles_file = profiles_file
        self.profiles = {}
        self.load_profiles()
    
    def load_profiles(self):
        """Load company profiles from JSON file."""
        try:
            with open(self.profiles_file, 'r', encoding='utf-8') as f:
                profiles_data = json.load(f)
                
            # Convert old format to new format if needed
            for company_name, data in profiles_data.items():
                if isinstance(data, dict):
                    # Convert old format to new CompanyProfile format
                    profile = CompanyProfile()
                    profile.name = company_name
                    profile.business_type = data.get('business_type', '')
                    profile.target_audience = data.get('target_audience', '')
                    profile.product_name = data.get('product_name', '')  # Load product_name field
                    profile.website_url = data.get('website_url', '')
                    profile.description = data.get('description', '')
                    
                    # Use existing timestamps if available, otherwise set current time
                    profile.created_at = data.get('created_at', datetime.now().isoformat())
                    profile.updated_at = data.get('updated_at', datetime.now().isoformat())
                    
                    self.profiles[profile.company_id] = profile
                    
        except FileNotFoundError:
            # Create empty profiles file if it doesn't exist
            self.profiles = {}
            self.save_profiles()
        except json.JSONDecodeError:
            # Handle corrupted JSON file
            self.profiles = {}
    
    def save_profiles(self):
        """Save company profiles to JSON file."""
        try:
            # Convert to format for storage
            profiles_data = {}
            for profile in self.profiles.values():
                profiles_data[profile.name] = {
                    'business_input': profile.name,  # Keep for compatibility
                    'name': profile.name,  # Add proper name field
                    'business_type': profile.business_type,
                    'target_audience': profile.target_audience,
                    'product_name': profile.product_name,  # Include product_name field
                    'website_url': profile.website_url,
                    'description': profile.description,
                    'created_at': profile.created_at,
                    'updated_at': profile.updated_at
                }
            
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(profiles_data, f, indent=2, ensure_ascii=False)
                
            # Also save to session state for backward compatibility
            if 'company_profiles' not in st.session_state:
                st.session_state.company_profiles = {}
            st.session_state.company_profiles.update(profiles_data)
            
        except Exception as e:
            print(f"Error saving profiles: {e}")
    
    def create_profile(self, name: str) -> CompanyProfile:
        """Create a new company profile."""
        profile = CompanyProfile()
        profile.name = name
        profile.created_at = datetime.now().isoformat()
        
        self.profiles[profile.company_id] = profile
        self.save_profiles()
        return profile
    
    def get_profile(self, company_id: str) -> Optional[CompanyProfile]:
        """Get a company profile by ID."""
        return self.profiles.get(company_id)
    
    def update_profile(self, company_id: str, data: Dict[str, Any]) -> bool:
        """Update a company profile."""
        if company_id in self.profiles:
            profile = self.profiles[company_id]
            for key, value in data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            profile.updated_at = datetime.now().isoformat()
            self.save_profiles()
            return True
        return False
    
    def delete_profile(self, company_id: str) -> bool:
        """Delete a company profile."""
        if company_id in self.profiles:
            del self.profiles[company_id]
            self.save_profiles()
            return True
        return False
    
    def list_profiles(self) -> List[CompanyProfile]:
        """Get all company profiles."""
        return list(self.profiles.values())
    
    def clear_all_profiles(self) -> bool:
        """Clear all saved company profiles."""
        try:
            self.profiles.clear()
            self.save_profiles()
            return True
        except Exception as e:
            print(f"Error clearing profiles: {e}")
            return False
    
    def get_recent_companies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent companies in the format expected by main.py."""
        profiles = self.list_profiles()
        
        # Sort by updated_at or created_at, most recent first
        sorted_profiles = sorted(profiles, key=lambda p: p.updated_at or p.created_at or '', reverse=True)
        
        # Convert to the format expected by main.py
        recent_companies = []
        for profile in sorted_profiles[:limit]:
            company_data = {
                'name': profile.name,
                'profile': {
                    'business_input': profile.name,
                    'business_type': profile.business_type,
                    'target_audience': profile.target_audience,
                    'website_url': profile.website_url,
                    'description': profile.description
                }
            }
            recent_companies.append(company_data)
        
        return recent_companies
    
    def populate_from_website_analysis(self, analysis_results: Dict[str, Any]):
        """Populate session state from website analysis."""
        if not analysis_results.get('success'):
            return
        
        business_info = analysis_results.get('business_info', {})
        
        # Map website analysis to session state
        mapping = {
            'business_name': business_info.get('company_name', ''),
            'business_type': business_info.get('business_type', ''),
            'target_audience': business_info.get('target_audience', ''),
            'description': business_info.get('description', '')
        }
        
        for key, value in mapping.items():
            if value and value.strip():
                st.session_state[key] = value


class SessionManager:
    """Manages session state and company data integration."""
    
    def __init__(self):
        self.company_manager = CompanyManager()
    
    def load_company_to_session(self, company_id: str) -> bool:
        """Load company profile data into session state."""
        profile = self.company_manager.get_profile(company_id)
        if profile:
            # Clear widget keys to ensure they update with new session state values
            widget_keys_to_clear = [
                'business_name_input', 'business_type_input', 
                'target_audience_input', 'product_name_input', 
                'company_description_input'
            ]
            for key in widget_keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Load profile data into session state
            st.session_state['selected_company'] = company_id
            st.session_state['business_name'] = profile.name
            st.session_state['business_type'] = profile.business_type
            st.session_state['target_audience'] = profile.target_audience
            st.session_state['product_name'] = profile.product_name  # Load product_name field
            st.session_state['website_url'] = profile.website_url
            st.session_state['company_description'] = profile.description
            return True
        return False
    
    def save_session_to_company(self, company_id: str) -> bool:
        """Save current session data to company profile."""
        # Capture current values from both session state and widget state
        product_name_value = (
            st.session_state.get('product_name', '') or 
            st.session_state.get('product_name_input', '')
        )
        
        session_data = {
            'name': st.session_state.get('business_name', ''),
            'business_type': st.session_state.get('business_type', ''),
            'target_audience': st.session_state.get('target_audience', ''),
            'product_name': product_name_value,  # Use fallback logic for product_name
            'website_url': st.session_state.get('website_url', ''),
            'description': st.session_state.get('company_description', '')
        }
        
        return self.company_manager.update_profile(company_id, session_data)
    
    def populate_from_website_analysis(self, analysis_results: Dict[str, Any]):
        """Populate session state from website analysis results."""
        self.company_manager.populate_from_website_analysis(analysis_results)
    
    def clear_all_profiles(self) -> bool:
        """Clear all saved company profiles."""
        return self.company_manager.clear_all_profiles()


def show_company_selector():
    """Display company profile selector in sidebar."""
    st.sidebar.markdown("### Company Profiles")
    
    session_manager = get_session_manager()
    profiles = session_manager.company_manager.list_profiles()
    
    # Company selector
    if profiles:
        profile_options = {f"{p.name} ({p.business_type})": p.company_id for p in profiles}
        profile_options["+ New Company"] = "new"
        
        selected_display = st.sidebar.selectbox(
            "Select Company:",
            list(profile_options.keys()),
            key="company_selector"
        )
        
        selected_id = profile_options[selected_display]
        
        if selected_id == "new":
            # Create new company
            new_name = st.sidebar.text_input("Company Name:", key="new_company_name")
            if st.sidebar.button("Create Company", key="create_company_btn"):
                if new_name.strip():
                    new_profile = session_manager.company_manager.create_profile(new_name.strip())
                    session_manager.load_company_to_session(new_profile.company_id)
                    st.sidebar.success(f"Created company: {new_name}")
                    st.rerun()
                else:
                    st.sidebar.error("Please enter a company name")
        else:
            # Load existing company
            if st.session_state.get('selected_company') != selected_id:
                session_manager.load_company_to_session(selected_id)
                st.rerun()
            
            # Save current session to company
            if st.sidebar.button("Save Changes", key="save_company_btn"):
                if session_manager.save_session_to_company(selected_id):
                    st.sidebar.success("Company profile updated")
                else:
                    st.sidebar.error("Failed to save profile")
    else:
        # No profiles yet
        st.sidebar.info("No company profiles yet")
        new_name = st.sidebar.text_input("Create First Company:", key="first_company_name")
        if st.sidebar.button("Create", key="create_first_company_btn"):
            if new_name.strip():
                new_profile = session_manager.company_manager.create_profile(new_name.strip())
                session_manager.load_company_to_session(new_profile.company_id)
                st.sidebar.success(f"Created: {new_name}")
                st.rerun()


def get_session_manager():
    """Get singleton instance of SessionManager."""
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = SessionManager()
    return st.session_state.session_manager


def get_company_manager():
    """Get singleton instance of CompanyManager."""
    session_manager = get_session_manager()
    return session_manager.company_manager
