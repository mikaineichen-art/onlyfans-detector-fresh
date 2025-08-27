#!/usr/bin/env python3
"""
Fast test script - HTTP only detection
Tests all 10 links quickly without Puppeteer
"""

import asyncio
import httpx
import re
from urllib.parse import urljoin

# OnlyFans detection regex
OF_REGEX = re.compile(r"onlyfans\.com", re.IGNORECASE)

async def test_http_detection():
    """Test HTTP-only detection on all 10 links"""
    
    test_links = [
        "https://linktr.ee/babesafreak",
        "https://midajahraeofficial.com", 
        "https://www.thesummerstarz.com",
        "https://allmylinks.com/bekkv",
        "https://allmylinks.com/shannafordphoto",
        "https://madicollinsofficial.com",
        "https://link.me/kaylasummers",
        "https://juicy.bio/missavanlife",
        "https://beacons.ai/robertaruiva",
        "https://xli.ink/michellevnn"
    ]
    
    print("🚀 Fast HTTP-Only OnlyFans Detection Test")
    print("=" * 60)
    
    results = []
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        for i, link in enumerate(test_links, 1):
            print(f"\n🔍 [{i}/10] Testing: {link}")
            print("-" * 40)
            
            try:
                # Get the page
                response = await client.get(link)
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Look for OnlyFans URLs
                    of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', content, re.IGNORECASE)
                    valid_urls = [url for url in of_urls if '/files' not in url and '/public' not in url]
                    
                    if valid_urls:
                        print(f"✅ FOUND OnlyFans! ({len(valid_urls)} URLs)")
                        print(f"   First URL: {valid_urls[0]}")
                        results.append(("✅", link, len(valid_urls)))
                    else:
                        print("❌ No OnlyFans found")
                        results.append(("❌", link, 0))
                        
                else:
                    print(f"❌ HTTP {response.status_code}")
                    results.append(("❌", link, 0))
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                results.append(("❌", link, 0))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    found_count = sum(1 for result in results if result[0] == "✅")
    total_count = len(results)
    
    for status, link, count in results:
        print(f"{status} {link}")
    
    print(f"\n🎯 SUCCESS RATE: {found_count}/{total_count} ({found_count/total_count*100:.1f}%)")
    
    if found_count >= 8:
        print("🎉 EXCELLENT! Ready for deployment!")
    elif found_count >= 6:
        print("👍 GOOD! Some improvements needed before deployment")
    else:
        print("⚠️  NEEDS WORK! Don't deploy yet!")

if __name__ == "__main__":
    asyncio.run(test_http_detection())

