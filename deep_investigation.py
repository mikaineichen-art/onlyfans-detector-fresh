#!/usr/bin/env python3
"""
Deep investigation script for remaining failing links
Analyzes the 3 links that are still not working
"""

import asyncio
import httpx
import re
import json
from urllib.parse import urljoin

async def deep_investigation():
    """Deep investigation of remaining failing links"""
    
    failing_links = [
        "https://link.me/kaylasummers",
        "https://beacons.ai/robertaruiva", 
        "https://xli.ink/michellevnn"
    ]
    
    print("🔬 DEEP INVESTIGATION OF REMAINING FAILING LINKS")
    print("=" * 70)
    
    for i, link in enumerate(failing_links, 1):
        print(f"\n🔬 [{i}/3] Deep Investigation: {link}")
        print("=" * 60)
        
        await investigate_deep(link)
        print()

async def investigate_deep(link: str):
    """Deep investigation of a single link"""
    
    # Test 1: Raw HTML analysis
    print("📄 Test 1: Raw HTML Analysis")
    await analyze_raw_html(link)
    
    # Test 2: JavaScript extraction
    print("\n⚡ Test 2: JavaScript Extraction")
    await extract_javascript_content(link)
    
    # Test 3: Network analysis
    print("\n🌐 Test 3: Network Analysis")
    await analyze_network_requests(link)
    
    # Test 4: Content inspection
    print("\n🔍 Test 4: Content Inspection")
    await inspect_content_details(link)

async def analyze_raw_html(link: str):
    """Analyze raw HTML for hidden content"""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(link)
            
            if response.status_code == 200:
                content = response.text
                
                # Look for OnlyFans mentions in raw HTML
                of_mentions = re.findall(r'onlyfans', content, re.IGNORECASE)
                print(f"   OnlyFans mentions found: {len(of_mentions)}")
                
                if of_mentions:
                    # Show context around each mention
                    for i, mention in enumerate(of_mentions[:5]):
                        start = max(0, content.lower().find(mention) - 100)
                        end = min(len(content), content.lower().find(mention) + 100)
                        context = content[start:end].replace('\n', ' ').strip()
                        print(f"      Context {i+1}: ...{context}...")
                
                # Look for hidden input fields
                hidden_inputs = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*value=["\']([^"\']+)["\'][^>]*>', content)
                if hidden_inputs:
                    print(f"   Hidden inputs found: {len(hidden_inputs)}")
                    for inp in hidden_inputs[:3]:
                        if 'onlyfans' in inp.lower():
                            print(f"      OnlyFans in hidden input: {inp}")
                
                # Look for data attributes
                data_attrs = re.findall(r'data-[^=]+=["\']([^"\']+)["\']', content)
                if data_attrs:
                    print(f"   Data attributes found: {len(data_attrs)}")
                    for attr in data_attrs[:5]:
                        if 'onlyfans' in attr.lower():
                            print(f"      OnlyFans in data attr: {attr}")
                
                # Look for script tags
                script_tags = re.findall(r'<script[^>]*>([^<]*)</script>', content, re.IGNORECASE)
                if script_tags:
                    print(f"   Script tags found: {len(script_tags)}")
                    for script in script_tags[:3]:
                        if 'onlyfans' in script.lower():
                            print(f"      OnlyFans in script: {script[:200]}...")
                            
            else:
                print(f"   ❌ Status {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Raw HTML analysis failed: {str(e)}")

