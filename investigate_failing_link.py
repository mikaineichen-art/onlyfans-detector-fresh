#!/usr/bin/env python3
"""
Special Investigation Script for Failing Link
Let's see what's happening with link.me/___kayla.lea___
"""

import asyncio
import httpx
import re
from urllib.parse import urljoin, urlparse

async def investigate_link(bio_link: str):
    """Deep investigation of a failing link"""
    print(f"🔍 Investigating: {bio_link}")
    print("=" * 60)
    
    # Test 1: Basic HTTP request
    print("\n📡 Test 1: Basic HTTP Request")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(bio_link)
            print(f"Status: {response.status_code}")
            print(f"Content Length: {len(response.text)}")
            
            # Look for OnlyFans mentions
            content_lower = response.text.lower()
            if 'onlyfans' in content_lower:
                print("✅ OnlyFans mentioned in basic content")
                # Find the specific text around OnlyFans
                start = max(0, content_lower.find('onlyfans') - 100)
                end = min(len(response.text), content_lower.find('onlyfans') + 100)
                print(f"Context: {response.text[start:end]}")
            else:
                print("❌ No OnlyFans mention in basic content")
                
    except Exception as e:
        print(f"❌ Basic HTTP failed: {e}")
    
    # Test 2: Different User-Agents
    print("\n🤖 Test 2: Different User-Agents")
    user_agents = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    for i, ua in enumerate(user_agents, 1):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"User-Agent": ua}
                response = await client.get(bio_link, headers=headers)
                print(f"UA {i}: Status {response.status_code}")
                
                content_lower = response.text.lower()
                if 'onlyfans' in content_lower:
                    print(f"✅ OnlyFans found with UA {i}")
                    # Extract OnlyFans URLs
                    of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', response.text, re.IGNORECASE)
                    if of_urls:
                        print(f"OnlyFans URLs: {of_urls}")
                    break
                else:
                    print(f"❌ No OnlyFans with UA {i}")
                    
        except Exception as e:
            print(f"❌ UA {i} failed: {e}")
    
    # Test 3: Check for redirects
    print("\n🔄 Test 3: Check for Redirects")
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
            response = await client.get(bio_link)
            if response.status_code in (301, 302, 303, 307, 308):
                location = response.headers.get('location')
                print(f"Redirect found: {location}")
                
                # Follow the redirect
                if location:
                    if location.startswith('/'):
                        redirect_url = urljoin(bio_link, location)
                    else:
                        redirect_url = location
                    
                    print(f"Following redirect to: {redirect_url}")
                    redirect_response = await client.get(redirect_url)
                    redirect_content = redirect_response.text.lower()
                    
                    if 'onlyfans' in redirect_content:
                        print("✅ OnlyFans found after redirect!")
                        of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', redirect_response.text, re.IGNORECASE)
                        if of_urls:
                            print(f"OnlyFans URLs: {of_urls}")
                    else:
                        print("❌ No OnlyFans after redirect")
            else:
                print("No redirects found")
                
    except Exception as e:
        print(f"❌ Redirect check failed: {e}")
    
    # Test 4: Look for hidden content
    print("\n🔍 Test 4: Look for Hidden Content")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(bio_link)
            content = response.text
            
            # Look for JavaScript variables
            js_patterns = [
                r'var\s+\w+\s*=\s*["\']([^"\']*onlyfans[^"\']*)["\']',
                r'const\s+\w+\s*=\s*["\']([^"\']*onlyfans[^"\']*)["\']',
                r'let\s+\w+\s*=\s*["\']([^"\']*onlyfans[^"\']*)["\']',
                r'["\']([^"\']*onlyfans[^"\']*)["\']'
            ]
            
            for pattern in js_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    print(f"✅ Found in JavaScript: {matches}")
            
            # Look for data attributes
            data_patterns = [
                r'data-[^=]*=["\']([^"\']*onlyfans[^"\']*)["\']',
                r'href=["\']([^"\']*onlyfans[^"\']*)["\']',
                r'src=["\']([^"\']*onlyfans[^"\']*)["\']'
            ]
            
            for pattern in data_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    print(f"✅ Found in data attributes: {matches}")
                    
    except Exception as e:
        print(f"❌ Hidden content check failed: {e}")
    
    print("\n" + "=" * 60)
    print("🔍 Investigation Complete!")

if __name__ == "__main__":
    # Test the failing link
    failing_link = "https://link.me/___kayla.lea___"
    asyncio.run(investigate_link(failing_link))
