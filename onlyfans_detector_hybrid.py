#!/usr/bin/env python3
"""
Hybrid OnlyFans Detector for n8n Integration
Phase 1: Fast HTTP detection (1-2 seconds)
Phase 2: Deep Puppeteer investigation (5-25 seconds) - only if Phase 1 finds nothing
"""

import asyncio
import json
import re
import sys
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import httpx
from pyppeteer import launch

# OnlyFans detection regex
OF_REGEX = re.compile(r"onlyfans\.com", re.IGNORECASE)

class HybridOnlyFansDetector:
    """Hybrid detector with fast HTTP + deep investigation"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.results = {
            "has_onlyfans": False,
            "onlyfans_urls": [],
            "detection_method": None,
            "errors": [],
            "debug_info": [],
            "phase_used": None
        }
    
    async def detect_onlyfans(self, bio_link: str) -> Dict:
        """Main detection method - hybrid approach"""
        self.results = {
            "has_onlyfans": False,
            "onlyfans_urls": [],
            "detection_method": None,
            "errors": [],
            "debug_info": [],
            "phase_used": None
        }
        
        try:
            # Phase 1: Fast HTTP detection (1-2 seconds)
            self.results["debug_info"].append("Starting Phase 1: Fast HTTP detection")
            if await self._phase1_fast_detection(bio_link):
                self.results["phase_used"] = "phase1_fast"
                self.results["debug_info"].append("Phase 1 successful - OnlyFans found quickly")
                return self.results
            
            # Phase 2: Deep investigation (5-25 seconds) - only if Phase 1 found nothing
            self.results["debug_info"].append("Phase 1 found nothing - starting Phase 2: Deep investigation")
            if await self._phase2_deep_investigation(bio_link):
                self.results["phase_used"] = "phase2_deep"
                self.results["debug_info"].append("Phase 2 successful - OnlyFans found via investigation")
                return self.results
            
            # Neither phase found OnlyFans
            self.results["phase_used"] = "both_phases_completed"
            self.results["debug_info"].append("Both phases completed - no OnlyFans found")
                
        except Exception as e:
            self.results["errors"].append(f"Detection failed: {str(e)}")
            self.results["phase_used"] = "error"
        
        return self.results
    
    async def _phase1_fast_detection(self, bio_link: str) -> bool:
        """Phase 1: Fast HTTP detection (1-2 seconds)"""
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
            # Extract first 5 links for quick check
            all_links = re.findall(r'href=["\']([^"\']+)["\']', content)
            all_links.extend(re.findall(r'data-url=["\']([^"\']+)["\']', content))
            
            for link in all_links[:5]:  # Limit for speed
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
    
    async def _phase2_deep_investigation(self, bio_link: str) -> bool:
        """Phase 2: Deep Puppeteer investigation (5-25 seconds)"""
        try:
            # Launch Puppeteer with Heroku-compatible options
            browser = await launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--single-process',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--memory-pressure-off',
                    '--max_old_space_size=4096'
                ]
            )
            
            page = await browser.newPage()
            
            # Set timeout for Phase 2 (25 seconds total)
            page.setDefaultTimeout(25000)
            
            # Track redirects
            onlyfans_redirects = []
            
            # Listen for redirects
            page.on('response', lambda response: self._handle_response(response, onlyfans_redirects))
            
            try:
                # Load the bio link page
                await page.goto(bio_link, {'waitUntil': 'domcontentloaded', 'timeout': 15000})
                await page.waitFor(3000)  # Wait for JS to load
                
                # Accept cookies if present
                await self._handle_cookies_and_overlays(page)
                
                # Platform-specific deep parsing
                if await self._platform_specific_parsing(page, bio_link):
                    await browser.close()
                    return True
                
                # Get all links from the page (including dynamic content)
                all_links = await self._extract_all_links_deep(page, bio_link)
                
                # Check for OnlyFans in extracted links
                of_links = [link for link in all_links if OF_REGEX.search(link) and '/files' not in link and '/public' not in link]
                
                if of_links:
                    self.results["has_onlyfans"] = True
                    self.results["onlyfans_urls"] = of_links
                    self.results["detection_method"] = "phase2_deep_link_extraction"
                    self.results["debug_info"].append(f"Phase 2: Found {len(of_links)} OnlyFans links via deep extraction")
                    await browser.close()
                    return True
                
                # Try interactive clicking to trigger redirects
                if await self._interactive_click_investigation(page, bio_link):
                    await browser.close()
                    return True
                
                # Check if we captured any redirects
                if onlyfans_redirects:
                    self.results["has_onlyfans"] = True
                    self.results["onlyfans_urls"] = onlyfans_redirects
                    self.results["detection_method"] = "phase2_redirect_capture"
                    self.results["debug_info"].append(f"Phase 2: Captured {len(onlyfans_redirects)} OnlyFans redirects")
                    await browser.close()
                    return True
                
            except Exception as e:
                self.results["errors"].append(f"Phase 2 page interaction failed: {str(e)}")
            finally:
                await browser.close()
                
        except Exception as e:
            self.results["errors"].append(f"Phase 2 setup failed: {str(e)}")
        
        return False
    
    async def _handle_cookies_and_overlays(self, page):
        """Handle cookies and overlays that might block content"""
        try:
            # Common cookie/overlay selectors
            selectors = [
                "button:has-text('Accept All')",
                "button:has-text('Accept')",
                "button:has-text('OK')",
                "button:has-text('Got it')",
                "button:has-text('Continue')",
                "button:has-text('Close')",
                ".cookie-accept",
                ".overlay-close"
            ]
            
            for selector in selectors:
                try:
                    element = await page.querySelector(selector)
                    if element:
                        await element.click()
                        await page.waitFor(1000)
                        break
                except:
                    continue
        except:
            pass
    
    async def _platform_specific_parsing(self, page, bio_link: str) -> bool:
        """Platform-specific deep parsing strategies"""
        try:
            domain = urlparse(bio_link).netloc.lower()
            
            # Linktree specific parsing
            if 'linktr.ee' in domain:
                return await self._parse_linktree_deep(page)
            
            # AllMyLinks specific parsing
            elif 'allmylinks.com' in domain:
                return await self._parse_allmylinks_deep(page)
            
            # Beacons specific parsing
            elif 'beacons.ai' in domain:
                return await self._parse_beacons_deep(page)
            
            # Link.me specific parsing
            elif 'link.me' in domain:
                return await self._parse_linkme_deep(page)
            
            # Generic deep parsing for other platforms
            else:
                return await self._parse_generic_deep(page)
                
        except Exception as e:
            self.results["errors"].append(f"Platform-specific parsing failed: {str(e)}")
        
        return False
    
    async def _parse_linktree_deep(self, page) -> bool:
        """Deep parsing for Linktree"""
        try:
            # Wait for dynamic content
            await page.waitFor(2000)
            
            # Look for hidden/expanded content
            expanded_selectors = [
                "[data-testid*='LinkButton']",
                ".link-button",
                ".social-link"
            ]
            
            for selector in expanded_selectors:
                elements = await page.querySelectorAll(selector)
                for element in elements[:20]:
                    try:
                        href = await page.evaluate('el => el.href', element)
                        if href and 'onlyfans.com' in href.lower() and '/files' not in href:
                            self.results["has_onlyfans"] = True
                            self.results["onlyfans_urls"] = [href]
                            self.results["detection_method"] = "phase2_linktree_deep"
                            self.results["debug_info"].append("Phase 2: Found OnlyFans via Linktree deep parsing")
                            return True
                    except:
                        continue
            
            # Try clicking "Show more" buttons if they exist
            show_more_selectors = [
                "button:has-text('Show more')",
                "button:has-text('Load more')",
                ".show-more"
            ]
            
            for selector in show_more_selectors:
                try:
                    button = await page.querySelector(selector)
                    if button:
                        await button.click()
                        await page.waitFor(2000)
                        # Re-check for OnlyFans links after expansion
                        return await self._parse_linktree_deep(page)
                except:
                    continue
                    
        except Exception as e:
            self.results["errors"].append(f"Linktree deep parsing failed: {str(e)}")
        
        return False
    
    async def _parse_allmylinks_deep(self, page) -> bool:
        """Deep parsing for AllMyLinks"""
        try:
            # Wait for dynamic content
            await page.waitFor(3000)
            
            # Look for dynamically loaded links
            link_selectors = [
                "a[href*='onlyfans']",
                ".link-item a",
                ".social-link a"
            ]
            
            for selector in link_selectors:
                elements = await page.querySelectorAll(selector)
                for element in elements:
                    try:
                        href = await page.evaluate('el => el.href', element)
                        if href and 'onlyfans.com' in href.lower() and '/files' not in href:
                            self.results["has_onlyfans"] = True
                            self.results["onlyfans_urls"] = [href]
                            self.results["detection_method"] = "phase2_allmylinks_deep"
                            self.results["debug_info"].append("Phase 2: Found OnlyFans via AllMyLinks deep parsing")
                            return True
                    except:
                        continue
                        
        except Exception as e:
            self.results["errors"].append(f"AllMyLinks deep parsing failed: {str(e)}")
        
        return False
    
    async def _parse_beacons_deep(self, page) -> bool:
        """Deep parsing for Beacons"""
        try:
            # Wait for dynamic content
            await page.waitFor(3000)
            
            # Look for Beacons-specific elements
            link_selectors = [
                "a[href*='onlyfans']",
                ".beacon-link",
                ".social-link"
            ]
            
            for selector in link_selectors:
                elements = await page.querySelectorAll(selector)
                for element in elements:
                    try:
                        href = await page.evaluate('el => el.href', element)
                        if href and 'onlyfans.com' in href.lower() and '/files' not in href:
                            self.results["has_onlyfans"] = True
                            self.results["onlyfans_urls"] = [href]
                            self.results["detection_method"] = "phase2_beacons_deep"
                            self.results["debug_info"].append("Phase 2: Found OnlyFans via Beacons deep parsing")
                            return True
                    except:
                        continue
                        
        except Exception as e:
            self.results["errors"].append(f"Beacons deep parsing failed: {str(e)}")
        
        return False
    
    async def _parse_linkme_deep(self, page) -> bool:
        """Deep parsing for Link.me"""
        try:
            # Wait for dynamic content
            await page.waitFor(3000)
            
            # Look for Link.me specific elements
            link_selectors = [
                "a[href*='onlyfans']",
                ".link-item",
                ".social-link"
            ]
            
            for selector in link_selectors:
                elements = await page.querySelectorAll(selector)
                for element in elements:
                    try:
                        href = await page.evaluate('el => el.href', element)
                        if href and 'onlyfans.com' in href.lower() and '/files' not in href:
                            self.results["has_onlyfans"] = True
                            self.results["onlyfans_urls"] = [href]
                            self.results["detection_method"] = "phase2_linkme_deep"
                            self.results["debug_info"].append("Phase 2: Found OnlyFans via Link.me deep parsing")
                            return True
                    except:
                        continue
                        
        except Exception as e:
            self.results["errors"].append(f"Link.me deep parsing failed: {str(e)}")
        
        return False
    
    async def _parse_generic_deep(self, page) -> bool:
        """Generic deep parsing for unknown platforms"""
        try:
            # Wait for dynamic content
            await page.waitFor(3000)
            
            # Look for any OnlyFans links
            link_selectors = [
                "a[href*='onlyfans']",
                "[data-url*='onlyfans']",
                "[data-href*='onlyfans']"
            ]
            
            for selector in link_selectors:
                elements = await page.querySelectorAll(selector)
                for element in elements:
                    try:
                        href = await page.evaluate('el => el.href || el.getAttribute("data-url") || el.getAttribute("data-href")', element)
                        if href and 'onlyfans.com' in href.lower() and '/files' not in href:
                            self.results["has_onlyfans"] = True
                            self.results["onlyfans_urls"] = [href]
                            self.results["detection_method"] = "phase2_generic_deep"
                            self.results["debug_info"].append("Phase 2: Found OnlyFans via generic deep parsing")
                            return True
                    except:
                        continue
                        
        except Exception as e:
            self.results["errors"].append(f"Generic deep parsing failed: {str(e)}")
        
        return False
    
    async def _extract_all_links_deep(self, page, base_url: str) -> List[str]:
        """Extract all links including dynamic content"""
        links = []
        
        try:
            # Get all href attributes
            hrefs = await page.evaluate('''
                () => {
                    const anchors = document.querySelectorAll('a[href]');
                    return Array.from(anchors).map(a => a.href);
                }
            ''')
            
            # Get all data attributes
            data_urls = await page.evaluate('''
                () => {
                    const elements = document.querySelectorAll('[data-url], [data-href], [data-link]');
                    return Array.from(elements).map(el => 
                        el.getAttribute('data-url') || el.getAttribute('data-href') || el.getAttribute('data-link')
                    ).filter(url => url);
                }
            ''')
            
            # Get JavaScript variables (basic extraction)
            js_urls = await page.evaluate('''
                () => {
                    const scripts = document.querySelectorAll('script');
                    const urls = [];
                    scripts.forEach(script => {
                        const content = script.textContent || script.innerHTML;
                        const matches = content.match(/https?:\/\/[^\s<>"\']*onlyfans\.com[^\s<>"\']*/gi);
                        if (matches) urls.push(...matches);
                    });
                    return urls;
                }
            ''')
            
            # Combine and filter
            all_urls = hrefs + data_urls + js_urls
            for url in all_urls:
                if url and url.startswith('http'):
                    links.append(url)
                elif url and url.startswith('/'):
                    links.append(urljoin(base_url, url))
                    
        except Exception as e:
            self.results["errors"].append(f"Deep link extraction failed: {str(e)}")
        
        return links
    
    async def _interactive_click_investigation(self, page, base_url: str) -> bool:
        """Interactive clicking to trigger redirects"""
        try:
            # Common button selectors that might lead to OnlyFans
            click_selectors = [
                'button',
                '.btn',
                '.button',
                '[role="button"]',
                'a[href="#"]',
                '.social-link',
                '.profile-link'
            ]
            
            for selector in click_selectors:
                try:
                    elements = await page.querySelectorAll(selector)
                    for element in elements[:10]:  # Check first 10 elements
                        try:
                            # Check if element has text that might indicate OnlyFans
                            text = await page.evaluate('el => el.textContent', element)
                            if text and any(keyword in text.lower() for keyword in ['onlyfans', 'of', 'premium', 'exclusive']):
                                await element.click()
                                await page.waitFor(3000)
                                
                                # Check if we got redirected to OnlyFans
                                current_url = page.url
                                if OF_REGEX.search(current_url) and '/files' not in current_url and '/public' not in current_url:
                                    self.results["has_onlyfans"] = True
                                    self.results["onlyfans_urls"] = [current_url]
                                    self.results["detection_method"] = "phase2_interactive_click"
                                    self.results["debug_info"].append(f"Phase 2: Found OnlyFans via click: {text}")
                                    return True
                                
                                # Go back to original page
                                await page.goto(base_url, {'waitUntil': 'domcontentloaded'})
                                
                        except Exception:
                            continue
                            
                except Exception:
                    continue
                    
        except Exception as e:
            self.results["errors"].append(f"Interactive click investigation failed: {str(e)}")
        
        return False
    
    def _handle_response(self, response, onlyfans_redirects):
        """Handle response events to capture redirects"""
        try:
            if response.status >= 300 and response.status < 400:
                location = response.headers.get('location', '')
                if 'onlyfans.com' in location.lower() and '/files' not in location:
                    onlyfans_redirects.append(location)
        except:
            pass
    
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

async def detect_onlyfans_in_bio_link(bio_link: str, headless: bool = True) -> Dict:
    """Main function to detect OnlyFans in a bio link"""
    detector = HybridOnlyFansDetector(headless=headless)
    return await detector.detect_onlyfans(bio_link)

def main():
    """Command line interface for n8n integration"""
    if len(sys.argv) != 2:
        print("Usage: python onlyfans_detector_hybrid.py <bio_link>")
        print("Example: python onlyfans_detector_hybrid.py 'https://link.me/username'")
        sys.exit(1)
    
    bio_link = sys.argv[1]
    
    # Run detection
    result = asyncio.run(detect_onlyfans_in_bio_link(bio_link))
    
    # Output JSON result for n8n
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
