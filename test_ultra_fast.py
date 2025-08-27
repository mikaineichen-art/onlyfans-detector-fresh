#!/usr/bin/env python3
"""
Ultra-Fast Batch OnlyFans Detection Test
All links processed simultaneously with 10-second timeouts
"""

import asyncio
import httpx
import re
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import time

# OnlyFans detection regex
OF_REGEX = re.compile(r"onlyfans\.com", re.IGNORECASE)

async def test_single_link_fast(link: str, timeout: int = 10) -> tuple:
    """Test a single link with strict timeout"""
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Try with desktop user agent first
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = await client.get(link, headers=headers)
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Look for OnlyFans URLs
                of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', content, re.IGNORECASE)
                valid_urls = [url for url in of_urls if '/files' not in url and '/public' not in url]
                
                if valid_urls:
                    elapsed = time.time() - start_time
                    return ("✅", link, len(valid_urls), elapsed, "direct_html_scan")
                
                # Quick redirect check (limited for speed)
                all_links = re.findall(r'href=["\']([^"\']+)["\']', content)
                all_links.extend(re.findall(r'data-url=["\']([^"\']+)["\']', content))
                
                for test_link in all_links[:5]:  # Check first 5 links only
                    if not test_link or test_link.startswith('#') or test_link.startswith('mailto:'):
                        continue
                    
                    try:
                        if test_link.startswith('/'):
                            test_link = urljoin(link, test_link)
                        
                        # Quick redirect check
                        final_url = await follow_redirects_ultra_fast(client, test_link)
                        
                        if OF_REGEX.search(final_url) and '/files' not in final_url and '/public' not in final_url:
                            elapsed = time.time() - start_time
                            return ("✅", link, 1, elapsed, "redirect_chain")
                            
                    except Exception:
                        continue
                
                elapsed = time.time() - start_time
                return ("❌", link, 0, elapsed, "no_onlyfans_found")
                
            else:
                elapsed = time.time() - start_time
                return ("❌", link, 0, elapsed, f"http_{response.status_code}")
                
    except Exception as e:
        elapsed = time.time() - start_time
        return ("❌", link, 0, elapsed, f"error: {str(e)[:50]}")

async def follow_redirects_ultra_fast(client: httpx.AsyncClient, url: str, max_redirects: int = 3) -> str:
    """Ultra-fast redirect following"""
    current = url
    
    for _ in range(max_redirects):
        try:
            resp = await client.head(current, follow_redirects=False, timeout=3.0)
            if resp.status_code in (301, 302, 303, 307, 308):
                location = resp.headers.get('location')
                if location:
                    if location.startswith('/'):
                        current = urljoin(current, location)
                    else:
                        current = location
                else:
                    break
            else:
                break
        except Exception:
            break
    
    return current

async def test_all_links_ultra_fast():
    """Test all 10 links simultaneously with strict timeouts"""
    
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
    
    print("⚡ ULTRA-FAST OnlyFans Detection Test")
    print("=" * 60)
    print("🚀 Testing all 10 links simultaneously with 10-second timeouts")
    print("=" * 60)
    
    start_total = time.time()
    
    # Test all links simultaneously
    tasks = [test_single_link_fast(link, timeout=10) for link in test_links]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append(("❌", test_links[i], 0, 10.0, f"exception: {str(result)[:50]}"))
        else:
            processed_results.append(result)
    
    # Display results
    print("\n📊 INDIVIDUAL RESULTS:")
    print("-" * 60)
    
    for i, (status, link, count, elapsed, method) in enumerate(processed_results, 1):
        print(f"[{i:2d}] {status} {link}")
        print(f"     Time: {elapsed:.2f}s | Method: {method}")
        if count > 0:
            print(f"     Found: {count} OnlyFans URL(s)")
        print()
    
    # Summary
    total_time = time.time() - start_total
    found_count = sum(1 for result in processed_results if result[0] == "✅")
    total_count = len(processed_results)
    
    print("=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    
    for status, link, count, elapsed, method in processed_results:
        print(f"{status} {link}")
    
    print(f"\n🎯 SUCCESS RATE: {found_count}/{total_count} ({found_count/total_count*100:.1f}%)")
    print(f"⏱️  TOTAL TIME: {total_time:.2f} seconds")
    print(f"⚡ AVERAGE TIME PER LINK: {total_time/total_count:.2f} seconds")
    
    if found_count >= 8:
        print("🎉 EXCELLENT! Ready for deployment!")
    elif found_count >= 6:
        print("👍 GOOD! Some improvements needed before deployment")
    else:
        print("⚠️  NEEDS WORK! Don't deploy yet!")

if __name__ == "__main__":
    asyncio.run(test_all_links_ultra_fast())

