#!/usr/bin/env python3
"""
Quick test for the 4 failing links
Tests only the problematic links to verify our fixes
"""

import asyncio
from onlyfans_detector_hybrid_final import detect_onlyfans_in_bio_link

async def quick_test_4_links():
    """Quick test of the 4 previously failing links"""
    
    failing_links = [
        "https://www.thesummerstarz.com",
        "https://link.me/kaylasummers", 
        "https://beacons.ai/robertaruiva",
        "https://xli.ink/michellevnn"
    ]
    
    print("⚡ QUICK TEST - 4 FAILING LINKS")
    print("=" * 50)
    print("Testing our fixes for the problematic links...")
    print()
    
    results = []
    
    for i, link in enumerate(failing_links, 1):
        print(f"🔍 [{i}/4] Testing: {link}")
        print("-" * 40)
        
        try:
            start_time = asyncio.get_event_loop().time()
            result = await detect_onlyfans_in_bio_link(link)
            end_time = asyncio.get_event_loop().time()
            
            duration = round(end_time - start_time, 2)
            
            if result["has_onlyfans"]:
                print(f"✅ SUCCESS! Found {len(result['onlyfans_urls'])} OnlyFans links")
                print(f"   URLs: {result['onlyfans_urls']}")
                print(f"   Method: {result['detection_method']}")
                print(f"   Time: {duration}s")
            else:
                print(f"❌ STILL FAILING")
                print(f"   Method: {result['detection_method']}")
                print(f"   Time: {duration}s")
                if result['errors']:
                    print(f"   Errors: {result['errors']}")
            
            if result['debug_info']:
                print(f"   Debug: {' → '.join(result['debug_info'])}")
                
            results.append({
                'link': link,
                'success': result["has_onlyfans"],
                'method': result['detection_method'],
                'duration': duration,
                'urls': result['onlyfans_urls']
            })
            
        except Exception as e:
            print(f"❌ TEST FAILED: {str(e)}")
            results.append({
                'link': link,
                'success': False,
                'method': 'error',
                'duration': 0,
                'urls': []
            })
        
        print()
    
    # Summary
    print("📊 QUICK TEST RESULTS")
    print("=" * 50)
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"✅ Fixed: {successful}/{total} ({successful/total*100:.1f}%)")
    print()
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['link']}")
        if result['success']:
            print(f"   Method: {result['method']}")
            print(f"   URLs: {result['urls']}")
            print(f"   Time: {result['duration']}s")
        print()
    
    if successful == total:
        print("🎉🎉🎉 ALL 4 LINKS FIXED! 🎉🎉🎉")
        print("Ready for deployment to Heroku!")
    elif successful >= 2:
        print(f"🚀 GOOD PROGRESS! {successful} out of {total} links fixed!")
        print("Significant improvement achieved!")
    else:
        print(f"😞 Only {successful} out of {total} links fixed.")
        print("Need to investigate further.")

if __name__ == "__main__":
    asyncio.run(quick_test_4_links())

