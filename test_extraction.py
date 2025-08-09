#!/usr/bin/env python3
"""
Quick diagnostic script to test website extraction outside of Streamlit
"""
import requests
from bs4 import BeautifulSoup
import sys

def test_extraction(url):
    print(f"Testing extraction for: {url}")
    print("-" * 50)
    
    try:
        # Test basic fetch
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        print(f"✅ Fetch successful: {response.status_code}")
        print(f"📊 Content length: {len(response.text)} chars")
        
        # Test BeautifulSoup parsing
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"✅ BeautifulSoup parsing successful")
        
        # Test basic element extraction
        title = soup.find('title')
        print(f"📝 Title: {'Found' if title else 'Not found'}")
        if title:
            print(f"   Text: {title.get_text().strip()[:100]}")
        
        headings = soup.find_all(['h1', 'h2', 'h3'])
        print(f"📝 Headings: {len(headings)} found")
        
        paragraphs = soup.find_all('p')
        meaningful_p = [p for p in paragraphs if len(p.get_text().strip()) > 30]
        print(f"📝 Paragraphs: {len(paragraphs)} total, {len(meaningful_p)} meaningful")
        
        # Test meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        print(f"📝 Meta description: {'Found' if meta_desc else 'Not found'}")
        
        print("\n" + "=" * 50)
        print("DIAGNOSIS:")
        
        if len(response.text) == 0:
            print("❌ No content fetched from URL")
        elif len(headings) == 0 and len(meaningful_p) == 0:
            print("❌ No meaningful content found in HTML")
            print("   This could be a JavaScript-heavy site")
        else:
            print("✅ Content extraction should work")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_extraction(sys.argv[1])
    else:
        print("Usage: python test_extraction.py <URL>")
        print("Example: python test_extraction.py https://example.com")
