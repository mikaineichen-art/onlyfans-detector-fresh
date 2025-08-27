import asyncio
import httpx
import re
import logging
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OnlyFansDetector:
    def __init__(self):
        self.onlyfans_patterns = [
            r'https?://(?:www\.)?onlyfans\.com/[a-zA-Z0-9_.-]+',
            r'https?://(?:www\.)?onlyfans\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+',
            r'onlyfans\.com/[a-zA-Z0-9_.-]+',
            r'onlyfans\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+'
        ]
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Enhanced patterns for bio link platforms
        self.platform_patterns = {
            'link.me': {
                'selectors': ['a[href*="onlyfans"], a[href*="onlyfans.com"]', '.link-item a', '.bio-link a'],
                'text_patterns': [r'onlyfans\.com/[a-zA-Z0-9_.-]+', r'@[a-zA-Z0-9_.-]+'],
                'interactive_elements': ['.link-item', '.bio-link', '.social-link']
            },
            'beacons.ai': {
                'selectors': ['a[href*="onlyfans"], a[href*="onlyfans.com"]', '.link a', '.social-link a'],
                'text_patterns': [r'onlyfans\.com/[a-zA-Z0-9_.-]+', r'@[a-zA-Z0-9_.-]+'],
                'interactive_elements': ['.link', '.social-link', '.bio-link']
            },
            'taplink.cc': {
                'selectors': ['a[href*="onlyfans"], a[href*="onlyfans.com"]', '.link a', '.social a'],
                'text_patterns': [r'onlyfans\.com/[a-zA-Z0-9_.-]+', r'@[a-zA-Z0-9_.-]+'],
                'interactive_elements': ['.link', '.social', '.bio']
            }
        }

    async def detect_onlyfans_in_bio_link(self, bio_link: str) -> Dict:
        """
        Enhanced OnlyFans detection with multiple fallback strategies
        """
        start_time = time.time()
        debug_info = []
        errors = []
        detection_method = None
        
        try:
            # Phase 1: Fast HTTP detection (1-2 seconds)
            debug_info.append("Phase 1: Fast HTTP detection")
            result = await self._fast_http_detection(bio_link)
            if result['has_onlyfans']:
                detection_method = "Phase 1: Direct HTTP detection"
                return self._format_result(True, result['onlyfans_urls'], detection_method, debug_info, errors, start_time)
            
            # Phase 2: Enhanced HTTP detection (2-5 seconds)
            debug_info.append("Phase 2: Enhanced HTTP detection")
            result = await self._enhanced_http_detection(bio_link)
            if result['has_onlyfans']:
                detection_method = "Phase 2: Enhanced HTTP strategies"
                return self._format_result(True, result['onlyfans_urls'], detection_method, debug_info, errors, start_time)
            
            # Phase 3: Try Playwright if available (5-15 seconds)
            debug_info.append("Phase 3: Interactive detection with Playwright")
            try:
                result = await self._playwright_detection(bio_link)
                if result['has_onlyfans']:
                    detection_method = "Phase 3: Interactive Playwright detection"
                    return self._format_result(True, result['onlyfans_urls'], detection_method, debug_info, errors, start_time)
            except Exception as e:
                error_msg = f"Playwright detection failed: {str(e)}"
                errors.append(error_msg)
                debug_info.append(f"Phase 3: {error_msg}")
            
            # Phase 4: Final fallback extraction (2-3 seconds)
            debug_info.append("Phase 4: Final fallback extraction")
            result = await self._final_fallback_extraction(bio_link)
            if result['has_onlyfans']:
                detection_method = "Phase 4: Fallback extraction"
                return self._format_result(True, result['onlyfans_urls'], detection_method, debug_info, errors, start_time)
            
            # Phase 5: Desperate mode (3-5 seconds)
            debug_info.append("Phase 5: Desperate mode extraction")
            result = await self._desperate_mode_extraction(bio_link)
            if result['has_onlyfans']:
                detection_method = "Phase 5: Desperate mode extraction"
                return self._format_result(True, result['onlyfans_urls'], detection_method, debug_info, errors, start_time)
            
            debug_info.append("All phases completed - no OnlyFans found")
            return self._format_result(False, [], None, debug_info, errors, start_time)
            
        except Exception as e:
            error_msg = f"Detection failed: {str(e)}"
            errors.append(error_msg)
            debug_info.append(f"Error: {error_msg}")
            return self._format_result(False, [], None, debug_info, errors, start_time)

    async def _fast_http_detection(self, bio_link: str) -> Dict:
        """Fast HTTP detection - direct content check"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(bio_link, follow_redirects=True)
                content = response.text.lower()
                
                # Check for direct OnlyFans links
                for pattern in self.onlyfans_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        return {'has_onlyfans': True, 'onlyfans_urls': matches}
                
                return {'has_onlyfans': False, 'onlyfans_urls': []}
                
        except Exception as e:
            logger.warning(f"Fast HTTP detection failed: {e}")
            return {'has_onlyfans': False, 'onlyfans_urls': []}

    async def _enhanced_http_detection(self, bio_link: str) -> Dict:
        """Enhanced HTTP detection with multiple strategies"""
        try:
            # Try different User-Agents
            for user_agent in self.user_agents[:3]:  # Limit to 3 attempts
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        headers = {'User-Agent': user_agent}
                        response = await client.get(bio_link, headers=headers, follow_redirects=True)
                        content = response.text.lower()
                        
                        # Check for OnlyFans
                        for pattern in self.onlyfans_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                debug_info.append(f"Found OnlyFans with User-Agent: {user_agent[:50]}...")
                                return {'has_onlyfans': True, 'onlyfans_urls': matches}
                        
                        # Check for redirects
                        if response.history:
                            redirect_count = len(response.history)
                            debug_info.append(f"Redirect {redirect_count}: {response.url}")
                            
                            # Check final URL content
                            final_content = response.text.lower()
                            for pattern in self.onlyfans_patterns:
                                matches = re.findall(pattern, final_content, re.IGNORECASE)
                                if matches:
                                    debug_info.append(f"Found OnlyFans after {redirect_count} redirects")
                                    return {'has_onlyfans': True, 'onlyfans_urls': matches}
                        
                except Exception as e:
                    continue
            
            return {'has_onlyfans': False, 'onlyfans_urls': []}
            
        except Exception as e:
            logger.warning(f"Enhanced HTTP detection failed: {e}")
            return {'has_onlyfans': False, 'onlyfans_urls': []}

    async def _playwright_detection(self, bio_link: str) -> Dict:
        """Playwright-based detection with fallback"""
        try:
            # Try to import Playwright
            try:
                from playwright.async_api import async_playwright
            except ImportError:
                raise Exception("Playwright not available")
            
            async with async_playwright() as p:
                # Try to launch browser
                try:
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
                except Exception as e:
                    # Fallback to basic chromium
                    logger.warning(f"Chrome launch failed: {e}, falling back to basic chromium")
                    browser = await p.chromium.launch(
                        headless=True,
                        args=['--no-sandbox', '--disable-setuid-sandbox']
                    )
                
                try:
                    page = await browser.new_page()
                    
                    # Set viewport and user agent
                    await page.set_viewport_size({"width": 1280, "height": 720})
                    await page.set_extra_http_headers({
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    
                    # Navigate to page
                    await page.goto(bio_link, wait_until='networkidle', timeout=15000)
                    
                    # Wait for content to load
                    await page.wait_for_timeout(2000)
                    
                    # Check for OnlyFans links
                    content = await page.content()
                    for pattern in self.onlyfans_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            await browser.close()
                            return {'has_onlyfans': True, 'onlyfans_urls': matches}
                    
                    # Try interactive clicking for specific platforms
                    platform = self._get_platform(bio_link)
                    if platform in self.platform_patterns:
                        result = await self._interactive_platform_detection(page, platform)
                        if result['has_onlyfans']:
                            await browser.close()
                            return result
                    
                    await browser.close()
                    return {'has_onlyfans': False, 'onlyfans_urls': []}
                    
                except Exception as e:
                    await browser.close()
                    raise e
                    
        except Exception as e:
            logger.warning(f"Playwright detection failed: {e}")
            # Try alternative approaches for specific platforms
            return await self._alternative_platform_detection(bio_link)

    async def _interactive_platform_detection(self, page, platform: str) -> Dict:
        """Interactive detection for specific platforms"""
        try:
            platform_config = self.platform_patterns[platform]
            
            # Try clicking on interactive elements
            for selector in platform_config['interactive_elements']:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements[:3]:  # Limit to 3 elements
                        try:
                            await element.click()
                            await page.wait_for_timeout(1000)
                            
                            # Check content after click
                            content = await page.content()
                            for pattern in self.onlyfans_patterns:
                                matches = re.findall(pattern, content, re.IGNORECASE)
                                if matches:
                                    return {'has_onlyfans': True, 'onlyfans_urls': matches}
                        except:
                            continue
                except:
                    continue
            
            return {'has_onlyfans': False, 'onlyfans_urls': []}
            
        except Exception as e:
            logger.warning(f"Interactive detection failed: {e}")
            return {'has_onlyfans': False, 'onlyfans_urls': []}

    async def _alternative_platform_detection(self, bio_link: str) -> Dict:
        """Alternative detection methods for specific platforms"""
        platform = self._get_platform(bio_link)
        
        if platform == 'beacons.ai':
            return await self._beacons_alternative_detection(bio_link)
        elif platform == 'link.me':
            return await self._linkme_alternative_detection(bio_link)
        
        return {'has_onlyfans': False, 'onlyfans_urls': []}

    async def _beacons_alternative_detection(self, bio_link: str) -> Dict:
        """Alternative detection for beacons.ai"""
        try:
            debug_info.append("Trying alternative approach for beacons.ai...")
            
            # Try with different headers and approaches
            for i, user_agent in enumerate(self.user_agents[:3]):
                try:
                    debug_info.append(f"Alternative approach {i+1} for beacons.ai...")
                    
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        headers = {
                            'User-Agent': user_agent,
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Accept-Encoding': 'gzip, deflate',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1'
                        }
                        
                        response = await client.get(bio_link, headers=headers, follow_redirects=True)
                        content = response.text.lower()
                        
                        # Check for OnlyFans
                        for pattern in self.onlyfans_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                debug_info.append(f"Alternative approach {i+1} succeeded!")
                                return {'has_onlyfans': True, 'onlyfans_urls': matches}
                        
                except Exception as e:
                    continue
            
            debug_info.append("All alternative approaches failed")
            return {'has_onlyfans': False, 'onlyfans_urls': []}
            
        except Exception as e:
            logger.warning(f"Beacons alternative detection failed: {e}")
            return {'has_onlyfans': False, 'onlyfans_urls': []}

    async def _linkme_alternative_detection(self, bio_link: str) -> Dict:
        """Alternative detection for link.me"""
        try:
            # Try with different approaches
            for i, user_agent in enumerate(self.user_agents[:3]):
                try:
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        headers = {
                            'User-Agent': user_agent,
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Accept-Encoding': 'gzip, deflate',
                            'Connection': 'keep-alive'
                        }
                        
                        response = await client.get(bio_link, headers=headers, follow_redirects=True)
                        content = response.text.lower()
                        
                        # Check for OnlyFans
                        for pattern in self.onlyfans_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                return {'has_onlyfans': True, 'onlyfans_urls': matches}
                        
                except Exception as e:
                    continue
            
            return {'has_onlyfans': False, 'onlyfans_urls': []}
            
        except Exception as e:
            logger.warning(f"Link.me alternative detection failed: {e}")
            return {'has_onlyfans': False, 'onlyfans_urls': []}

    async def _final_fallback_extraction(self, bio_link: str) -> Dict:
        """Final fallback extraction with aggressive text parsing"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try with mobile user agent
                headers = {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
                
                response = await client.get(bio_link, headers=headers, follow_redirects=True)
                content = response.text.lower()
                
                # Aggressive text extraction
                text_content = re.sub(r'<[^>]+>', ' ', content)
                text_content = re.sub(r'\s+', ' ', text_content)
                
                # Check for OnlyFans patterns in text
                for pattern in self.onlyfans_patterns:
                    matches = re.findall(pattern, text_content, re.IGNORECASE)
                    if matches:
                        return {'has_onlyfans': True, 'onlyfans_urls': matches}
                
                return {'has_onlyfans': False, 'onlyfans_urls': []}
                
        except Exception as e:
            logger.warning(f"Final fallback extraction failed: {e}")
            return {'has_onlyfans': False, 'onlyfans_urls': []}

    async def _desperate_mode_extraction(self, bio_link: str) -> Dict:
        """Desperate mode - try everything possible"""
        try:
            debug_info.append("Desperate mode: Trying aggressive extraction...")
            
            # Try multiple user agents and approaches
            for i, user_agent in enumerate(self.user_agents):
                try:
                    debug_info.append(f"Desperate approach {i+1}: {user_agent[:50]}...")
                    
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        headers = {
                            'User-Agent': user_agent,
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Accept-Encoding': 'gzip, deflate',
                            'Connection': 'keep-alive',
                            'Cache-Control': 'no-cache'
                        }
                        
                        response = await client.get(bio_link, headers=headers, follow_redirects=True)
                        content = response.text.lower()
                        
                        # Check for OnlyFans
                        for pattern in self.onlyfans_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                debug_info.append(f"OnlyFans found in approach {i+1}, extracting...")
                                debug_info.append("OnlyFans confirmed to exist in desperate mode")
                                return {'has_onlyfans': True, 'onlyfans_urls': matches}
                        
                        # Check for blocked responses
                        if response.status_code == 403:
                            debug_info.append(f"Approach {i+1} blocked (403)")
                            continue
                        
                except Exception as e:
                    continue
            
            debug_info.append("All desperate approaches failed")
            return {'has_onlyfans': False, 'onlyfans_urls': []}
            
        except Exception as e:
            logger.warning(f"Desperate mode extraction failed: {e}")
            return {'has_onlyfans': False, 'onlyfans_urls': []}

    def _get_platform(self, url: str) -> str:
        """Extract platform from URL"""
        domain = urlparse(url).netloc.lower()
        if 'link.me' in domain:
            return 'link.me'
        elif 'beacons.ai' in domain:
            return 'beacons.ai'
        elif 'taplink.cc' in domain:
            return 'taplink.cc'
        return 'unknown'

    def _format_result(self, has_onlyfans: bool, onlyfans_urls: List[str], 
                      detection_method: Optional[str], debug_info: List[str], 
                      errors: List[str], start_time: float) -> Dict:
        """Format the final result"""
        processing_time = time.time() - start_time
        
        return {
            'has_onlyfans': has_onlyfans,
            'onlyfans_urls': onlyfans_urls,
            'detection_method': detection_method,
            'debug_info': debug_info,
            'errors': errors,
            'processing_time': round(processing_time, 2)
        }

# Global detector instance
detector = OnlyFansDetector()

async def detect_onlyfans_in_bio_link(bio_link: str) -> Dict:
    """
    Main function to detect OnlyFans links in a bio link
    """
    return await detector.detect_onlyfans_in_bio_link(bio_link)

# For testing
if __name__ == "__main__":
    async def test():
        test_links = [
            "https://link.me/kaylasummers",
            "https://beacons.ai/zoeneli",
            "https://taplink.cc/passionasian"
        ]
        
        for link in test_links:
            print(f"\nTesting: {link}")
            result = await detect_onlyfans_in_bio_link(link)
            print(f"Result: {result['has_onlyfans']}")
            print(f"Method: {result['detection_method']}")
            print(f"URLs: {result['onlyfans_urls']}")
    
    asyncio.run(test())
