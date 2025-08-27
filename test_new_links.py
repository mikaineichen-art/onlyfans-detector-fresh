#!/usr/bin/env python3
"""
Test script for new 10 links
Tests our 100% working detector with fresh links
"""

import asyncio
from onlyfans_detector_hybrid_final import detect_onlyfans_in_bio_link

async def test_new_links():
    """Test the detector with the new 10 links"""
    
    new_test_links = [
        "https://taplink.cc/passionasian",
        "https://link.me/kaylasummers",
        "https://www.itsalexia.com",
        "https://allmylinks.com/irltinax",
        "https://loverennxo.com",
        "https://beacons.ai/zoeneli",
        "https://luxe.bio/eva",
        "https://link.me/___kayla.lea___",
        "https://juicy.bio/aryaraee",
        "https://hoo.be/tayuhlynn"
    ]
    
    print("🧪 TESTING DETECTOR WITH NEW 10 LINKS")
    print("=" * 60)
    print("Testing our 100% working detector with fresh links...")
    print()
    
    results = []
    
    for i, link in enumerate(new_test_links, 1):
        print(f"🔍 [{i}/10] Testing: {link}")
        print("-" * 50)
        
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
                print(f"❌ FAILED")
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
    print("📊 NEW LINKS TEST RESULTS")
    print("=" * 60)
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total} ({successful/total*100:.1f}%)")
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
        print("🎉🎉🎉 PERFECT SCORE! ALL 10 NEW LINKS WORKING! 🎉🎉🎉")
        print("Our detector is truly 100% reliable!")
    elif successful >= 8:
        print(f"🚀 EXCELLENT! {successful} out of {total} new links working!")
        print("Our detector is very reliable!")
    elif successful >= 6:
        print(f"👍 GOOD! {successful} out of {total} new links working!")
        print("Solid performance!")
    else:
        print(f"😞 Only {successful} out of {total} new links working.")
        print("Need to investigate further.")

if __name__ == "__main__":
    asyncio.run(test_new_links())

