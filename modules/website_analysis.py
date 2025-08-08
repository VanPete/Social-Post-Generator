#!/usr/bin/env python3
"""
Website analysis module for Social Post Generator
Enhanced with GPT-powered business information extraction and 403 error mitigation
"""

import requests
from bs4 import BeautifulSoup
import streamlit as st
from urllib.parse import urljoin, urlparse
from typing import Dict, Any, Optional
import openai
import random
import time

class WebsiteAnalyzer:
    """Analyzes websites to extract business information using web scraping and GPT."""
    
    def __init__(self, openai_client=None):
        # Rotate between multiple realistic user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        self.openai_client = openai_client
    
    def _get_headers(self):
        """Get randomized headers to avoid bot detection."""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
    
    def analyze_website(self, url: str) -> Dict[str, Any]:
        """Analyze a website with multiple fallback strategies for 403 errors."""
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Try multiple strategies to bypass 403 errors
            content = None
            final_url = url
            
            # Strategy 1: Standard request with rotating headers
            try:
                content, final_url = self._fetch_with_headers(url)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    st.warning("Website blocked direct access. Trying alternative methods...")
                    
                    # Strategy 2: Try with session and delay
                    try:
                        content, final_url = self._fetch_with_session(url)
                    except:
                        # Strategy 3: Try different URL variations
                        content, final_url = self._try_url_variations(url)
                else:
                    raise e
            
            if not content:
                return {
                    'success': False,
                    'error': "Could not access website content after trying multiple methods"
                }
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract raw content
            raw_content = self._extract_raw_content(soup)
            
            # Use GPT to enhance extraction if client available
            if self.openai_client and raw_content:
                business_info = self._extract_with_gpt(raw_content, final_url)
            else:
                # Fallback to basic extraction
                business_info = self._extract_business_info_basic(soup, final_url)
            
            return {
                'success': True,
                'url': final_url,
                'business_info': business_info
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"Failed to fetch website: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error analyzing website: {str(e)}"
            }
    
    def _fetch_with_headers(self, url: str) -> tuple:
        """Fetch website content with randomized headers."""
        headers = self._get_headers()
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        return response.content, response.url
    
    def _fetch_with_session(self, url: str) -> tuple:
        """Fetch website content using session with delay."""
        session = requests.Session()
        session.headers.update(self._get_headers())
        
        # Add small delay to appear more human-like
        time.sleep(random.uniform(1, 3))
        
        response = session.get(url, timeout=15, allow_redirects=True)
        response.raise_for_status()
        return response.content, response.url
    
    def _try_url_variations(self, url: str) -> tuple:
        """Try different URL variations to bypass restrictions."""
        parsed = urlparse(url)
        
        # Try different URL variations
        variations = [
            f"{parsed.scheme}://www.{parsed.netloc}{parsed.path}",  # Add www
            f"{parsed.scheme}://{parsed.netloc.replace('www.', '')}{parsed.path}",  # Remove www
            f"https://{parsed.netloc}{parsed.path}",  # Force HTTPS
            f"http://{parsed.netloc}{parsed.path}",   # Try HTTP
        ]
        
        # Remove duplicates and original URL
        variations = list(set(variations))
        if url in variations:
            variations.remove(url)
        
        for variation in variations:
            try:
                headers = self._get_headers()
                time.sleep(random.uniform(0.5, 2))  # Random delay
                
                response = requests.get(variation, headers=headers, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    return response.content, response.url
            except:
                continue
        
        # If all variations fail, try to get basic info from domain
        try:
            domain_url = f"{parsed.scheme}://{parsed.netloc}"
            headers = self._get_headers()
            response = requests.get(domain_url, headers=headers, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                return response.content, response.url
        except:
            pass
        
        raise requests.exceptions.RequestException("All URL variations failed")
    
    def _extract_raw_content(self, soup: BeautifulSoup) -> str:
        """Extract relevant text content from website for GPT analysis."""
        content_parts = []
        
        # Get title
        title = soup.find('title')
        if title:
            content_parts.append(f"Title: {title.get_text().strip()}")
        
        # Get meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            content_parts.append(f"Description: {meta_desc['content'].strip()}")
        
        # Get main headings
        headings = soup.find_all(['h1', 'h2', 'h3'], limit=5)
        for h in headings:
            content_parts.append(f"Heading: {h.get_text().strip()}")
        
        # Get first few paragraphs
        paragraphs = soup.find_all('p', limit=8)
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 30:  # Only meaningful paragraphs
                content_parts.append(f"Content: {text[:200]}")
        
        # Get about section if exists
        about_section = soup.find(['section', 'div'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['about', 'company', 'business', 'who-we-are']
        ))
        if about_section:
            about_text = about_section.get_text()[:500]
            content_parts.append(f"About Section: {about_text}")
        
        return '\n'.join(content_parts)
    
    def _extract_with_gpt(self, content: str, url: str) -> Dict[str, str]:
        """Use GPT to extract structured business information from website content."""
        try:
            prompt = f"""Analyze this website content and extract the following business information in JSON format:

Website URL: {url}
Website Content:
{content[:2000]}

Please extract:
1. company_name: The business/company name
2. business_type: What type of business this is (e.g., "Restaurant", "Tech Startup", "Marketing Agency")
3. target_audience: Who their target customers are (e.g., "Small business owners", "Young professionals", "Families")
4. product_service: Their main product or service offering
5. description: A brief description of what they do

Return ONLY a JSON object with these 5 fields. If information is not clear, provide your best inference based on the content.

Example format:
{{
    "company_name": "ABC Marketing",
    "business_type": "Digital Marketing Agency", 
    "target_audience": "Small to medium businesses",
    "product_service": "Social media management and digital advertising",
    "description": "Full-service digital marketing agency helping SMBs grow online"
}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a business analyst expert at extracting company information from website content. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse JSON response
            import json
            gpt_response = response.choices[0].message.content.strip()
            
            # Clean response if it has markdown formatting
            if gpt_response.startswith('```json'):
                gpt_response = gpt_response.replace('```json', '').replace('```', '').strip()
            
            business_info = json.loads(gpt_response)
            
            # Validate required fields exist
            required_fields = ['company_name', 'business_type', 'target_audience', 'product_service', 'description']
            for field in required_fields:
                if field not in business_info:
                    business_info[field] = ""
            
            return business_info
            
        except Exception as e:
            print(f"GPT extraction failed: {e}")
            # Fallback to basic extraction
            return self._extract_business_info_basic_from_content(content)
    
    def _extract_business_info_basic(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        """Basic extraction without GPT (fallback method)."""
        info = {}
        
        # Extract company name
        info['company_name'] = self._extract_company_name(soup)
        
        # Extract business type/description
        info['business_type'] = self._extract_business_type(soup)
        
        # Extract description
        info['description'] = self._extract_description(soup)
        
        # Extract target audience (basic inference)
        info['target_audience'] = self._infer_target_audience(soup)
        
        # Extract product/service
        info['product_service'] = self._extract_product_service(soup)
        
        return info
    
    def _extract_business_info_basic_from_content(self, content: str) -> Dict[str, str]:
        """Extract basic info from raw content (GPT fallback)."""
        lines = content.split('\n')
        info = {
            'company_name': '',
            'business_type': '',
            'target_audience': 'general audience',
            'product_service': '',
            'description': ''
        }
        
        # Try to extract company name from title
        for line in lines:
            if line.startswith('Title:'):
                title = line.replace('Title:', '').strip()
                # Clean common suffixes
                for suffix in [' - Home', ' | Home', ' - Official Website']:
                    if title.endswith(suffix):
                        title = title[:-len(suffix)]
                info['company_name'] = title
                break
        
        # Extract description from meta description
        for line in lines:
            if line.startswith('Description:'):
                info['description'] = line.replace('Description:', '').strip()
                break
        
        return info
    
    def _extract_company_name(self, soup: BeautifulSoup) -> str:
        """Extract company name from website."""
        # Try title tag first
        title = soup.find('title')
        if title:
            title_text = title.get_text().strip()
            
            # Remove common suffixes and prefixes
            suffixes_to_remove = [
                ' - Home', ' | Home', ' - Official Website', ' | Official Site',
                ' - Homepage', ' | Homepage', ' Home Page', ' | Home Page',
                ' | Official Website', ' - Official Site', ' | Main Page',
                ' - Main Page', ' | Welcome', ' - Welcome'
            ]
            
            for suffix in suffixes_to_remove:
                if title_text.endswith(suffix):
                    title_text = title_text[:-len(suffix)]
            
            # Clean up common business descriptors at the end
            descriptors_to_remove = [
                ' in Columbus, OH', ' in Columbus, Ohio', ' - Columbus, OH',
                ' | Columbus, OH', ' Columbus, OH', ' Columbus Ohio'
            ]
            
            for descriptor in descriptors_to_remove:
                if title_text.endswith(descriptor):
                    title_text = title_text[:-len(descriptor)]
            
            # Extract just the company name if it contains descriptive text
            # Look for patterns like "Company Name | Description" or "Company Name - Description"
            if ' | ' in title_text and not any(word in title_text.lower() for word in ['home', 'welcome', 'official']):
                # Take the first part before the pipe
                parts = title_text.split(' | ')
                if len(parts) > 1:
                    title_text = parts[-1].strip()  # Take the last part (usually company name)
            
            if title_text:
                return title_text.strip()
        
        # Try h1 tag
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        # Try meta property og:site_name
        og_site = soup.find('meta', property='og:site_name')
        if og_site and og_site.get('content'):
            return og_site['content'].strip()
        
        return ""
    
    def _extract_business_type(self, soup: BeautifulSoup) -> str:
        """Extract business type from website."""
        # Look for about section
        about_section = soup.find(['section', 'div'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['about', 'company', 'business']
        ))
        
        if about_section:
            text = about_section.get_text()[:200]
            # Simple business type inference
            business_types = {
                'Restaurant': ['restaurant', 'dining', 'food', 'cuisine', 'menu'],
                'Tech Company': ['software', 'technology', 'app', 'digital', 'tech'],
                'Retail Store': ['shop', 'store', 'retail', 'products', 'merchandise'],
                'Service Provider': ['service', 'consulting', 'solution', 'professional'],
                'Healthcare': ['health', 'medical', 'doctor', 'clinic', 'hospital'],
                'Education': ['education', 'school', 'training', 'course', 'learn']
            }
            
            text_lower = text.lower()
            for biz_type, keywords in business_types.items():
                if any(keyword in text_lower for keyword in keywords):
                    return biz_type
        
        return ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract business description from website."""
        # Try meta description first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Try og:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        # Try first paragraph
        first_p = soup.find('p')
        if first_p:
            return first_p.get_text().strip()[:200]
        
        return ""
    
    def _infer_target_audience(self, soup: BeautifulSoup) -> str:
        """Infer target audience from website content."""
        text_content = soup.get_text().lower()
        
        # Simple audience inference based on keywords
        audiences = {
            'Small business owners': ['small business', 'entrepreneur', 'startup'],
            'Professionals': ['professional', 'corporate', 'business executive'],
            'Families': ['family', 'parents', 'children', 'kids'],
            'Young adults': ['millennial', 'young adult', 'college', 'student'],
            'Seniors': ['senior', 'retirement', 'elderly', 'mature']
        }
        
        for audience, keywords in audiences.items():
            if any(keyword in text_content for keyword in keywords):
                return audience
        
        return "General audience"
    
    def _extract_product_service(self, soup: BeautifulSoup) -> str:
        """Extract main product or service offering."""
        # Look for services/products sections
        service_section = soup.find(['section', 'div'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['service', 'product', 'offering', 'solution']
        ))
        
        if service_section:
            text = service_section.get_text().strip()[:150]
            return text
        
        # Try to find from headings
        headings = soup.find_all(['h2', 'h3'], limit=3)
        for h in headings:
            text = h.get_text().strip()
            if any(word in text.lower() for word in ['service', 'product', 'solution', 'offering']):
                return text
        
        return ""


def get_website_analyzer(openai_client=None):
    """Get singleton instance of WebsiteAnalyzer."""
    # Create a unique key based on whether OpenAI client is available
    key = f'website_analyzer_{"gpt" if openai_client else "basic"}'
    
    if key not in st.session_state or (openai_client and not hasattr(st.session_state[key], 'openai_client')):
        st.session_state[key] = WebsiteAnalyzer(openai_client)
    
    return st.session_state[key]
