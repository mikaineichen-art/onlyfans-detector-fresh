#!/usr/bin/env python3
"""
Investigation script for failing OnlyFans detection
Analyzes why 4 specific links are not being detected
"""

import asyncio
import httpx
import re
from urllib.parse import urljoin

# OnlyFans detection regex
OF_REGEX = re.compile(r"onlyfans\.com", re.IGNORECASE)

async def investigate_failing_links():
    """Investigate why the 4 failing links are not being detected"""
    
    failing_links = [
        "https://www.thesummerstarz.com",
        "https://link.me/kaylasummers", 
        "https://beacons.ai/robertaruiva",
        "https://xli.ink/michellevnn"
    ]
    
    print("🔍 INVESTIGATING FAILING ONLYFANS DETECTION")
    print("=" * 70)
    
    for i, link in enumerate(failing_links, 1):
        print(f"\n🔍 [{i}/4] Investigating: {link}")
        print("-" * 50)
        
        await investigate_single_link(link)
        
        print()

async def investigate_single_link(link: str):
    """Investigate a single failing link"""
    
    try:
        # Test 1: Basic HTTP response
        print("📡 Test 1: Basic HTTP Response")
        await test_basic_http(link)
        
        # Test 2: Different user agents
        print("\n🌐 Test 2: Different User Agents")
        await test_user_agents(link)
        
        # Test 3: Redirect analysis
        print("\n🔄 Test 3: Redirect Analysis")
        await test_redirects(link)
        
        # Test 4: Content analysis
        print("\n📄 Test 4: Content Analysis")
        await analyze_content(link)
        
        # Test 5: Alternative paths
        print("\n🛤️  Test 5: Alternative Paths")
        await test_alternative_paths(link)
        
    except Exception as e:
        print(f"❌ Investigation failed: {str(e)}")

async def test_basic_http(link: str):
    """Test basic HTTP response"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(link)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"   Content-Length: {len(response.text)} characters")
            
            if response.status_code != 200:
                print(f"   ⚠️  Non-200 status - this might be the issue!")
                
    except Exception as e:
        print(f"   ❌ HTTP test failed: {str(e)}")

async def test_user_agents(link: str):
    """Test different user agents"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15',
        'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    ]
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            for i, user_agent in enumerate(user_agents, 1):
                try:
                    headers = {'User-Agent': user_agent}
                    response = await client.get(link, headers=headers)
                    print(f"   UA {i}: Status {response.status_code}")
                    
                    if response.status_code == 200:
                        content = response.text.lower()
                        of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', content, re.IGNORECASE)
                        if of_urls:
                            print(f"   ✅ Found {len(of_urls)} OnlyFans URLs with UA {i}!")
                        else:
                            print(f"   ❌ No OnlyFans URLs found with UA {i}")
                            
                except Exception as e:
                    print(f"   ❌ UA {i} failed: {str(e)}")
                    
    except Exception as e:
        print(f"   ❌ User agent test failed: {str(e)}")

async def test_redirects(link: str):
    """Test redirect handling"""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=False) as client:
            # Test HEAD request
            head_response = await client.head(link)
            print(f"   HEAD Status: {head_response.status_code}")
            
            if head_response.status_code in (301, 302, 303, 307, 308):
                location = head_response.headers.get('location')
                print(f"   🔄 Redirect Location: {location}")
                
                if location:
                    # Follow the redirect
                    if location.startswith('/'):
                        redirect_url = urljoin(link, location)
                    else:
                        redirect_url = location
                    
                    print(f"   🔄 Following redirect to: {redirect_url}")
                    
                    try:
                        redirect_response = await client.get(redirect_url)
                        print(f"   🔄 Redirect Status: {redirect_response.status_code}")
                        
                        if redirect_response.status_code == 200:
                            content = redirect_response.text.lower()
                            of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', content, re.IGNORECASE)
                            if of_urls:
                                print(f"   ✅ Found {len(of_urls)} OnlyFans URLs after redirect!")
                            else:
                                print(f"   ❌ No OnlyFans URLs found after redirect")
                                
                    except Exception as e:
                        print(f"   ❌ Redirect follow failed: {str(e)}")
            else:
                print(f"   ✅ No redirects detected")
                
    except Exception as e:
        print(f"   ❌ Redirect test failed: {str(e)}")

async def analyze_content(link: str):
    """Analyze page content for clues"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(link)
            
            if response.status_code == 200:
                content = response.text
                
                # Look for common patterns
                print(f"   📄 Page title: {extract_title(content)}")
                print(f"   🔗 Total links found: {len(re.findall(r'href=["\']([^"\']+)["\']', content))}")
                print(f"   🖼️  Images found: {len(re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content))}")
                print(f"   📱 Meta viewport: {'Yes' if 'viewport' in content.lower() else 'No'}")
                
                # Look for OnlyFans mentions
                of_mentions = re.findall(r'onlyfans', content, re.IGNORECASE)
                if of_mentions:
                    print(f"   🎯 OnlyFans mentions found: {len(of_mentions)}")
                    # Show context around mentions
                    for i, mention in enumerate(of_mentions[:3]):
                        start = max(0, content.lower().find(mention) - 50)
                        end = min(len(content), content.lower().find(mention) + 50)
                        context = content[start:end].replace('\n', ' ').strip()
                        print(f"      Context {i+1}: ...{context}...")
                else:
                    print(f"   ❌ No OnlyFans mentions found in content")
                
                # Look for social media patterns
                social_patterns = ['instagram', 'twitter', 'tiktok', 'youtube', 'snapchat']
                found_social = []
                for pattern in social_patterns:
                    if pattern in content.lower():
                        found_social.append(pattern)
                
                if found_social:
                    print(f"   📱 Social media found: {', '.join(found_social)}")
                else:
                    print(f"   ❌ No social media patterns found")
                    
            else:
                print(f"   ❌ Cannot analyze content - status {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Content analysis failed: {str(e)}")

async def test_alternative_paths(link: str):
    """Test alternative paths"""
    common_paths = [
        '/links', '/social', '/socials', '/connect', '/bio', '/profile', 
        '/about', '/contact', '/links.html', '/social.html', '/index.html'
    ]
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for path in common_paths:
                try:
                    test_url = urljoin(link, path)
                    response = await client.get(test_url)
                    
                    if response.status_code == 200:
                        print(f"   ✅ {path}: Status {response.status_code}")
                        content = response.text.lower()
                        of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', content, re.IGNORECASE)
                        if of_urls:
                            print(f"      🎯 Found {len(of_urls)} OnlyFans URLs in {path}!")
                            return  # Found it!
                    else:
                        print(f"   ❌ {path}: Status {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {path}: Failed - {str(e)}")
                    
    except Exception as e:
        print(f"   ❌ Alternative paths test failed: {str(e)}")

def extract_title(content: str) -> str:
    """Extract page title from HTML"""
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
    if title_match:
        return title_match.group(1).strip()
    return "No title found"

if __name__ == "__main__":
    asyncio.run(investigate_failing_links())
