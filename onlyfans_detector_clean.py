#!/usr/bin/env python3
"""
Clean OnlyFans Detector - Railway Compatible
Simplified version without complex Playwright setup
"""

import re
import asyncio
import httpx
import os
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Tuple
import time
import sys
import json

# Try to import Playwright, but don't fail if not available
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
    print("✅ Playwright available")
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright not available - will use HTTP-only mode")

class CleanDetector:
    """Clean detector with HTTP + optional interactive detection"""
    
    def __init__(self):
        self.results = {
            "has_onlyfans": False,
            "onlyfans_urls": [],
            "detection_method": None,
            "debug_info": [],
            "errors": []
        }
        
    async def detect_onlyfans(self, bio_link: str) -> Dict:
        """Main detection method"""
        self.results = {
            "has_onlyfans": False,
            "onlyfans_urls": [],
            "detection_method": None,
            "debug_info": [],
            "errors": []
        }
        
        try:
            # Phase 1: Fast HTTP detection
            self.results["debug_info"].append("Phase 1: Fast HTTP detection")
            if await self._phase1_fast_detection(bio_link):
                self.results["detection_method"] = "Phase 1: Direct HTTP detection"
                return self.results

            # Phase 2: Enhanced HTTP detection
            self.results["debug_info"].append("Phase 2: Enhanced HTTP detection")
            if await self._phase2_enhanced_detection(bio_link):
                self.results["detection_method"] = "Phase 2: Enhanced HTTP strategies"
                return self.results

            # Phase 3: Interactive detection with Playwright (if available)
            if PLAYWRIGHT_AVAILABLE:
                self.results["debug_info"].append("Phase 3: Interactive detection with Playwright")
                if await self._phase3_interactive_detection(bio_link):
                    self.results["detection_method"] = "Phase 3: Interactive Playwright detection"
                    return self.results
            else:
                self.results["debug_info"].append("Phase 3: Skipped (Playwright not available)")

            # Phase 4: Special link.me fallback
            if "link.me" in bio_link.lower():
                self.results["debug_info"].append("Phase 4: Special link.me fallback detection")
                if await self._handle_linkme_fallback(bio_link):
                    self.results["detection_method"] = "Phase 4: Special link.me fallback"
                    return self.results

            # All phases completed - no OnlyFans found
            self.results["debug_info"].append("All phases completed - no OnlyFans found")
            
        except Exception as e:
            self.results["errors"].append(f"Detection failed: {str(e)}")
            
        return self.results

    async def _phase1_fast_detection(self, bio_link: str) -> bool:
        """Phase 1: Fast direct detection"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(bio_link)
                
                if response.status_code == 200:
                    content = response.text.lower()
                    of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', content, re.IGNORECASE)
                    
                    if of_urls:
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = list(set(of_urls))
                        return True
                        
        except Exception as e:
            self.results["errors"].append(f"Phase 1 failed: {str(e)}")
            
        return False

    async def _phase2_enhanced_detection(self, bio_link: str) -> bool:
        """Phase 2: Enhanced HTTP detection"""
        try:
            # Try different user agents
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1'
            ]
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                for user_agent in user_agents:
                    try:
                        headers = {'User-Agent': user_agent}
                        response = await client.get(bio_link, headers=headers)
                        
                        if response.status_code == 200:
                            content = response.text.lower()
                            of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', content, re.IGNORECASE)
                            
                            if of_urls:
                                self.results["has_onlyfans"] = True
                                self.results["onlyfans_urls"] = list(set(of_urls))
                                return True
                                
                    except Exception as e:
                        continue
                        
        except Exception as e:
            self.results["errors"].append(f"Phase 2 failed: {str(e)}")
            
        return False

    async def _phase3_interactive_detection(self, bio_link: str) -> bool:
        """Phase 3: Interactive detection with Playwright"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                
                context = await browser.new_context()
                page = await context.new_page()
                
                try:
                    await page.goto(bio_link, wait_until="domcontentloaded", timeout=15000)
                    await page.wait_for_timeout(3000)
                    
                    # Look for OnlyFans content
                    page_content = await page.content()
                    of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', page_content, re.IGNORECASE)
                    
                    if of_urls:
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = list(set(of_urls))
                        return True
                    
                    # Just check if OnlyFans is mentioned anywhere
                    if 'onlyfans' in page_content.lower():
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                        return True
                        
                finally:
                    await browser.close()
                    
        except Exception as e:
            self.results["errors"].append(f"Phase 3 failed: {str(e)}")
            
        return False

    async def _handle_linkme_fallback(self, bio_link: str) -> bool:
        """Special fallback detection for link.me"""
        try:
            self.results["debug_info"].append(f"=== DEBUGGING {bio_link} ===")
            
            async with httpx.AsyncClient(timeout=25.0) as client:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Referer': 'https://www.google.com/'
                }
                
                response = await client.get(bio_link, headers=headers)
                
                self.results["debug_info"].append(f"Response status: {response.status_code}")
                self.results["debug_info"].append(f"Response length: {len(response.text)}")
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Check for OnlyFans mentions
                    has_onlyfans_mention = 'onlyfans' in content.lower()
                    self.results["debug_info"].append(f"Contains 'onlyfans': {has_onlyfans_mention}")
                    
                    # Check for age verification indicators
                    age_verification_indicators = [
                        '18+', '18 plus', 'age verification', 'age gate', 'age check',
                        'confirm age', 'verify age', 'enter site', 'i\'m 18+', 'i am 18+',
                        'adult content', 'mature content', 'nsfw', 'explicit content',
                        'click to enter', 'proceed to site', 'continue to site'
                    ]
                    
                    age_verification_found = any(indicator.lower() in content.lower() for indicator in age_verification_indicators)
                    self.results["debug_info"].append(f"Age verification indicators found: {age_verification_found}")
                    
                    # Decision logic - if we find age verification, it's likely OnlyFans content
                    if age_verification_found:
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                        self.results["debug_info"].append("Early return due to age-gate signal")
                        return True
                    
                    if has_onlyfans_mention:
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                        self.results["debug_info"].append("OnlyFans found in link.me content")
                        return True
                
                self.results["debug_info"].append("=== END DEBUG ===")
                        
        except Exception as e:
            self.results["errors"].append(f"Link.me fallback detection failed: {str(e)}")
            
        return False

# Main function for n8n integration
async def detect_onlyfans_in_bio_link(bio_link: str) -> Dict:
    """Main function for n8n integration"""
    detector = CleanDetector()
    return await detector.detect_onlyfans(bio_link)

def main():
    """Command line interface"""
    import sys
    import json
    if len(sys.argv) != 2:
        print("Usage: python onlyfans_detector_clean.py <bio_link>")
        sys.exit(1)
        
    bio_link = sys.argv[1]
    
    async def run_detection():
        result = await detect_onlyfans_in_bio_link(bio_link)
        print(json.dumps(result, indent=2))
        
    asyncio.run(run_detection())

if __name__ == "__main__":
    main()
