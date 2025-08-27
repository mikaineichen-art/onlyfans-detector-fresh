#!/usr/bin/env python3
"""
Test script for the Enhanced OnlyFans Detector
Tests all 10 links with the enhanced detection logic
"""

import asyncio
import json
from onlyfans_detector_enhanced import detect_onlyfans_in_bio_link

async def test_enhanced_detector():
    """Test the enhanced detector with all 10 links"""
    
    # Test links provided by the user
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
    
    print("🚀 Testing Enhanced OnlyFans Detector (100% Detection Target)")
    print("=" * 70)
    
    results = []
    
    for i, link in enumerate(test_links, 1):
        print(f"\n🔍 [{i}/10] Testing: {link}")
        print("-" * 50)
        
        try:
            result = await detect_onlyfans_in_bio_link(link)
            
            print(f"✅ Success: {result['has_onlyfans']}")
            print(f"📊 Phase used: {result['phase_used']}")
            print(f"🔗 Method: {result['detection_method']}")
            
            if result['onlyfans_urls']:
                print(f"🎯 OnlyFans URLs found: {len(result['onlyfans_urls'])}")
                print(f"   • {result['onlyfans_urls'][0]}")
                results.append(("✅", link, len(result['onlyfans_urls'])))
            else:
                print("❌ No OnlyFans found")
                results.append(("❌", link, 0))
            
            if result['debug_info']:
                print(f"📝 Debug info:")
                for info in result['debug_info']:
                    print(f"   • {info}")
            
            if result['errors']:
                print(f"❌ Errors:")
                for error in result['errors']:
                    print(f"   • {error}")
                    
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results.append(("❌", link, 0))
        
        print()
    
    # Summary
    print("=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)
    
    found_count = sum(1 for result in results if result[0] == "✅")
    total_count = len(results)
    
    for status, link, count in results:
        print(f"{status} {link}")
    
    print(f"\n🎯 SUCCESS RATE: {found_count}/{total_count} ({found_count/total_count*100:.1f}%)")
    
    if found_count >= 9:
        print("🎉 EXCELLENT! Nearly 100% detection achieved!")
    elif found_count >= 8:
        print("🎉 EXCELLENT! Ready for deployment!")
    elif found_count >= 7:
        print("👍 VERY GOOD! Significant improvement achieved!")
    elif found_count >= 6:
        print("👍 GOOD! Some improvements needed before deployment")
    else:
        print("⚠️  NEEDS WORK! Don't deploy yet!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_detector())
