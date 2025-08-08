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
            # Add to debug log if available
            def add_debug(message):
                if hasattr(st, 'session_state') and 'debug_log' in st.session_state:
                    st.session_state.debug_log.append(message)
                st.write(message)
            
            add_debug("🔍 DEBUG: Starting image analysis...")
            add_debug(f"🔍 DEBUG: Image file type: {type(image_file)}")
            
            # Handle Streamlit UploadedFile objects properly
            if hasattr(image_file, 'read'):
                # Reset file pointer to beginning
                image_file.seek(0)
                image_bytes = image_file.read()
                # Reset again for future reads
                image_file.seek(0)
                add_debug(f"✅ DEBUG: Read {len(image_bytes)} bytes from uploaded file")
            else:
                # If it's already bytes
                image_bytes = image_file
                add_debug(f"✅ DEBUG: Using provided bytes: {len(image_bytes)} bytes")
            
            # Check if we actually got data
            if not image_bytes:
                add_debug("❌ DEBUG: No image data found")
                return None
            
            # Use PIL to properly handle the image and convert to supported format
            from PIL import Image
            import io
            
            # Create BytesIO object and try to open with PIL
            image_stream = io.BytesIO(image_bytes)
            add_debug(f"✅ DEBUG: Created BytesIO stream with {len(image_bytes)} bytes")
            
            try:
                pil_image = Image.open(image_stream)
                add_debug(f"✅ DEBUG: PIL opened image - Format: {pil_image.format}, Mode: {pil_image.mode}, Size: {pil_image.size}")
            except Exception as pil_error:
                add_debug(f"❌ DEBUG: PIL failed to open image: {str(pil_error)}")
                # Try reading the file again in case of stream position issues
                if hasattr(image_file, 'read'):
                    image_file.seek(0)
                    image_bytes = image_file.read()
                    image_file.seek(0)
                    image_stream = io.BytesIO(image_bytes)
                    pil_image = Image.open(image_stream)
                    add_debug(f"✅ DEBUG: PIL opened image on retry - Format: {pil_image.format}, Mode: {pil_image.mode}, Size: {pil_image.size}")
                else:
                    raise pil_error
            
            # Convert to RGB if necessary (for transparency or other modes)
            if pil_image.mode in ('RGBA', 'LA', 'P'):
                # Convert to RGB by adding white background
                rgb_image = Image.new('RGB', pil_image.size, (255, 255, 255))
                if pil_image.mode == 'P':
                    pil_image = pil_image.convert('RGBA')
                rgb_image.paste(pil_image, mask=pil_image.split()[-1] if pil_image.mode in ('RGBA', 'LA') else None)
                pil_image = rgb_image
                add_debug("✅ DEBUG: Converted image to RGB mode")
            
            # Save as JPEG to ensure compatibility
            output_buffer = io.BytesIO()
            pil_image.save(output_buffer, format='JPEG', quality=85)
            processed_image_bytes = output_buffer.getvalue()
            
            add_debug(f"✅ DEBUG: Image processed and converted to JPEG ({len(processed_image_bytes)} bytes)")
            
            # Convert to base64
            base64_image = base64.b64encode(processed_image_bytes).decode('utf-8')
            add_debug(f"✅ DEBUG: Image converted to base64 (length: {len(base64_image)} chars)")
            
            # Analyze image with GPT-4o (Vision model)
            add_debug("🔍 DEBUG: Calling OpenAI Vision API...")
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use GPT-4o for vision capabilities
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
            
            add_debug("✅ DEBUG: OpenAI Vision API call completed")
            
            result = response.choices[0].message.content.strip()
            add_debug(f"✅ DEBUG: Analysis result length: {len(result)} characters")
            add_debug(f"📝 DEBUG: Analysis preview: {result[:100]}...")
            
            return result
            
        except Exception as e:
            error_msg = f"❌ DEBUG: Error analyzing image: {str(e)}"
            if hasattr(st, 'session_state') and 'debug_log' in st.session_state:
                st.session_state.debug_log.append(error_msg)
            st.error(error_msg)
            import traceback
            error_details = traceback.format_exc()
            if hasattr(st, 'session_state') and 'debug_log' in st.session_state:
                st.session_state.debug_log.append(f"🔍 DEBUG: Full traceback: {error_details}")
            st.code(error_details)
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
    # Initialize debug log in session state
    if 'debug_log' not in st.session_state:
        st.session_state.debug_log = []
    
    def add_debug(message):
        st.session_state.debug_log.append(message)
        st.write(message)  # Also show immediately
    
    # Clear previous results and debug log
    st.session_state.generated_captions = []
    st.session_state.trigger_generate_captions = False
    st.session_state.debug_log = []
    
    add_debug("🔄 Starting caption generation process...")
    
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
        # Generate captions for each uploaded image
        try:
            add_debug(f"🔍 DEBUG: Found {len(uploaded_images)} uploaded images")
            
            from main import initialize_openai_client
            openai_client = initialize_openai_client()
            caption_generator = get_caption_generator(openai_client)
            
            add_debug(f"✅ DEBUG: OpenAI client and caption generator initialized")
            
            with st.spinner(f"Analyzing {len(uploaded_images)} image(s) and generating captions..."):
                for i, image_file in enumerate(uploaded_images, 1):
                    try:
                        add_debug(f"📷 Processing image {i} of {len(uploaded_images)}: {image_file.name}")
                        
                        # Analyze current image
                        add_debug(f"🔍 DEBUG: Starting analysis for image {i}")
                        image_analysis = caption_generator.analyze_image(image_file)
                        
                        if image_analysis:
                            add_debug(f"✅ DEBUG: Image {i} analyzed successfully")
                            add_debug(f"📝 DEBUG: Analysis preview: {image_analysis[:100]}...")
                            
                            # Generate captions for this specific image
                            params_with_image = params.copy()
                            params_with_image['image_analysis'] = image_analysis
                            
                            add_debug(f"🔍 DEBUG: Calling generate_captions for image {i}")
                            success, captions, error_msg = caption_generator.generate_captions(**params_with_image)
                            
                            if success:
                                add_debug(f"✅ DEBUG: Generated {len(captions)} captions for image {i}")
                                add_debug(f"📝 DEBUG: First caption preview: {captions[0][:50]}..." if captions else "📝 DEBUG: No captions returned")
                                
                                # Add image context to captions for display
                                image_captions = {
                                    'image_name': image_file.name,
                                    'image_file': image_file,
                                    'captions': captions,
                                    'image_analysis': image_analysis
                                }
                                all_captions.append(image_captions)
                            else:
                                add_debug(f"❌ DEBUG: Failed to generate captions for {image_file.name}: {error_msg}")
                        else:
                            add_debug(f"⚠️ DEBUG: Could not analyze {image_file.name} - image_analysis is None")
                    
                    except Exception as img_error:
                        add_debug(f"❌ DEBUG: Exception processing image {i}: {str(img_error)}")
                        import traceback
                        error_details = traceback.format_exc()
                        add_debug(f"🔍 DEBUG: Full traceback: {error_details}")
                
                add_debug(f"🔍 DEBUG: Total image caption sets generated: {len(all_captions)}")
                
                if all_captions:
                    st.session_state.generated_captions = all_captions
                    add_debug(f"✅ DEBUG: Stored {len(all_captions)} caption sets in session state")
                    st.success(f"✅ Generated captions for {len(all_captions)} image(s)!")
                    return True
                else:
                    add_debug("❌ DEBUG: No captions could be generated for any images - all_captions is empty")
                    return False
                    
        except Exception as e:
            add_debug(f"❌ DEBUG: Error during image caption generation: {str(e)}")
            import traceback
            error_details = traceback.format_exc()
            add_debug(f"🔍 DEBUG: Full traceback: {error_details}")
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
