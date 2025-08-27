#!/usr/bin/env python3
"""
Deep Investigation Script for Failing Link
Let's look deeper into what's happening with link.me/___kayla.lea___
"""

import asyncio
import httpx
import re
import json
from urllib.parse import urljoin, urlparse

async def deep_investigate_link(bio_link: str):
    """Deep investigation with JavaScript and dynamic content analysis"""
    print(f"🔍 Deep Investigating: {bio_link}")
    print("=" * 60)
    
    # Test 1: Get the full page content and analyze it
    print("\n📄 Test 1: Full Page Content Analysis")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(bio_link)
            content = response.text
            
            print(f"Page Title: {extract_title(content)}")
            print(f"Meta Description: {extract_meta_description(content)}")
            
            # Look for any social media links
            social_patterns = [
                r'https?://[^\s<>"\']*instagram\.com[^\s<>"\']*',
                r'https?://[^\s<>"\']*twitter\.com[^\s<>"\']*',
                r'https?://[^\s<>"\']*tiktok\.com[^\s<>"\']*',
                r'https?://[^\s<>"\']*youtube\.com[^\s<>"\']*',
                r'https?://[^\s<>"\']*snapchat\.com[^\s<>"\']*',
                r'https?://[^\s<>"\']*pinterest\.com[^\s<>"\']*'
            ]
            
            print("\n🔗 Social Media Links Found:")
            for pattern in social_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    print(f"✅ {pattern.split('.com')[0].split('/')[-1]}: {matches}")
            
            # Look for any external links
            external_links = re.findall(r'href=["\'](https?://[^"\']*)["\']', content)
            print(f"\n🌐 Total External Links: {len(external_links)}")
            
            # Look for linktree-like patterns
            linktree_patterns = [
                r'linktr\.ee/[^\s<>"\']*',
                r'allmylinks\.com/[^\s<>"\']*',
                r'beacons\.ai/[^\s<>"\']*',
                r'xli\.ink/[^\s<>"\']*'
            ]
            
            print("\n🔗 Link Aggregator Links:")
            for pattern in linktree_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    print(f"✅ {pattern.split('.')[0]}: {matches}")
                    
    except Exception as e:
        print(f"❌ Content analysis failed: {e}")
    
    # Test 2: Look for JavaScript content and data
    print("\n💻 Test 2: JavaScript and Data Analysis")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(bio_link)
            content = response.text
            
            # Look for JSON data in script tags
            script_patterns = [
                r'<script[^>]*>([^<]*)</script>',
                r'window\.__INITIAL_STATE__\s*=\s*({[^;]+})',
                r'window\.__DATA__\s*=\s*({[^;]+})',
                r'var\s+data\s*=\s*({[^;]+})',
                r'const\s+data\s*=\s*({[^;]+})'
            ]
            
            for pattern in script_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                if matches:
                    print(f"✅ Found script data: {len(matches)} matches")
                    for match in matches[:3]:  # Show first 3
                        if len(match) > 50:  # Only show substantial matches
                            print(f"   Preview: {match[:100]}...")
            
            # Look for data attributes
            data_attrs = re.findall(r'data-[^=]*=["\']([^"\']*)["\']', content)
            if data_attrs:
                print(f"✅ Found {len(data_attrs)} data attributes")
                # Look for OnlyFans in data attributes
                of_in_data = [attr for attr in data_attrs if 'onlyfans' in attr.lower()]
                if of_in_data:
                    print(f"   OnlyFans in data: {of_in_data}")
                    
    except Exception as e:
        print(f"❌ JavaScript analysis failed: {e}")
    
    # Test 3: Check if this is actually a false positive
    print("\n🤔 Test 3: False Positive Check")
    print("This link might not actually have OnlyFans!")
    print("Let's verify by checking what social links it DOES have...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(bio_link)
            content = response.text
            
            # Extract all URLs from the page
            all_urls = re.findall(r'https?://[^\s<>"\']*', content)
            
            print(f"\n🔗 All URLs found ({len(all_urls)} total):")
            for url in all_urls[:20]:  # Show first 20
                if any(domain in url.lower() for domain in ['instagram', 'twitter', 'tiktok', 'youtube', 'snapchat', 'pinterest', 'linktr', 'allmylinks', 'beacons', 'xli']):
                    print(f"   {url}")
                    
    except Exception as e:
        print(f"❌ URL extraction failed: {e}")
    
    print("\n" + "=" * 60)
    print("🔍 Deep Investigation Complete!")

def extract_title(content):
    """Extract page title"""
    title_match = re.search(r'<title[^>]*>([^<]*)</title>', content, re.IGNORECASE)
    return title_match.group(1) if title_match else "No title found"

def extract_meta_description(content):
    """Extract meta description"""
    desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', content, re.IGNORECASE)
    return desc_match.group(1) if desc_match else "No description found"

if __name__ == "__main__":
    # Test the failing link
    failing_link = "https://link.me/___kayla.lea___"
    asyncio.run(deep_investigate_link(failing_link))
