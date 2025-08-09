#!/usr/bin/env python3
"""
Caption generation module for Social Post Generator
"""

import openai
import streamlit as st
from config.constants import OPENAI_MODELS
from typing import Tuple, List, Optional
import base64
import io
from PIL import Image

class CaptionGenerator:
    """Handles AI-powered caption generation."""
    
    def __init__(self, openai_client):
        self.client = openai_client
    
    def analyze_image(self, image_file) -> Optional[str]:
        """Analyze uploaded image to understand its content for caption generation."""
        try:
            # Handle Streamlit UploadedFile objects properly
            if hasattr(image_file, 'read'):
                image_file.seek(0)
                image_bytes = image_file.read()
                image_file.seek(0)
            else:
                image_bytes = image_file
            
            if not image_bytes:
                return None
            
            # Use PIL to properly handle the image and convert to supported format
            from PIL import Image
            import io
            
            image_stream = io.BytesIO(image_bytes)
            pil_image = Image.open(image_stream)
            
            # Convert to RGB if necessary (for transparency or other modes)
            if pil_image.mode in ('RGBA', 'LA', 'P'):
                rgb_image = Image.new('RGB', pil_image.size, (255, 255, 255))
                if pil_image.mode == 'P':
                    pil_image = pil_image.convert('RGBA')
                rgb_image.paste(pil_image, mask=pil_image.split()[-1] if pil_image.mode in ('RGBA', 'LA') else None)
                pil_image = rgb_image
            
            # Save as JPEG to ensure compatibility
            output_buffer = io.BytesIO()
            pil_image.save(output_buffer, format='JPEG', quality=85)
            processed_image_bytes = output_buffer.getvalue()
            
            # Convert to base64
            base64_image = base64.b64encode(processed_image_bytes).decode('utf-8')
            
            # Analyze image with GPT-4o (Vision model)
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this image for social media caption generation. Describe: 1) What you see in the image, 2) The mood/tone, 3) Key visual elements, 4) What type of business/service this might represent. Be concise but detailed."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error analyzing image: {str(e)}")
            return None
    
    def generate_captions(self, **params) -> Tuple[bool, List[str], Optional[str]]:
        """Generate social media captions based on business parameters and optional image."""
        try:
            # Extract parameters
            business_name = params.get('business_name', '')
            business_type = params.get('business_type', '')
            target_audience = params.get('target_audience', '')
            product_name = params.get('product_name', '')
            company_description = params.get('company_description', '')
            platform_char_limit = params.get('platform_char_limit')
            selected_platform = params.get('selected_platform', '')
            model = params.get('model', OPENAI_MODELS["standard"])
            include_cta = params.get('include_cta', False)
            image_analysis = params.get('image_analysis', None)  # New parameter for image description
            
            # Build prompt with optional image context
            prompt = self._build_prompt(
                business_name, business_type, target_audience, 
                product_name, company_description, platform_char_limit, selected_platform, include_cta, image_analysis
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
                     product_name: str, company_description: str, char_limit: Optional[int], platform: str, include_cta: bool, 
                     image_analysis: Optional[str] = None) -> str:
        """Build the AI prompt for caption generation."""
        prompt = f"""Create 2 engaging social media captions for:

Business: {business_name}
Type: {business_type}
Target Audience: {target_audience}"""
        
        if product_name:
            prompt += f"\nProduct/Service: {product_name}"
        
        if company_description:
            prompt += f"\nCompany Description: {company_description}"
        
        if image_analysis:
            prompt += f"\n\nImage Context: {image_analysis}"
            prompt += "\nIMPORTANT: Reference the uploaded image in your captions. Make the captions match what's shown in the image."
        
        if platform and platform not in ["All Social Platforms", "2-3 sentences", "3-4 sentences", "4-5 sentences (Default)"]:
            prompt += f"\nPlatform: {platform}"
        
        if char_limit:
            prompt += f"\nCharacter Limit: {char_limit} characters"
        elif platform == "2-3 sentences":
            prompt += f"\nLength: 2-3 sentences for optimal engagement"
        elif platform == "3-4 sentences":
            prompt += f"\nLength: 3-4 sentences for detailed engagement"
        elif platform == "4-5 sentences (Default)":
            prompt += f"\nLength: 4-5 sentences for comprehensive engagement"
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
Caption 2: [caption text]"""
        
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
        
        return captions[:2]  # Return max 2 captions

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
        'company_description': st.session_state.get('company_description', ''),
        'platform_char_limit': st.session_state.get('platform_char_limit'),
        'selected_platform': st.session_state.get('selected_platform', ''),
        'model': st.session_state.get('openai_model', OPENAI_MODELS["standard"]),
        'image_count': st.session_state.get('image_count', 1),
        'include_cta': st.session_state.get('include_cta', False)
    }
    
    # Check for uploaded images and analyze them
    uploaded_images = st.session_state.get('uploaded_images', [])
    all_captions = []
    
    if uploaded_images:
        try:
            from main import initialize_openai_client
            openai_client = initialize_openai_client()
            caption_generator = get_caption_generator(openai_client)
            
            with st.spinner(f"Analyzing {len(uploaded_images)} image(s) and generating captions..."):
                for i, image_file in enumerate(uploaded_images, 1):
                    try:
                        # Analyze current image
                        image_analysis = caption_generator.analyze_image(image_file)
                        
                        if image_analysis:
                            # Generate captions for this specific image
                            params_with_image = params.copy()
                            params_with_image['image_analysis'] = image_analysis
                            
                            success, captions, error_msg = caption_generator.generate_captions(**params_with_image)
                            
                            if success:
                                # Add image context to captions for display
                                image_captions = {
                                    'image_name': image_file.name,
                                    'image_file': image_file,
                                    'captions': captions,
                                    'image_analysis': image_analysis
                                }
                                all_captions.append(image_captions)
                    
                    except Exception as img_error:
                        st.error(f"Error processing image {i}: {str(img_error)}")
                
                if all_captions:
                    st.session_state.generated_captions = all_captions
                    st.success(f"✅ Generated captions for {len(all_captions)} image(s)!")
                    return True
                else:
                    st.error("No captions could be generated for any images")
                    return False
                    
        except Exception as e:
            st.error(f"Error during image caption generation: {str(e)}")
            return False
    else:
        # No images - generate standard captions
        params['image_analysis'] = None
    
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