async def extract_javascript_content(link: str):
    """Extract and analyze JavaScript content"""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(link)
            
            if response.status_code == 200:
                content = response.text
                
                # Extract all JavaScript content
                js_patterns = [
                    r'<script[^>]*>([^<]*)</script>',
                    r'window\.__INITIAL_STATE__\s*=\s*({[^}]+})',
                    r'window\.__PRELOADED_STATE__\s*=\s*({[^}]+})',
                    r'data-props\s*=\s*["\']([^"\']+)["\']',
                    r'data-state\s*=\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in js_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        print(f"   Pattern {pattern[:30]}...: {len(matches)} matches")
                        
                        for match in matches[:2]:
                            if 'onlyfans' in match.lower():
                                print(f"      OnlyFans found: {match[:100]}...")
                                
                                # Try to extract URLs
                                urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', match, re.IGNORECASE)
                                if urls:
                                    print(f"      URLs extracted: {urls}")
                
                # Look for JSON-like structures
                json_patterns = [
                    r'\{[^{}]*"onlyfans"[^{}]*\}',
                    r'\[[^\[\]]*"onlyfans"[^\[\]]*\]'
                ]
                
                for pattern in json_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        print(f"   JSON-like structure found: {len(matches)}")
                        for match in matches[:2]:
                            print(f"      Structure: {match[:100]}...")
                            
    except Exception as e:
        print(f"   ❌ JavaScript extraction failed: {str(e)}")

async def analyze_network_requests(link: str):
    """Analyze network requests and responses"""
    try:
        # Test different request methods
        async with httpx.AsyncClient(timeout=20.0) as client:
            
            # Test HEAD request
            try:
                head_response = await client.head(link)
                print(f"   HEAD Status: {head_response.status_code}")
                print(f"   HEAD Headers: {dict(head_response.headers)}")
            except Exception as e:
                print(f"   HEAD failed: {str(e)}")
            
            # Test with different Accept headers
            accept_headers = [
                'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'application/json',
                'text/plain',
                '*/*'
            ]
            
            for accept in accept_headers:
                try:
                    headers = {'Accept': accept}
                    response = await client.get(link, headers=headers)
                    print(f"   Accept {accept[:30]}...: Status {response.status_code}")
                    
                    if response.status_code == 200:
                        content = response.text.lower()
                        if 'onlyfans' in content:
                            print(f"      ✅ OnlyFans found with Accept: {accept}")
                            
                except Exception as e:
                    continue
                    
    except Exception as e:
        print(f"   ❌ Network analysis failed: {str(e)}")

async def inspect_content_details(link: str):
    """Inspect content details and structure"""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(link)
            
            if response.status_code == 200:
                content = response.text
                
                # Analyze page structure
                print(f"   Content length: {len(content)} characters")
                print(f"   HTML tags: {len(re.findall(r'<[^>]+>', content))}")
                print(f"   Links: {len(re.findall(r'href=["\']([^"\']+)["\']', content))}")
                print(f"   Images: {len(re.findall(r'<img[^>]+>', content))}")
                print(f"   Scripts: {len(re.findall(r'<script[^>]*>', content))}")
                print(f"   Styles: {len(re.findall(r'<style[^>]*>', content))}")
                
                # Look for specific patterns
                patterns = [
                    (r'instagram', 'Instagram'),
                    (r'twitter', 'Twitter'),
                    (r'tiktok', 'TikTok'),
                    (r'youtube', 'YouTube'),
                    (r'snapchat', 'Snapchat'),
                    (r'telegram', 'Telegram'),
                    (r'discord', 'Discord'),
                    (r'patreon', 'Patreon'),
                    (r'fansly', 'Fansly')
                ]
                
                found_platforms = []
                for pattern, name in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        found_platforms.append(name)
                
                if found_platforms:
                    print(f"   Social platforms found: {', '.join(found_platforms)}")
                
                # Look for OnlyFans in different contexts
                of_contexts = [
                    (r'<a[^>]*href=["\']([^"\']*onlyfans[^"\']*)["\'][^>]*>([^<]*)</a>', 'Link text'),
                    (r'<img[^>]*alt=["\']([^"\']*onlyfans[^"\']*)["\'][^>]*>', 'Image alt'),
                    (r'<div[^>]*>([^<]*onlyfans[^<]*)</div>', 'Div content'),
                    (r'<span[^>]*>([^<]*onlyfans[^<]*)</span>', 'Span content')
                ]
                
                for pattern, context_type in of_contexts:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        print(f"   {context_type} with OnlyFans: {len(matches)} found")
                        for match in matches[:2]:
                            if isinstance(match, tuple):
                                match = match[0]
                            print(f"      {match[:100]}...")
                            
            else:
                print(f"   ❌ Cannot inspect content - status {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Content inspection failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(deep_investigation())
