#!/usr/bin/env python3
"""
Ultimate HTTP-Only OnlyFans Detector
Maximum accuracy using sophisticated HTTP techniques
No browser automation - fast and reliable
"""

import asyncio
import json
import re
import sys
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import httpx

# OnlyFans detection regex
OF_REGEX = re.compile(r"onlyfans\.com", re.IGNORECASE)

class UltimateHTTPDetector:
    """Ultimate HTTP-only detector with maximum accuracy"""
    
    def __init__(self):
        self.results = {
            "has_onlyfans": False,
            "onlyfans_urls": [],
            "detection_method": None,
            "errors": [],
            "debug_info": [],
            "phase_used": None
        }
    
    async def detect_onlyfans(self, bio_link: str) -> Dict:
        """Main detection method - ultimate HTTP approach"""
        self.results = {
            "has_onlyfans": False,
            "onlyfans_urls": [],
            "detection_method": None,
            "errors": [],
            "debug_info": [],
            "phase_used": None
        }
        
        try:
            # Phase 1: Fast direct detection (1-2 seconds)
            self.results["debug_info"].append("Starting Phase 1: Fast direct detection")
            if await self._phase1_fast_detection(bio_link):
                self.results["phase_used"] = "phase1_fast"
                self.results["debug_info"].append("Phase 1 successful - OnlyFans found quickly")
                return self.results
            
            # Phase 2: Enhanced detection with multiple strategies (3-5 seconds)
            self.results["debug_info"].append("Phase 1 found nothing - starting Phase 2: Enhanced detection")
            if await self._phase2_enhanced_detection(bio_link):
                self.results["phase_used"] = "phase2_enhanced"
                self.results["debug_info"].append("Phase 2 successful - OnlyFans found via enhanced methods")
                return self.results
            
            # Phase 3: Deep investigation (5-8 seconds)
            self.results["debug_info"].append("Phase 2 found nothing - starting Phase 3: Deep investigation")
            if await self._phase3_deep_investigation(bio_link):
                self.results["phase_used"] = "phase3_deep"
                self.results["debug_info"].append("Phase 3 successful - OnlyFans found via deep investigation")
                return self.results
            
            # All phases completed - no OnlyFans found
            self.results["phase_used"] = "all_phases_completed"
            self.results["debug_info"].append("All phases completed - no OnlyFans found")
                
        except Exception as e:
            self.results["errors"].append(f"Detection failed: {str(e)}")
            self.results["phase_used"] = "error"
        
        return self.results
    
    async def _phase1_fast_detection(self, bio_link: str) -> bool:
        """Phase 1: Fast direct detection (1-2 seconds)"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(bio_link)
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Look for OnlyFans URLs in HTML
                    of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', content, re.IGNORECASE)
                    
                    if of_urls:
                        # Filter out /files and /public (not creator profiles)
                        valid_urls = [url for url in of_urls if '/files' not in url and '/public' not in url]
                        if valid_urls:
                            self.results["has_onlyfans"] = True
                            self.results["onlyfans_urls"] = valid_urls
                            self.results["detection_method"] = "phase1_direct_html_scan"
                            self.results["debug_info"].append(f"Phase 1: Found {len(valid_urls)} direct OnlyFans links")
                            return True
                    
                    # Quick redirect chain check (limited for speed)
                    if await self._quick_redirect_check(client, bio_link, content):
                        return True
                            
        except Exception as e:
            self.results["errors"].append(f"Phase 1 failed: {str(e)}")
        
        return False
    
    async def _quick_redirect_check(self, client: httpx.AsyncClient, bio_link: str, content: str) -> bool:
        """Quick redirect check for Phase 1"""
        try:
            # Extract first 8 links for quick check
            all_links = re.findall(r'href=["\']([^"\']+)["\']', content)
            all_links.extend(re.findall(r'data-url=["\']([^"\']+)["\']', content))
            
            for link in all_links[:8]:  # Check first 8 links
                if not link or link.startswith('#') or link.startswith('mailto:'):
                    continue
                
                try:
                    if link.startswith('/'):
                        link = urljoin(bio_link, link)
                    
                    # Quick redirect check
                    final_url, _ = await self._follow_redirects_fast(client, link)
                    
                    if OF_REGEX.search(final_url) and '/files' not in final_url and '/public' not in final_url:
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = [final_url]
                        self.results["detection_method"] = "phase1_redirect_chain"
                        self.results["debug_info"].append(f"Phase 1: Found OnlyFans via quick redirect: {link} → {final_url}")
                        return True
                        
                except Exception:
                    continue
                    
        except Exception as e:
            self.results["errors"].append(f"Quick redirect check failed: {str(e)}")
        
        return False
    
    async def _phase2_enhanced_detection(self, bio_link: str) -> bool:
        """Phase 2: Enhanced detection with multiple strategies (3-5 seconds)"""
        try:
            # Try with different user agents and headers
            headers_list = [
                {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'},
                {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'},
                {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)'}
            ]
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                for headers in headers_list:
                    try:
                        response = await client.get(bio_link, headers=headers)
                        if response.status_code == 200:
                            content = response.text
                            
                            # Enhanced OnlyFans detection
                            if await self._enhanced_onlyfans_detection(content, bio_link, client):
                                return True
                                
                    except Exception:
                        continue
                
                # Try with different paths for common platforms
                if await self._try_common_paths(bio_link, client):
                    return True
                    
        except Exception as e:
            self.results["errors"].append(f"Phase 2 enhanced detection failed: {str(e)}")
        
        return False
    
    async def _phase3_deep_investigation(self, bio_link: str) -> bool:
        """Phase 3: Deep investigation (5-8 seconds)"""
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                # Get the page with mobile user agent (often shows different content)
                mobile_headers = {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                response = await client.get(bio_link, headers=mobile_headers)
                if response.status_code == 200:
                    content = response.text
                    
                    # Deep OnlyFans detection
                    if await self._deep_onlyfans_detection(content, bio_link, client):
                        return True
                
                # Try with JavaScript rendering hints
                js_headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                response = await client.get(bio_link, headers=js_headers)
                if response.status_code == 200:
                    content = response.text
                    
                    # Deep OnlyFans detection
                    if await self._deep_onlyfans_detection(content, bio_link, client):
                        return True
                    
        except Exception as e:
            self.results["errors"].append(f"Phase 3 deep investigation failed: {str(e)}")
        
        return False
    
    async def _enhanced_onlyfans_detection(self, content: str, base_url: str, client: httpx.AsyncClient) -> bool:
        """Enhanced OnlyFans detection with multiple strategies"""
        try:
            # Strategy 1: Direct OnlyFans URLs
            of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', content, re.IGNORECASE)
            valid_urls = [url for url in of_urls if '/files' not in url and '/public' not in url]
            if valid_urls:
                self.results["has_onlyfans"] = True
                self.results["onlyfans_urls"] = valid_urls
                self.results["detection_method"] = "phase2_direct_html_scan"
                self.results["debug_info"].append(f"Phase 2: Found {len(valid_urls)} direct OnlyFans links")
                return True
            
            # Strategy 2: JavaScript variables and data attributes
            js_patterns = [
                r'onlyfans\.com[^"\']*["\']',
                r'["\']([^"\']*onlyfans\.com[^"\']*)["\']',
                r'data-url=["\']([^"\']*onlyfans\.com[^"\']*)["\']',
                r'data-href=["\']([^"\']*onlyfans\.com[^"\']*)["\']',
                r'data-link=["\']([^"\']*onlyfans\.com[^"\']*)["\']',
                r'url\(["\']?([^"\')\s]*onlyfans\.com[^"\')\s]*)["\']?\)'
            ]
            
            for pattern in js_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if 'onlyfans.com' in match and '/files' not in match and '/public' not in match:
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = [match]
                        self.results["detection_method"] = "phase2_js_variable_scan"
                        self.results["debug_info"].append(f"Phase 2: Found OnlyFans via JS variable: {match}")
                        return True
            
            # Strategy 3: Enhanced redirect chain analysis
            if await self._enhanced_redirect_analysis(content, base_url, client):
                return True
                
        except Exception as e:
            self.results["errors"].append(f"Enhanced OnlyFans detection failed: {str(e)}")
        
        return False
    
    async def _deep_onlyfans_detection(self, content: str, base_url: str, client: httpx.AsyncClient) -> bool:
        """Deep OnlyFans detection for Phase 3"""
        try:
            # Strategy 1: Direct OnlyFans URLs
            of_urls = re.findall(r'https?://[^\s<>"\']*onlyfans\.com[^\s<>"\']*', content, re.IGNORECASE)
            valid_urls = [url for url in of_urls if '/files' not in url and '/public' not in url]
            if valid_urls:
                self.results["has_onlyfans"] = True
                self.results["onlyfans_urls"] = valid_urls
                self.results["detection_method"] = "phase3_direct_html_scan"
                self.results["debug_info"].append(f"Phase 3: Found {len(valid_urls)} direct OnlyFans links")
                return True
            
            # Strategy 2: Advanced JavaScript extraction
            js_advanced_patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*({[^}]*onlyfans[^}]*})',
                r'window\.__PRELOADED_STATE__\s*=\s*({[^}]*onlyfans[^}]*})',
                r'data-props\s*=\s*["\']([^"\']*onlyfans[^"\']*)["\']',
                r'data-state\s*=\s*["\']([^"\']*onlyfans[^"\']*)["\']'
            ]
            
            for pattern in js_advanced_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if 'onlyfans.com' in match and '/files' not in match and '/public' not in match:
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = [match]
                        self.results["detection_method"] = "phase3_js_advanced_scan"
                        self.results["debug_info"].append(f"Phase 3: Found OnlyFans via advanced JS: {match}")
                        return True
            
            # Strategy 3: Deep redirect chain analysis
            if await self._deep_redirect_analysis(content, base_url, client):
                return True
                
        except Exception as e:
            self.results["errors"].append(f"Deep OnlyFans detection failed: {str(e)}")
        
        return False
    
    async def _enhanced_redirect_analysis(self, content: str, base_url: str, client: httpx.AsyncClient) -> bool:
        """Enhanced redirect chain analysis for Phase 2"""
        try:
            # Extract more link patterns
            link_patterns = [
                r'href=["\']([^"\']+)["\']',
                r'data-url=["\']([^"\']+)["\']',
                r'data-href=["\']([^"\']+)["\']',
                r'data-link=["\']([^"\']+)["\']',
                r'url\(["\']?([^"\')\s]+)["\']?\)',
                r'["\']([^"\']*\.(?:png|jpg|jpeg|gif|svg|webp))["\']'
            ]
            
            all_links = []
            for pattern in link_patterns:
                matches = re.findall(pattern, content)
                all_links.extend(matches)
            
            # Check first 20 links (more than Phase 1)
            for link in all_links[:20]:
                if not link or link.startswith('#') or link.startswith('mailto:'):
                    continue
                
                try:
                    if link.startswith('/'):
                        link = urljoin(base_url, link)
                    
                    # Enhanced redirect following
                    final_url, chain = await self._follow_redirects_enhanced(client, link)
                    
                    if OF_REGEX.search(final_url) and '/files' not in final_url and '/public' not in final_url:
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = [final_url]
                        self.results["detection_method"] = "phase2_enhanced_redirect"
                        self.results["debug_info"].append(f"Phase 2: Found OnlyFans via enhanced redirect: {link} → {final_url}")
                        return True
                        
                except Exception:
                    continue
                    
        except Exception as e:
            self.results["errors"].append(f"Enhanced redirect analysis failed: {str(e)}")
        
        return False
    
    async def _deep_redirect_analysis(self, content: str, base_url: str, client: httpx.AsyncClient) -> bool:
        """Deep redirect chain analysis for Phase 3"""
        try:
            # Extract even more link patterns
            link_patterns = [
                r'href=["\']([^"\']+)["\']',
                r'data-url=["\']([^"\']+)["\']',
                r'data-href=["\']([^"\']+)["\']',
                r'data-link=["\']([^"\']+)["\']',
                r'data-src=["\']([^"\']+)["\']',
                r'src=["\']([^"\']+)["\']',
                r'url\(["\']?([^"\')\s]+)["\']?\)',
                r'["\']([^"\']*\.(?:png|jpg|jpeg|gif|svg|webp))["\']',
                r'["\']([^"\']*\.(?:css|js))["\']'
            ]
            
            all_links = []
            for pattern in link_patterns:
                matches = re.findall(pattern, content)
                all_links.extend(matches)
            
            # Check first 30 links (maximum coverage)
            for link in all_links[:30]:
                if not link or link.startswith('#') or link.startswith('mailto:'):
                    continue
                
                try:
                    if link.startswith('/'):
                        link = urljoin(base_url, link)
                    
                    # Deep redirect following
                    final_url, chain = await self._follow_redirects_deep(client, link)
                    
                    if OF_REGEX.search(final_url) and '/files' not in final_url and '/public' not in final_url:
                        self.results["has_onlyfans"] = True
                        self.results["onlyfans_urls"] = [final_url]
                        self.results["detection_method"] = "phase3_deep_redirect"
                        self.results["debug_info"].append(f"Phase 3: Found OnlyFans via deep redirect: {link} → {final_url}")
                        return True
                        
                except Exception:
                    continue
                    
        except Exception as e:
            self.results["errors"].append(f"Deep redirect analysis failed: {str(e)}")
        
        return False
    
    async def _try_common_paths(self, base_url: str, client: httpx.AsyncClient) -> bool:
        """Try common paths that might contain OnlyFans links"""
        try:
            common_paths = [
                '/links',
                '/social',
                '/socials',
                '/connect',
                '/bio',
                '/profile',
                '/about',
                '/contact',
                '/links.html',
                '/social.html'
            ]
            
            for path in common_paths:
                try:
                    test_url = urljoin(base_url, path)
                    response = await client.get(test_url, timeout=10.0)
                    if response.status_code == 200:
                        if await self._enhanced_onlyfans_detection(response.text, test_url, client):
                            return True
                except Exception:
                    continue
                    
        except Exception as e:
            self.results["errors"].append(f"Common paths check failed: {str(e)}")
        
        return False
    
    async def _follow_redirects_fast(self, client: httpx.AsyncClient, url: str, max_redirects: int = 3) -> Tuple[str, List[str]]:
        """Fast redirect following for Phase 1"""
        chain = [url]
        current = url
        
        for _ in range(max_redirects):
            try:
                resp = await client.head(current, follow_redirects=False, timeout=5.0)
                if resp.status_code in (301, 302, 303, 307, 308):
                    location = resp.headers.get('location')
                    if location:
                        if location.startswith('/'):
                            current = urljoin(current, location)
                        else:
                            current = location
                        chain.append(current)
                    else:
                        break
                else:
                    break
            except Exception:
                break
        
        return current, chain
    
    async def _follow_redirects_enhanced(self, client: httpx.AsyncClient, url: str, max_redirects: int = 5) -> Tuple[str, List[str]]:
        """Enhanced redirect following for Phase 2"""
        chain = [url]
        current = url
        
        for _ in range(max_redirects):
            try:
                resp = await client.head(current, follow_redirects=False, timeout=8.0)
                if resp.status_code in (301, 302, 303, 307, 308):
                    location = resp.headers.get('location')
                    if location:
                        if location.startswith('/'):
                            current = urljoin(current, location)
                        else:
                            current = location
                        chain.append(current)
                    else:
                        break
                else:
                    break
            except Exception:
                break
        
        return current, chain
    
    async def _follow_redirects_deep(self, client: httpx.AsyncClient, url: str, max_redirects: int = 7) -> Tuple[str, List[str]]:
        """Deep redirect following for Phase 3"""
        chain = [url]
        current = url
        
        for _ in range(max_redirects):
            try:
                resp = await client.head(current, follow_redirects=False, timeout=10.0)
                if resp.status_code in (301, 302, 303, 307, 308):
                    location = resp.headers.get('location')
                    if location:
                        if location.startswith('/'):
                            current = urljoin(current, location)
                        else:
                            current = location
                        chain.append(current)
                    else:
                        break
                else:
                    break
            except Exception:
                break
        
        return current, chain

async def detect_onlyfans_in_bio_link(bio_link: str, headless: bool = True) -> Dict:
    """Main function to detect OnlyFans in a bio link"""
    detector = UltimateHTTPDetector()
    return await detector.detect_onlyfans(bio_link)

def main():
    """Command line interface for n8n integration"""
    if len(sys.argv) != 2:
        print("Usage: python onlyfans_detector_http_ultimate.py <bio_link>")
        print("Example: python onlyfans_detector_http_ultimate.py 'https://link.me/username'")
        sys.exit(1)
    
    bio_link = sys.argv[1]
    
    # Run detection
    result = asyncio.run(detect_onlyfans_in_bio_link(bio_link))
    
    # Output JSON result for n8n
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

