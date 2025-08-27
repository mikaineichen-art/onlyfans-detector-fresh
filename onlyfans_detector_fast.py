#!/usr/bin/env python3
"""
Fast OnlyFans Detector for n8n Integration
Detects OnlyFans links in bio landing pages using only HTTP requests
Optimized for speed and reliability on Heroku
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

class OnlyFansDetector:
    """Fast OnlyFans detector using HTTP requests only"""
    
    def __init__(self):
        self.results = {
            "has_onlyfans": False,
            "onlyfans_urls": [],
            "detection_method": None,
            "errors": [],
            "debug_info": []
        }
    
    async def detect_onlyfans(self, bio_link: str) -> Dict:
        """Main detection method - optimized for speed"""
        self.results = {
            "has_onlyfans": False,
            "onlyfans_urls": [],
            "detection_method": None,
            "errors": [],
            "debug_info": []
        }
        
        try:
            # Method 1: Fast direct link check
            if await self._check_direct_links(bio_link):
                return self.results
            
            # Method 2: Quick redirect chain analysis
            if await self._check_redirect_chains(bio_link):
                return self.results
                
        except Exception as e:
            self.results["errors"].append(f"Detection failed: {str(e)}")
        
        return self.results
    
    async def _check_direct_links(self, bio_link: str) -> bool:
        """Fast check for direct OnlyFans links in the page HTML"""
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
                            self.results["detection_method"] = "direct_html_scan"
                            self.results["debug_info"].append(f"Found {len(valid_urls)} direct OnlyFans links")
                            return True
                            
        except Exception as e:
            self.results["errors"].append(f"Direct link check failed: {str(e)}")
        
        return False
    
    async def _check_redirect_chains(self, bio_link: str) -> bool:
        """Fast redirect chain analysis for OnlyFans destinations"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Get all links from the page first
                response = await client.get(bio_link)
                if response.status_code == 200:
                    content = response.text
                    
                    # Extract all links quickly
                    all_links = re.findall(r'href=["\']([^"\']+)["\']', content)
                    all_links.extend(re.findall(r'data-url=["\']([^"\']+)["\']', content))
                    
                    # Check first 10 links for redirects (limit for speed)
                    for link in all_links[:10]:
                        if not link or link.startswith('#') or link.startswith('mailto:'):
                            continue
                        
                        try:
                            if link.startswith('/'):
                                link = urljoin(bio_link, link)
                            
                            # Follow redirects quickly
                            final_url, _ = await self._follow_redirects_fast(client, link)
                            
                            if OF_REGEX.search(final_url) and '/files' not in final_url and '/public' not in final_url:
                                self.results["has_onlyfans"] = True
                                self.results["onlyfans_urls"] = [final_url]
                                self.results["detection_method"] = "redirect_chain"
                                self.results["debug_info"].append(f"Found OnlyFans via redirect: {link} → {final_url}")
                                return True
                                
                        except Exception:
                            continue
                            
        except Exception as e:
            self.results["errors"].append(f"Redirect chain check failed: {str(e)}")
        
        return False
    
    async def _follow_redirects_fast(self, client: httpx.AsyncClient, url: str, max_redirects: int = 3) -> Tuple[str, List[str]]:
        """Fast redirect following with shorter timeout"""
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
    detector = OnlyFansDetector()
    return await detector.detect_onlyfans(bio_link)

def main():
    """Command line interface for n8n integration"""
    if len(sys.argv) != 2:
        print("Usage: python onlyfans_detector_fast.py <bio_link>")
        print("Example: python onlyfans_detector_fast.py 'https://link.me/username'")
        sys.exit(1)
    
    bio_link = sys.argv[1]
    
    # Run detection
    result = asyncio.run(detect_onlyfans_in_bio_link(bio_link))
    
    # Output JSON result for n8n
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

