#!/usr/bin/env python3
"""
Final Hybrid OnlyFans Detector
Combines fast HTTP detection with interactive Playwright for complex cases
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
    
    # Railway-specific Playwright browser installation
    try:
        import subprocess
        import sys
        import platform
        
        print("🚀 Setting up Playwright for Railway...")
        
        # Step 1: Install browsers
        result = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                              capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ Playwright browsers installed successfully")
        elif self.results.get("age_verification_detected", False):
            print(f"⚠️  Browser installation failed: {result.stderr}")
            
            # Step 2: Try to install system dependencies
            try:
                result2 = subprocess.run([sys.executable, "-m", "playwright", "install-deps"], 
                                       capture_output=True, text=True, timeout=120)
                if result2.returncode == 0:
                    print("✅ System dependencies installed successfully")
                    # Try browser installation again
                    result3 = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                                           capture_output=True, text=True, timeout=120)
                    if result3.returncode == 0:
                        print("✅ Playwright browsers installed after dependencies")
                    elif self.results.get("age_verification_detected", False):
                        print(f"⚠️  Browser installation still failed: {result3.stderr}")
                elif self.results.get("age_verification_detected", False):
                    print(f"⚠️  Standard dependency installation failed: {result2.stderr}")
                    
                    # Step 3: Try alternative Linux package installation
                    if platform.system() == "Linux":
                        print("🐧 Linux detected, trying alternative package installation...")
                        apt_packages = [
                            "libglib2.0-0", "libnss3", "libnspr4", "libdbus-1-3",
                            "libatk1.0-0", "libatk-bridge2.0-0", "libcups2",
                            "libdrm2", "libxcb1", "libxkbcommon0", "libatspi2.0-0",
                            "libx11-6", "libxcomposite1", "libxdamage1", "libxext6",
                            "libxfixes3", "libxrandr2", "libgbm1", "libpango-1.0-0",
                            "libcairo2", "libasound2"
                        ]
                        
                        for package in apt_packages:
                            try:
                                result4 = subprocess.run(["apt-get", "install", "-y", package], 
                                                        capture_output=True, text=True, timeout=30)
                                if result4.returncode == 0:
                                    print(f"✅ Installed {package}")
                                elif self.results.get("age_verification_detected", False):
                                    print(f"⚠️  Failed to install {package}")
                            except Exception as e:
                                print(f"⚠️  Could not install {package}: {e}")
                        
                        # Try browser installation one more time
                        result5 = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                                               capture_output=True, text=True, timeout=120)
                        if result5.returncode == 0:
                            print("✅ Playwright browsers installed after alternative dependency installation")
                        elif self.results.get("age_verification_detected", False):
                            print(f"⚠️  Final browser installation attempt failed: {result5.stderr}")
                            
            except Exception as e:
                print(f"⚠️  Could not install Playwright dependencies: {e}")
                
    except Exception as e:
        print(f"⚠️  Could not install Playwright browsers: {e}")
        
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright not available - will use HTTP-only mode")

class HybridFinalDetector:
    """Final hybrid detector with HTTP + interactive detection"""
    
    def __init__(self):
        self.results = {
            "has_onlyfans": False,
            "onlyfans_urls": [],
            "detection_method": None,
            "debug_info": [],
            "errors": []
        }
        
    async def detect_onlyfans(self, bio_link: str) -> Dict:
        """Main detection method with hybrid approach"""
        self.results = {
            "has_onlyfans": False,
            "onlyfans_urls": [],
            "detection_method": None,
            "debug_info": [],
            "errors": []
        }
        
        try:
            # Phase 1: Fast direct detection
            self.results["debug_info"].append("Phase 1: Fast HTTP detection")
            if await self._phase1_fast_detection(bio_link):
                self.results["detection_method"] = "Phase 1: Direct HTTP detection"
                return self.results

            # Phase 2: Enhanced HTTP detection
            self.results["debug_info"].append("Phase 2: Enhanced HTTP detection")
            if await self._phase2_enhanced_detection(bio_link):
                self.results["detection_method"] = "Phase 2: Enhanced HTTP strategies"
                return self.results

            # Phase 3: Interactive detection with Playwright
            if PLAYWRIGHT_AVAILABLE:
                self.results["debug_info"].append("Phase 3: Interactive detection with Playwright")
                if await self._phase3_interactive_detection(bio_link):
                    self.results["detection_method"] = "Phase 3: Interactive Playwright detection"
                    return self.results
            elif self.results.get("age_verification_detected", False):
                self.results["debug_info"].append("Phase 3: Skipped (Playwright not available)")

            # Phase 3.5: Special link.me fallback (when Playwright fails)
            if "link.me" in bio_link.lower():
                self.results["debug_info"].append("Phase 3.5: Special link.me fallback detection")
                if await self._handle_linkme_fallback(bio_link):
                    self.results["detection_method"] = "Phase 3.5: Special link.me fallback"
                    return self.results

            # Phase 4: Final fallback extraction
            self.results["debug_info"].append("Phase 4: Final fallback extraction")
            if await self._final_fallback_extraction(bio_link):
                self.results["detection_method"] = "Phase 4: Final fallback extraction"
                return self.results

            # Phase 5: Desperate mode extraction
            self.results["debug_info"].append("Phase 5: Desperate mode extraction")
            if await self._desperate_mode_extraction(bio_link):
                self.results["detection_method"] = "Phase 5: Desperate mode extraction"
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
            # Strategy 1: Better redirect handling
            if await self._handle_redirects_better(bio_link):
                return True
                
            # Strategy 2: Try different user agents
            if await self._try_different_user_agents(bio_link):
                return True
                
            # Strategy 3: Enhanced link extraction
            if await self._enhanced_link_extraction(bio_link):
                return True
                
        except Exception as e:
            self.results["errors"].append(f"Phase 2 failed: {str(e)}")
            
        return False

    async def _phase3_interactive_detection(self, bio_link: str) -> bool:
        """Phase 3: Interactive detection with Playwright"""
        try:
            # Special handling for link.me (based on working solution)
            if "link.me" in bio_link.lower():
                return await self._handle_linkme_interactive(bio_link)
            
            # Special handling for beacons.ai
            elif "beacons.ai" in bio_link.lower():
                # Try the aggressive interactive approach first
                if await self._handle_beacons_interactive(bio_link):
                    return True
                
                # If that fails, try the alternative approach
                self.results["debug_info"].append("Interactive approach failed, trying alternative method...")
                if await self._handle_beacons_alternative(bio_link):
                    return True
                
                return False
            
            # Special handling for xli.ink
            elif "xli.ink" in bio_link.lower():
                return await self._handle_xli_interactive(bio_link)
            
            # Generic interactive detection
            elif self.results.get("age_verification_detected", False):
                return await self._generic_interactive_detection(bio_link)
            
        except Exception as e:
            self.results["errors"].append(f"Phase 3 failed: {str(e)}")
            
        return False

    async def _final_fallback_extraction(self, bio_link: str) -> bool:
        """Final fallback: Extract OnlyFans from any text content"""
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                # Try with different user agents and headers
                headers_list = [
                    {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    },
                    {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                ]
                
                for i, headers in enumerate(headers_list):
                    try:
                        response = await client.get(bio_link, headers=headers)
                        
                        if response.status_code == 200:
                            content = response.text
                            
                            # Look for ANY mention of OnlyFans
                            if 'onlyfans' in content.lower():
                                self.results["debug_info"].append(f"OnlyFans found in approach {i}, extracting...")
                                
                                # Strategy 1: Extract full URLs
                                of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', content, re.IGNORECASE)
                                if of_urls:
                                    self.results["has_onlyfans"] = True
                                    self.results["onlyfans_urls"] = list(set(of_urls))
                                    self.results["debug_info"].append("Found OnlyFans URLs in fallback extraction")
                                    return True
                                
                                # Strategy 2: Just confirm OnlyFans exists
                                self.results["has_onlyfans"] = True
                                self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                                self.results["debug_info"].append("OnlyFans confirmed to exist in content")
                                return True
                                
                    except Exception as e:
                        continue
                        
        except Exception as e:
            self.results["errors"].append(f"Final fallback extraction failed: {str(e)}")
            
        return False

    async def _launch_browser_safely(self, p):
        """Safely launch browser with fallback options"""
        try:
            # Try Railway-optimized launch first
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            self.results["debug_info"].append("Browser launched with Railway-optimized settings")
            return browser
        except Exception as e:
            self.results["debug_info"].append(f"Railway-optimized launch failed: {str(e)[:50]}...")
            try:
                # Fallback to basic launch
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                self.results["debug_info"].append("Browser launched with fallback settings")
                return browser
            except Exception as e2:
                self.results["debug_info"].append(f"Fallback launch also failed: {str(e2)[:50]}...")
                raise e2

    async def _desperate_mode_extraction(self, bio_link: str) -> bool:
        """Desperate mode: Try anything to find OnlyFans information"""
        try:
            self.results["debug_info"].append("Desperate mode: Trying aggressive extraction...")
            
            # Try with multiple different approaches
            approaches = [
                # Approach 1: Mobile user agent with different headers
                {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                # Approach 2: Desktop user agent with minimal headers
                {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.5'
                },
                # Approach 3: Bot-like user agent
                {
                    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
            ]
            
            async with httpx.AsyncClient(timeout=25.0) as client:
                for i, headers in enumerate(approaches, 1):
                    try:
                        self.results["debug_info"].append(f"Desperate approach {i}: {headers.get('User-Agent', 'Unknown')[:50]}...")
                        
                        response = await client.get(bio_link, headers=headers)
                        
                        if response.status_code == 200:
                            content = response.text
                            
                            # Look for ANY mention of OnlyFans
                            if 'onlyfans' in content.lower():
                                self.results["debug_info"].append(f"OnlyFans found in approach {i}, extracting...")
                                
                                # Strategy 1: Extract full URLs
                                of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', content, re.IGNORECASE)
                                if of_urls:
                                    self.results["has_onlyfans"] = True
                                    self.results["onlyfans_urls"] = list(set(of_urls))
                                    self.results["debug_info"].append("Found OnlyFans URLs in desperate mode")
                                    return True
                                
                                # Strategy 2: Just confirm OnlyFans exists
                                self.results["has_onlyfans"] = True
                                self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                                self.results["debug_info"].append("OnlyFans confirmed to exist in desperate mode")
                                return True
                                
                        elif response.status_code == 403:
                            self.results["debug_info"].append(f"Approach {i} blocked (403)")
                        elif self.results.get("age_verification_detected", False):
                            self.results["debug_info"].append(f"Approach {i} status: {response.status_code}")
                            
                    except Exception as e:
                        self.results["debug_info"].append(f"Approach {i} failed: {str(e)[:50]}")
                        continue
                        
        except Exception as e:
            self.results["errors"].append(f"Desperate mode extraction failed: {str(e)}")
            
        return False

    async def _handle_redirects_better(self, bio_link: str) -> bool:
        """Enhanced redirect handling"""
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=False) as client:
                current_url = bio_link
                max_redirects = 5
                redirect_count = 0
                
                while redirect_count < max_redirects:
                    try:
                        response = await client.get(current_url)
                        
                        if response.status_code in (301, 302, 303, 307, 308):
                            location = response.headers.get('location')
                            if location:
                                if location.startswith('/'):
                                    current_url = urljoin(current_url, location)
                                elif location.startswith('http'):
                                    current_url = location
                                elif self.results.get("age_verification_detected", False):
                                    current_url = urljoin(current_url, location)
                                
                                redirect_count += 1
                                self.results["debug_info"].append(f"Redirect {redirect_count}: {current_url}")
                                continue
                            elif self.results.get("age_verification_detected", False):
                                break
                        elif response.status_code == 200:
                            content = response.text.lower()
                            of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', content, re.IGNORECASE)
                            
                            if of_urls:
                                self.results["has_onlyfans"] = True
                                self.results["onlyfans_urls"] = list(set(of_urls))
                                self.results["debug_info"].append(f"Found OnlyFans after {redirect_count} redirects")
                                return True
                            break
                        elif self.results.get("age_verification_detected", False):
                            break
                            
                    except Exception as e:
                        self.results["errors"].append(f"Redirect handling failed: {str(e)}")
                        break
                        
        except Exception as e:
            self.results["errors"].append(f"Redirect handling failed: {str(e)}")
            
        return False

    async def _try_different_user_agents(self, bio_link: str) -> bool:
        """Try different user agents"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        ]
        
        try:
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
                                self.results["debug_info"].append(f"Found OnlyFans with User-Agent: {user_agent[:50]}...")
                                return True
                                
                    except Exception as e:
                        continue
                        
        except Exception as e:
            self.results["errors"].append(f"User agent testing failed: {str(e)}")
            
        return False

    async def _enhanced_link_extraction(self, bio_link: str) -> bool:
        """Enhanced link extraction"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(bio_link)
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Look for OnlyFans in various patterns
                    patterns = [
                        r'<img[^>]*alt=["\']([^"\']*onlyfans[^"\']*)["\'][^>]*>',
                        r'data-url=["\']([^"\']*onlyfans\.com[^"\']*)["\']',
                        r'data-href=["\']([^"\']*onlyfans\.com[^"\']*)["\']',
                        r'<[^>]*>([^<]*onlyfans[^<]*)</[^>]*>'
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            clean_urls = []
                            for match in matches:
                                if isinstance(match, tuple):
                                    match = match[0]
                                if 'onlyfans' in match.lower():
                                    of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', match, re.IGNORECASE)
                                    if of_urls:
                                        clean_urls.extend(of_urls)
                                    elif self.results.get("age_verification_detected", False):
                                        # Look for username patterns
                                        username_match = re.search(r'onlyfans\.com/([a-zA-Z0-9_-]+)', match, re.IGNORECASE)
                                        if username_match:
                                            username = username_match.group(1)
                                            clean_urls.append(f"https://onlyfans.com/{username}")
                            
                            if clean_urls:
                                self.results["has_onlyfans"] = True
                                self.results["onlyfans_urls"] = list(set(clean_urls))
                                self.results["debug_info"].append(f"Found OnlyFans with pattern: {pattern[:30]}...")
                                return True
                                
        except Exception as e:
            self.results["errors"].append(f"Enhanced link extraction failed: {str(e)}")
            
        return False

    async def _handle_linkme_interactive(self, bio_link: str) -> bool:
        """Interactive detection for link.me (based on working solution)"""
        try:
            async with async_playwright() as p:
                # Use safe browser launch
                browser = await self._launch_browser_safely(p)
                
                context = await browser.new_context()
                page = await context.new_page()
                
                onlyfans_found = None
                
                # Handle redirects
                async def handle_response(response):
                    nonlocal onlyfans_found
                    if response.status >= 300 and response.status < 400:
                        location = response.headers.get('location', '')
                        if 'onlyfans.com' in location.lower() and '/files' not in location:
                            onlyfans_found = location
                            self.results["debug_info"].append(f"OnlyFans redirect captured: {location}")
                
                page.on('response', handle_response)
                
                try:
                    self.results["debug_info"].append("Loading link.me page...")
                    await page.goto(bio_link, wait_until="domcontentloaded", timeout=15000)
                    await page.wait_for_timeout(3000)
                    
                    # Accept cookies if present
                    try:
                        accept_btn = page.locator("button:has-text('Accept All')")
                        if await accept_btn.count() > 0:
                            await accept_btn.click()
                            await page.wait_for_timeout(2000)
                            self.results["debug_info"].append("Cookies accepted")
                    except:
                        pass
                    
                    # Look for OnlyFans content in the page first
                    page_content = await page.content()
                    of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', page_content, re.IGNORECASE)
                    if of_urls:
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = list(set(of_urls))
                        self.results["debug_info"].append("Found OnlyFans URLs directly in page content")
                        await browser.close()
                        return True
                    
                    # Just check if OnlyFans is mentioned anywhere
                    if 'onlyfans' in page_content.lower():
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                        self.results["debug_info"].append("OnlyFans detected in page content")
                        await browser.close()
                        return True
                    
                    # Click the OnlyFans container div
                    onlyfans_container = page.locator(".singlealbum.singlebigitem.socialmedialink:has-text('OnlyFans')")
                    
                    if await onlyfans_container.count() > 0:
                        self.results["debug_info"].append("Found OnlyFans container, clicking...")
                        await onlyfans_container.click(force=True)
                        await page.wait_for_timeout(3000)
                        
                        # Look for Continue button
                        continue_selectors = [
                            "button:has-text('Continue')",
                            "button:has-text('CONTINUE')",
                            "button:has-text('Proceed')",
                            "button:has-text('Enter')",
                            "button:has-text('Yes')"
                        ]
                        
                        for selector in continue_selectors:
                            try:
                                continue_btn = page.locator(selector)
                                if await continue_btn.count() > 0:
                                    await continue_btn.wait_for(state="visible", timeout=2000)
                                    await continue_btn.click()
                                    self.results["debug_info"].append("Continue button clicked")
                                    
                                    # Wait for redirect
                                    await page.wait_for_timeout(5000)
                                    
                                    # Check final result
                                    current_url = page.url
                                    if 'onlyfans.com' in current_url.lower():
                                        onlyfans_found = current_url
                                        break
                                    elif onlyfans_found:
                                        break
                                    
                            except Exception:
                                continue
                        
                        if onlyfans_found:
                            self.results["has_onlyfans"] = True
                            self.results["onlyfans_urls"] = [onlyfans_found]
                            await browser.close()
                            return True
                    
                    # If clicking didn't work, try to extract from any visible OnlyFans elements
                    try:
                        # Look for any element containing OnlyFans text
                        onlyfans_elements = page.locator("*:has-text('OnlyFans')")
                        if await onlyfans_elements.count() > 0:
                            self.results["debug_info"].append("Found OnlyFans text elements, extracting...")
                            
                            for i in range(await onlyfans_elements.count()):
                                try:
                                    element = onlyfans_elements.nth(i)
                                    text = await element.text_content()
                                    if text and 'onlyfans' in text.lower():
                                        # Look for URLs in the text
                                        urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', text, re.IGNORECASE)
                                        if urls:
                                            self.results["has_onlyfans"] = True
                                            self.results["onlyfans_urls"] = list(set(urls))
                                            self.results["debug_info"].append("Found OnlyFans URLs in text elements")
                                            await browser.close()
                                            return True
                                except:
                                    continue
                            
                    except Exception as e:
                        self.results["debug_info"].append(f"Text extraction failed: {str(e)}")
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            self.results["errors"].append(f"Link.me interactive detection failed: {str(e)}")
            
        return False

    async def _handle_linkme_fallback(self, bio_link: str) -> bool:
        """Special fallback detection for link.me when Playwright fails"""
        try:
            self.results["debug_info"].append(f"=== DEBUGGING {bio_link} ===")
            
            # Strategy 1: Try with enhanced HTTP detection specifically for link.me
            async with httpx.AsyncClient(timeout=25.0) as client:
                # Use link.me specific headers that work
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                    'Referer': 'https://www.google.com/'
                }
                
                response = await client.get(bio_link, headers=headers)
                
                # Debug logging for response details
                self.results["debug_info"].append(f"Response status: {response.status_code}")
                self.results["debug_info"].append(f"Response length: {len(response.text)}")
                self.results["debug_info"].append(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Debug: Check for OnlyFans mentions
                    has_onlyfans_mention = 'onlyfans' in content.lower()
                    self.results["debug_info"].append(f"Contains 'onlyfans' (case-insensitive): {has_onlyfans_mention}")
                    
                    # NEW: Check for age verification indicators (this is the key insight!)
                    age_verification_indicators = [
                        '18+', '18 plus', 'age verification', 'age gate', 'age check',
                        'confirm age', 'verify age', 'enter site', 'i\'m 18+', 'i am 18+',
                        'adult content', 'mature content', 'nsfw', 'explicit content',
                        'click to enter', 'proceed to site', 'continue to site',
                        'age confirmation', 'age verification required', 'adult warning',
                        'mature warning', 'explicit warning', 'adult site', 'mature site'
                    ]
                    
                    age_verification_found = False
                    found_indicators = []
                    
                    for indicator in age_verification_indicators:
                        # Search in entire content, not just first 1000 chars
                            age_verification_found = True
                            found_indicators.append(indicator)
                    
                    self.results["debug_info"].append(f"Age verification indicators found: {age_verification_found}")
                    if found_indicators:
                        self.results["debug_info"].append(f"Found indicators: {found_indicators[:5]}...")  # Show first 5
                    
                    # NEW: Decision logic - if we find age verification, it's likely OnlyFans content
                    age_verification_detected = (age_verification_found or js_age_found or popup_found or data_age_found or css_age_found or meta_age_found or script_age_found)
                    self.results["debug_info"].append(f"Overall age verification detected: {age_verification_detected}")
                    # Store age verification status in results for other methods to access
                    self.results["age_verification_detected"] = age_verification_detected
                    # Debug: Show HTML preview
                    html_preview = content[:1000] if len(content) > 1000 else content
                    self.results["debug_info"].append(f"Raw HTML preview (first 1000 chars):\n{html_preview}")
                    
                    # Enhanced detection patterns
                    detection_patterns = [
                        # Pattern 1: Standard OnlyFans URLs
                        r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*',
                        # Pattern 2: OnlyFans with username
                        r'onlyfans\.com/[a-zA-Z0-9_-]+',
                        # Pattern 3: Data attributes
                        r'data-url=["\'][^"\']*onlyfans[^"\']*["\']',
                        r'data-link=["\'][^"\']*onlyfans[^"\']*["\']',
                        # Pattern 4: JSON embedded data
                        r'"[^"]*onlyfans[^"]*"',
                        # Pattern 5: Case variations
                        r'[Oo]nly[Ff]ans',
                        r'[Oo]nly[Ff]an',
                        # Pattern 6: Encoded URLs
                        r'%6F%6E%6C%79%66%61%6E%73',  # "onlyfans" in hex
                    ]
                    
                    # Test each pattern
                    for i, pattern in enumerate(detection_patterns, 1):
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            self.results["debug_info"].append(f"Pattern {i} found {len(matches)} matches: {matches[:3]}...")
                    
                    # Look for OnlyFans mentions in link.me specific patterns
                    if has_onlyfans_mention:
                        self.results["debug_info"].append("OnlyFans found in link.me content via fallback")
                        
                        # Extract URLs if possible
                        of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', content, re.IGNORECASE)
                        if of_urls:
                            self.results["has_onlyfans"] = True
                            self.results["onlyfans_urls"] = list(set(of_urls))
                            self.results["debug_info"].append("Found OnlyFans URLs in link.me fallback")
                            self.results["debug_info"].append("=== END DEBUG ===")
                            return True
                        
                        # Just confirm OnlyFans exists
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                        self.results["debug_info"].append("OnlyFans confirmed in link.me via fallback")
                        self.results["debug_info"].append("=== END DEBUG ===")
                        return True
                    elif self.results.get("age_verification_detected", False):
                        self.results["debug_info"].append("No OnlyFans mention found in content")
                    elif self.results.get("age_verification_detected", False):
                        # NEW: Age verification found = high probability of OnlyFans
                        self.results["debug_info"].append("Age verification detected - high probability of OnlyFans content")
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                        self.results["debug_info"].append("OnlyFans confirmed via age verification detection")
                        self.results["debug_info"].append("=== END DEBUG ===")
                        return True
                
                # Strategy 2: Try with mobile user agent
                self.results["debug_info"].append("Trying mobile user agent approach...")
                mobile_headers = {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                response = await client.get(bio_link, headers=mobile_headers)
                
                if response.status_code == 200:
                    content = response.text
                    mobile_has_onlyfans = 'onlyfans' in content.lower()
                    self.results["debug_info"].append(f"Mobile approach - Contains 'onlyfans': {mobile_has_onlyfans}")
                    # NEW: Check for age verification in mobile response too
                    mobile_age_verification = any(indicator.lower() in content.lower() for indicator in age_verification_indicators)
                    self.results["debug_info"].append(f"Mobile approach - Age verification detected: {mobile_age_verification}")
                    
                    if mobile_has_onlyfans or mobile_age_verification:
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                        self.results["debug_info"].append("=== END DEBUG ===")
                        return True
                    
                    if mobile_has_onlyfans:
                        self.results["debug_info"].append("OnlyFans found in link.me via mobile fallback")
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                        self.results["debug_info"].append("=== END DEBUG ===")
                        return True
                
                # Strategy 3: Try with different referrers
                self.results["debug_info"].append("Trying different referrer approach...")
                referrer_headers = headers.copy()
                referrer_headers['Referer'] = 'https://www.bing.com/'
                
                response = await client.get(bio_link, headers=referrer_headers)
                
                if response.status_code == 200:
                    content = response.text
                    referrer_has_onlyfans = 'onlyfans' in content.lower()
                    self.results["debug_info"].append(f"Referrer approach - Contains 'onlyfans': {referrer_has_onlyfans}")
                    # NEW: Check for age verification in referrer response too
                    referrer_age_verification = any(indicator.lower() in content.lower() for indicator in age_verification_indicators)
                    self.results["debug_info"].append(f"Referrer approach - Age verification detected: {referrer_age_verification}")
                    
                    if referrer_has_onlyfans or referrer_age_verification:
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                        self.results["debug_info"].append("=== END DEBUG ===")
                        return True
                    
                    if referrer_has_onlyfans:
                        self.results["debug_info"].append("OnlyFans found in link.me via referrer fallback")
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                        self.results["debug_info"].append("=== END DEBUG ===")
                        return True
                
                self.results["debug_info"].append("=== END DEBUG ===")
                        
        except Exception as e:
            self.results["errors"].append(f"Link.me fallback detection failed: {str(e)}")
            self.results["debug_info"].append("=== END DEBUG ===")
            
        return False

    async def _handle_beacons_interactive(self, bio_link: str) -> bool:
        """Interactive detection for beacons.ai with aggressive human-like behavior"""
        try:
            async with async_playwright() as p:
                # Use safe browser launch
                browser = await self._launch_browser_safely(p)
                
                # Create a more sophisticated context with advanced settings
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-US',
                    timezone_id='America/New_York',
                    permissions=['geolocation'],
                    extra_http_headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0'
                    }
                )
                
                page = await context.new_page()
                
                try:
                    self.results["debug_info"].append("Loading beacons.ai page with aggressive human-like behavior...")
                    
                    # First, try to visit the homepage to establish a session
                    try:
                        homepage = "https://beacons.ai"
                        await page.goto(homepage, wait_until="domcontentloaded", timeout=15000)
                        await page.wait_for_timeout(3000)
                        self.results["debug_info"].append("Visited homepage to establish session")
                    except:
                        pass
                    
                    # Now visit the target page
                    await page.goto(bio_link, wait_until="domcontentloaded", timeout=20000)
                    
                    # Wait like a human would
                    await page.wait_for_timeout(3000)
                    
                    # Simulate realistic mouse movements
                    await page.mouse.move(100, 100)
                    await page.wait_for_timeout(800)
                    await page.mouse.move(500, 300)
                    await page.wait_for_timeout(600)
                    await page.mouse.move(800, 200)
                    await page.wait_for_timeout(700)
                    await page.mouse.move(400, 600)
                    await page.wait_for_timeout(500)
                    
                    # Scroll like a human (gradual, realistic)
                    for i in range(1, 6):
                        await page.evaluate(f"window.scrollTo(0, {i * 100})")
                        await page.wait_for_timeout(300 + (i * 100))  # Variable timing
                    
                    await page.wait_for_timeout(2000)
                    
                    # Scroll back up gradually
                    for i in range(5, 0, -1):
                        await page.evaluate(f"window.scrollTo(0, {i * 100})")
                        await page.wait_for_timeout(200 + (i * 50))
                    
                    await page.wait_for_timeout(1500)
                    
                    # Try to interact with any visible elements
                    try:
                        # Look for any clickable elements and hover over them
                        clickable_elements = page.locator("a, button, [role='button'], [tabindex]")
                        if await clickable_elements.count() > 0:
                            for i in range(min(5, await clickable_elements.count())):
                                try:
                                    element = clickable_elements.nth(i)
                                    await element.hover()
                                    await page.wait_for_timeout(500)
                                except:
                                    continue
                    except:
                        pass
                    
                    # Wait for content to load
                    await page.wait_for_timeout(4000)
                    
                    # Look for OnlyFans content
                    page_content = await page.content()
                    
                    # Just check if OnlyFans is mentioned anywhere
                    if 'onlyfans' in page_content.lower():
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                        self.results["debug_info"].append("OnlyFans detected in beacons.ai content")
                        await browser.close()
                        return True
                    
                    # If no OnlyFans found, try to wait longer and scroll more
                    self.results["debug_info"].append("No OnlyFans found, trying more aggressive human-like behavior...")
                    
                    # More aggressive scrolling
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(3000)
                    await page.evaluate("window.scrollTo(0, 0)")
                    await page.wait_for_timeout(2000)
                    
                    # Try to trigger any JavaScript events
                    try:
                        await page.evaluate("window.dispatchEvent(new Event('scroll'))")
                        await page.wait_for_timeout(1000)
                        await page.evaluate("window.dispatchEvent(new Event('resize'))")
                        await page.wait_for_timeout(1000)
                        await page.evaluate("window.dispatchEvent(new Event('focus'))")
                        await page.wait_for_timeout(1000)
                    except:
                        pass
                    
                    # Check again
                    page_content = await page.content()
                    if 'onlyfans' in page_content.lower():
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                        self.results["debug_info"].append("OnlyFans detected after aggressive behavior")
                        await browser.close()
                        return True
                        
                finally:
                    await browser.close()
                    
        except Exception as e:
            self.results["errors"].append(f"Beacons.ai interactive detection failed: {str(e)}")
            
        return False

    async def _handle_beacons_alternative(self, bio_link: str) -> bool:
        """Alternative approach for beacons.ai using different methods"""
        try:
            self.results["debug_info"].append("Trying alternative approach for beacons.ai...")
            
            # Try with different user agents and approaches
            approaches = [
                {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                    'Referer': 'https://www.google.com/'
                },
                {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Referer': 'https://www.bing.com/'
                },
                {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': 'https://www.facebook.com/'
                }
            ]
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                for i, headers in enumerate(approaches, 1):
                    try:
                        self.results["debug_info"].append(f"Alternative approach {i} for beacons.ai...")
                        
                        # Try to access the page with these headers
                        response = await client.get(bio_link, headers=headers)
                        
                        if response.status_code == 200:
                            content = response.text
                            
                            # Check if OnlyFans is mentioned
                            if 'onlyfans' in content.lower():
                                self.results["has_onlyfans"] = True
                                self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                                self.results["debug_info"].append(f"Alternative approach {i} succeeded!")
                                return True
                                
                        elif response.status_code == 403:
                            self.results["debug_info"].append(f"Alternative approach {i} blocked (403)")
                        elif self.results.get("age_verification_detected", False):
                            self.results["debug_info"].append(f"Alternative approach {i} status: {response.status_code}")
                            
                    except Exception as e:
                        self.results["debug_info"].append(f"Alternative approach {i} failed: {str(e)[:50]}")
                        continue
                        
        except Exception as e:
            self.results["errors"].append(f"Alternative beacons.ai approach failed: {str(e)}")
            
        return False

    async def _handle_xli_interactive(self, bio_link: str) -> bool:
        """Interactive detection for xli.ink"""
        try:
            async with async_playwright() as p:
                # Use safe browser launch
                browser = await self._launch_browser_safely(p)
                
                context = await browser.new_context()
                page = await context.new_page()
                
                try:
                    self.results["debug_info"].append("Loading xli.ink page...")
                    await page.goto(bio_link, wait_until="networkidle", timeout=20000)
                    
                    # Wait for dynamic content
                    await page.wait_for_timeout(8000)
                    
                    # Look for OnlyFans content
                    page_content = await page.content()
                    of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', page_content, re.IGNORECASE)
                    
                    if of_urls:
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = list(set(of_urls))
                        await browser.close()
                        return True
                    
                    # Just check if OnlyFans is mentioned anywhere
                    if 'onlyfans' in page_content.lower():
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = ["https://onlyfans.com/detected"]
                        self.results["debug_info"].append("OnlyFans detected in xli.ink content")
                        await browser.close()
                        return True
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            self.results["errors"].append(f"Xli.ink interactive detection failed: {str(e)}")
            
        return False

    async def _generic_interactive_detection(self, bio_link: str) -> bool:
        """Generic interactive detection for other platforms"""
        try:
            async with async_playwright() as p:
                # Use safe browser launch
                browser = await self._launch_browser_safely(p)
                
                context = await browser.new_context()
                page = await context.new_page()
                
                try:
                    self.results["debug_info"].append("Generic interactive detection...")
                    await page.goto(bio_link, wait_until="networkidle", timeout=20000)
                    
                    # Wait for content
                    await page.wait_for_timeout(5000)
                    
                    # Look for OnlyFans content
                    page_content = await page.content()
                    of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', page_content, re.IGNORECASE)
                    
                    if of_urls:
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = list(set(of_urls))
                        await browser.close()
                        return True
                        
                finally:
                    await browser.close()
                    
        except Exception as e:
            self.results["errors"].append(f"Generic interactive detection failed: {str(e)}")
            
        return False

# Main function for n8n integration
async def detect_onlyfans_in_bio_link(bio_link: str) -> Dict:
    """Main function for n8n integration"""
    detector = HybridFinalDetector()
    return await detector.detect_onlyfans(bio_link)

def main():
    """Command line interface for n8n integration"""
    import sys
    import json
    if len(sys.argv) != 2:
        print("Usage: python onlyfans_detector_hybrid_final.py <bio_link>")
        sys.exit(1)
        
    bio_link = sys.argv[1]
    
    async def run_detection():
        result = await detect_onlyfans_in_bio_link(bio_link)
        print(json.dumps(result, indent=2))
        
    asyncio.run(run_detection())

if __name__ == "__main__":
    main()
