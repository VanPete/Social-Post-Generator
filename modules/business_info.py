"""
Business info and website analysis for Social Post Generator
Enhanced with GPT-powered auto-fill capabilities and 403 error handling
"""
import streamlit as st
from modules.website_analysis import get_website_analyzer

def business_info_section(ui):
    """Display business info section with enhanced website analysis."""
    st.markdown("#### Business Details")
    
    # Website URL input
    website_url = st.text_input(
        "Website URL (optional):",
        value=st.session_state.get('website_url', '') or '',
        placeholder="https://yourcompany.com",
        help="Enter your website URL to automatically extract business information using AI",
        key="website_url_input"
    )
    st.session_state.website_url = website_url

    # Auto-fill button
    if website_url:
        col_analyze, col_clear = st.columns([3, 1])
        
        with col_analyze:
            if st.button("Auto-Fill from Website", use_container_width=True, type="secondary"):
                with st.spinner("Analyzing website with AI..."):
                    analyzer = _get_website_analyzer()
                    
                    try:
                        results = analyzer.analyze_website(website_url)
                        
                        if results and results.get('success'):
                            _apply_auto_fill_results(results)
                            st.rerun()
                        else:
                            _handle_analysis_error(results)
                            
                    except Exception as analysis_error:
                        st.error(f"Analysis failed: {str(analysis_error)[:100]}")
                        st.info("This may be due to network restrictions. You can fill in details manually.")

        with col_clear:
            if st.button("Clear", use_container_width=True):
                _clear_business_data()
                st.rerun()

    st.markdown("---")
    
    # Business form with enhanced labels
    business_data = ui.create_business_form()
    
    # Check if form is complete
    required_fields = ['business_name', 'business_type']
    is_complete = all(
        (business_data.get(field) or '').strip() 
        for field in required_fields
    )
    
    return is_complete

def _get_website_analyzer():
    """Get website analyzer with OpenAI client if available."""
    try:
        from main import initialize_openai_client
        openai_client = initialize_openai_client()
        from modules.website_analysis import get_website_analyzer
        return get_website_analyzer(openai_client)
    except Exception:
        from modules.website_analysis import get_website_analyzer
        return get_website_analyzer()

def _apply_auto_fill_results(results):
    """Apply auto-fill results to session state."""
    business_info = results.get('business_info', {})
    
    # Clear any existing input keys to avoid conflicts
    input_keys = ['business_name_input', 'business_type_input', 'target_audience_input', 'product_name_input']
    for key in input_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # Auto-fill session state keys
    if business_info.get('company_name'):
        st.session_state.business_name = business_info['company_name']
    
    if business_info.get('business_type'):
        st.session_state.business_type = business_info['business_type']
    
    if business_info.get('target_audience'):
        st.session_state.target_audience = business_info['target_audience']
    
    if business_info.get('product_service'):
        st.session_state.product_name = business_info['product_service']
    
    if business_info.get('description'):
        st.session_state.company_description = business_info['description']
    
    # Show success message
    extracted_fields = []
    for field, label in [
        ('company_name', 'Business Name'),
        ('business_type', 'Business Type'),
        ('target_audience', 'Target Audience'),
        ('product_service', 'Product/Service'),
        ('description', 'Company Description')
    ]:
        if business_info.get(field):
            extracted_fields.append(label)
    
    if extracted_fields:
        st.success(f"Auto-filled: {', '.join(extracted_fields)}")
    else:
        st.info("Website analyzed but limited information could be extracted. Please fill in details manually.")

def _handle_analysis_error(results):
    """Handle website analysis errors with helpful guidance."""
    error_msg = results.get('error', 'Could not analyze website') if results else 'Analysis failed'
    
    if '403' in error_msg or 'Forbidden' in error_msg:
        st.error("Website access blocked. This is common with business websites that protect against automated access.")
        st.info("Please fill in the business details manually below. The information you enter will be used to generate targeted social media captions.")
    elif 'Failed to fetch' in error_msg:
        st.warning(f"Could not connect to website: {error_msg}")
        st.info("Please check the URL and try again, or fill in details manually.")
    else:
        st.error(f"Website analysis failed: {error_msg}")

def _clear_business_data():
    """Clear business data from session state."""
    keys_to_clear = [
        'website_url', 'website_analysis_results', 
        'business_name', 'business_type', 'target_audience', 'product_name', 'company_description'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
