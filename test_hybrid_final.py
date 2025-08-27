#!/usr/bin/env python3
"""
Test script for the final hybrid detector
Tests all 10 links to see the final results
"""

import asyncio
from onlyfans_detector_hybrid_final import detect_onlyfans_in_bio_link

async def test_hybrid_final():
    """Test the final hybrid detector with all 10 links"""
    
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
    
    print("🧪 TESTING FINAL HYBRID DETECTOR")
    print("=" * 60)
    print("This detector combines:")
    print("  • Phase 1: Fast HTTP detection (1-2s)")
    print("  • Phase 2: Enhanced HTTP strategies (3-5s)")
    print("  • Phase 3: Interactive Playwright detection (10-15s)")
    print()
    
    results = []
    
    for i, link in enumerate(test_links, 1):
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
    print("📊 FINAL RESULTS")
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
        print("🎉🎉🎉 PERFECT SCORE! ALL 10 LINKS WORKING! 🎉🎉🎉")
        print("The final hybrid detector is a complete success!")
    elif successful >= 8:
        print(f"🚀 EXCELLENT! {successful} out of {total} links working!")
        print("The hybrid approach is very effective!")
    elif successful >= 6:
        print(f"👍 GOOD! {successful} out of {total} links working!")
        print("Significant improvement achieved!")
    else:
        print(f"😞 Only {successful} out of {total} links working.")
        print("Need to investigate further.")

if __name__ == "__main__":
    asyncio.run(test_hybrid_final())
