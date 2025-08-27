#!/usr/bin/env python3
"""
Local test script for OnlyFans Detector
Run this to test the detector locally before deployment
"""

import asyncio
import json
from onlyfans_detector_hybrid_final import detect_onlyfans_in_bio_link

async def test_detector():
    """Test the detector with a known working link"""
    
    # Test with a simple link that should work
    test_links = [
        "https://taplink.cc/passionasian",  # This one worked in your test
        "https://www.itsalexia.com",        # This one also worked
        "https://allmylinks.com/irltinax"   # This one worked too
    ]
    
    print("🧪 Testing OnlyFans Detector locally...")
    print("=" * 50)
    
    for i, link in enumerate(test_links, 1):
        print(f"\n🔍 Test {i}: {link}")
        print("-" * 30)
        
        try:
            result = await detect_onlyfans_in_bio_link(link)
            
            print(f"✅ Success: {result['has_onlyfans']}")
            print(f"🔗 URLs: {result['onlyfans_urls']}")
            print(f"📋 Method: {result['detection_method']}")
            
            if result['debug_info']:
                print(f"📝 Debug: {result['debug_info'][:3]}...")  # Show first 3 debug items
                
            if result['errors']:
                print(f"⚠️  Errors: {result['errors']}")
                
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Local testing completed!")

if __name__ == "__main__":
    asyncio.run(test_detector())
