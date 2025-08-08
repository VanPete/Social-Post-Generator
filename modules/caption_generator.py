#!/usr/bin/env python3
"""
Caption generation module for Social Post Generator
"""

import openai
import streamlit as st
from config.constants import OPENAI_MODELS
from typing import Tuple, List, Optional

class CaptionGenerator:
    """Handles AI-powered caption generation."""
    
    def __init__(self, openai_client):
        self.client = openai_client
    
    def generate_captions(self, **params) -> Tuple[bool, List[str], Optional[str]]:
        """Generate social media captions based on business parameters."""
        try:
            # Extract parameters
            business_name = params.get('business_name', '')
            business_type = params.get('business_type', '')
            target_audience = params.get('target_audience', '')
            product_name = params.get('product_name', '')
            platform_char_limit = params.get('platform_char_limit')
            selected_platform = params.get('selected_platform', '')
            model = params.get('model', OPENAI_MODELS["standard"])
            include_cta = params.get('include_cta', False)
            
            # Build prompt
            prompt = self._build_prompt(
                business_name, business_type, target_audience, 
                product_name, platform_char_limit, selected_platform, include_cta
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional social media content creator specializing in engaging, brand-appropriate captions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            captions = self._parse_captions(content)
            
            return True, captions, None
            
        except Exception as e:
            return False, [], str(e)
    
    def _build_prompt(self, business_name: str, business_type: str, target_audience: str, 
                     product_name: str, char_limit: Optional[int], platform: str, include_cta: bool) -> str:
        """Build the AI prompt for caption generation."""
        prompt = f"""Create 3 engaging social media captions for:

Business: {business_name}
Type: {business_type}
Target Audience: {target_audience}"""
        
        if product_name:
            prompt += f"\nProduct/Service: {product_name}"
        
        if platform and platform not in ["All Social Platforms (Default)", "2-3 sentences", "3-4 sentences"]:
            prompt += f"\nPlatform: {platform}"
        
        if char_limit:
            prompt += f"\nCharacter Limit: {char_limit} characters"
        elif platform == "2-3 sentences":
            prompt += f"\nLength: 2-3 sentences for optimal engagement"
        elif platform == "3-4 sentences":
            prompt += f"\nLength: 3-4 sentences for detailed engagement"
        else:
            prompt += f"\nLength: Character fitting for all social platforms"
        
        prompt += f"""

Requirements:
- Write in an engaging, professional tone
- Focus on value proposition and benefits
- Target the specified audience
- Make each caption unique and compelling
- NO hashtags or emojis
- Clean, readable format"""
        
        if include_cta:
            prompt += "\n- Include a clear call-to-action"
        
        prompt += """

Format your response as:
Caption 1: [caption text]
Caption 2: [caption text]
Caption 3: [caption text]"""
        
        return prompt
    
    def _parse_captions(self, content: str) -> List[str]:
        """Parse captions from AI response."""
        captions = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('Caption'):
                # Extract caption after the colon
                if ':' in line:
                    caption = line.split(':', 1)[1].strip()
                    if caption:
                        captions.append(caption)
        
        # Fallback: if parsing fails, try to split by numbers
        if not captions:
            import re
            caption_pattern = r'\d+[\.\)]\s*(.+?)(?=\d+[\.\)]|$)'
            matches = re.findall(caption_pattern, content, re.DOTALL)
            captions = [match.strip() for match in matches if match.strip()]
        
        # Final fallback: split by double newlines
        if not captions:
            parts = content.split('\n\n')
            captions = [part.strip() for part in parts if part.strip()]
        
        return captions[:3]  # Return max 3 captions

def get_caption_generator(openai_client):
    """Get singleton instance of CaptionGenerator."""
    if 'caption_generator' not in st.session_state:
        st.session_state.caption_generator = CaptionGenerator(openai_client)
    return st.session_state.caption_generator

def trigger_caption_generation(st):
    """Trigger caption generation and update session state."""
    # Clear previous results
    st.session_state.generated_captions = []
    st.session_state.trigger_generate_captions = False
    
    # Collect parameters from session state
    params = {
        'business_name': st.session_state.get('business_name', ''),
        'business_type': st.session_state.get('business_type', ''),
        'target_audience': st.session_state.get('target_audience', ''),
        'product_name': st.session_state.get('product_name', ''),
        'platform_char_limit': st.session_state.get('platform_char_limit'),
        'selected_platform': st.session_state.get('selected_platform', ''),
        'model': st.session_state.get('openai_model', OPENAI_MODELS["standard"]),
        'image_count': st.session_state.get('image_count', 1),
        'include_cta': st.session_state.get('include_cta', False)
    }
    
    # Validate required parameters
    required_params = ['business_name', 'business_type']
    missing_params = [p for p in required_params if not params[p].strip()]
    
    if missing_params:
        st.error(f"Please fill in required fields: {', '.join(missing_params)}")
        return False
    
    # Generate captions
    try:
        from main import initialize_openai_client
        openai_client = initialize_openai_client()
        caption_generator = get_caption_generator(openai_client)
        
        success, captions, error_msg = caption_generator.generate_captions(**params)
        
        if success:
            st.session_state.generated_captions = captions
            return True
        else:
            st.error(f"Caption generation failed: {error_msg}")
            return False
            
    except Exception as e:
        st.error(f"Error during caption generation: {str(e)}")
        return False
