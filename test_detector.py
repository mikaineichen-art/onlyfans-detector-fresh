#!/usr/bin/env python3
"""
Test script for the OnlyFans detector
Run this locally to test before deploying to Heroku
"""

import asyncio
import json
from onlyfans_detector_robust import detect_onlyfans_in_bio_link

async def test_detector():
    """Test the detector with known links"""
    
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
    
    print("🧪 Testing OnlyFans Detector Locally")
    print("=" * 50)
    
    for i, link in enumerate(test_links, 1):
        print(f"\n🔍 Test {i}: {link}")
        print("-" * 30)
        
        try:
            result = await detect_onlyfans_in_bio_link(link)
            
            print(f"✅ Success: {result['has_onlyfans']}")
            print(f"📊 Phase used: {result['phase_used']}")
            print(f"🔗 Method: {result['detection_method']}")
            
            if result['onlyfans_urls']:
                print(f"🎯 OnlyFans URLs found: {len(result['onlyfans_urls'])}")
                print(f"   • {result['onlyfans_urls'][0]}")
            
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
        
        print()
    
    print("=" * 50)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    asyncio.run(test_detector())
