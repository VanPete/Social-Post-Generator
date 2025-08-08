"""
Business info and website analysis for Social Post Generator
Enhanced with GPT-powered auto-fill capabilities and 403 error handling
"""
import streamlit as st
from modules.website_analysis import get_website_analyzer
from modules.companies import get_session_manager

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
                    # Get OpenAI client for enhanced analysis
                    openai_client = None
                    try:
                        # Try multiple ways to import the OpenAI client
                        try:
                            from main import initialize_openai_client
                            openai_client = initialize_openai_client()
                        except ImportError:
                            # Alternative import method for cloud environments
                            import importlib.util
                            import os
                            main_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.py')
                            spec = importlib.util.spec_from_file_location("main", main_path)
                            main_module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(main_module)
                            openai_client = main_module.initialize_openai_client()
                        
                        if openai_client:
                            analyzer = get_website_analyzer(openai_client)
                            st.sidebar.success("✅ Using GPT-enhanced analysis")
                        else:
                            analyzer = get_website_analyzer()
                            st.sidebar.warning("⚠️ Using basic analysis (GPT unavailable)")
                            
                    except Exception as e:
                        # Fallback to basic analysis
                        analyzer = get_website_analyzer()
                        st.sidebar.warning(f"⚠️ Using basic analysis (Error: {str(e)[:30]}...)")
                    
                    results = analyzer.analyze_website(website_url)
                    
                    # Debug info for troubleshooting
                    if st.sidebar.checkbox("Show Debug Info", value=False):
                        st.sidebar.json({
                            "analyzer_type": "GPT" if hasattr(analyzer, 'openai_client') and analyzer.openai_client else "Basic",
                            "results_success": results.get('success', False) if results else False,
                            "extracted_fields": len(results.get('business_info', {})) if results and results.get('success') else 0
                        })
                    
                    if results and results.get('success'):
                        st.session_state.website_analysis_results = results
                        
                        # Enhanced auto-fill with all extracted fields
                        business_info = results.get('business_info', {})
                        
                        # Auto-fill all available fields
                        if business_info.get('company_name'):
                            st.session_state.business_name = business_info['company_name']
                        
                        if business_info.get('business_type'):
                            st.session_state.business_type = business_info['business_type']
                        
                        if business_info.get('target_audience'):
                            st.session_state.target_audience = business_info['target_audience']
                        
                        if business_info.get('product_service'):
                            st.session_state.product_name = business_info['product_service']
                        
                        # Show success message with what was extracted
                        extracted_fields = []
                        if business_info.get('company_name'):
                            extracted_fields.append("Business Name")
                        if business_info.get('business_type'):
                            extracted_fields.append("Business Type")
                        if business_info.get('target_audience'):
                            extracted_fields.append("Target Audience")
                        if business_info.get('product_service'):
                            extracted_fields.append("Product/Service")
                        
                        if extracted_fields:
                            st.success(f"Auto-filled: {', '.join(extracted_fields)}")
                        else:
                            st.info("Website analyzed but limited information could be extracted. Please fill in details manually.")
                        
                        st.rerun()
                    else:
                        error_msg = results.get('error', 'Could not analyze website') if results else 'Analysis failed'
                        
                        # Provide helpful guidance for 403 errors
                        if '403' in error_msg or 'Forbidden' in error_msg:
                            st.error("Website access blocked. This is common with business websites that protect against automated access.")
                            st.info("Please fill in the business details manually below. The information you enter will be used to generate targeted social media captions.")
                        elif 'Failed to fetch' in error_msg:
                            st.warning(f"Could not connect to website: {error_msg}")
                            st.info("Please check the URL and try again, or fill in details manually.")
                        else:
                            st.error(f"Website analysis failed: {error_msg}")
        
        with col_clear:
            if st.button("Clear", use_container_width=True):
                keys_to_clear = [
                    'website_url', 'website_analysis_results', 
                    'business_name', 'business_type', 'target_audience', 'product_name'
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    st.markdown("---")
    
    # Business form with enhanced labels
    business_data = ui.create_business_form()
    
    # Show extraction results if available
    if st.session_state.get('website_analysis_results'):
        results = st.session_state.website_analysis_results
        if results.get('success'):
            business_info = results.get('business_info', {})
            if business_info.get('description'):
                with st.expander("AI-Extracted Business Description", expanded=False):
                    st.write(business_info['description'])
    
    # Check if form is complete - handle None values properly
    required_fields = ['business_name', 'business_type']
    is_complete = all(
        (business_data.get(field) or '').strip() 
        for field in required_fields
    )
    
    return is_complete
