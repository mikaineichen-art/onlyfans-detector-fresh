#!/usr/bin/env python3
"""
Railway-Specific Playwright Fix
Handles missing Chrome dependencies on Railway
"""

import subprocess
import sys
import os
import platform

def install_playwright_railway():
    """Install Playwright with Railway-specific fixes"""
    print("🚀 Installing Playwright for Railway...")
    
    try:
        # Step 1: Install Playwright browsers
        print("📦 Installing Playwright browsers...")
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Playwright browsers installed successfully")
        else:
            print(f"⚠️  Browser installation failed: {result.stderr}")
            return False
        
        # Step 2: Try to install system dependencies
        print("🔧 Installing system dependencies...")
        try:
            # Try the standard playwright install-deps
            result2 = subprocess.run([
                sys.executable, "-m", "playwright", "install-deps"
            ], capture_output=True, text=True, timeout=120)
            
            if result2.returncode == 0:
                print("✅ System dependencies installed successfully")
            else:
                print(f"⚠️  Standard dependency installation failed: {result2.stderr}")
                print("🔄 Trying alternative approach...")
                
                # Alternative: Try to install specific packages
                if platform.system() == "Linux":
                    print("🐧 Linux detected, trying apt packages...")
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
                            result3 = subprocess.run([
                                "apt-get", "install", "-y", package
                            ], capture_output=True, text=True, timeout=30)
                            if result3.returncode == 0:
                                print(f"✅ Installed {package}")
                            else:
                                print(f"⚠️  Failed to install {package}")
                        except Exception as e:
                            print(f"⚠️  Could not install {package}: {e}")
                
        except Exception as e:
            print(f"⚠️  Dependency installation failed: {e}")
        
        # Step 3: Verify installation
        print("🔍 Verifying Playwright installation...")
        try:
            import playwright
            print(f"✅ Playwright imported successfully: {playwright.__version__}")
            
            # Try to launch a browser
            from playwright.async_api import async_playwright
            print("✅ Playwright async API imported successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Playwright verification failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

def test_playwright_launch():
    """Test if Playwright can actually launch a browser"""
    print("\n🧪 Testing Playwright browser launch...")
    
    try:
        import asyncio
        from playwright.async_api import async_playwright
        
        async def test_launch():
            async with async_playwright() as p:
                # Try to launch with minimal args
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
                
                context = await browser.new_context()
                page = await context.new_page()
                
                # Test a simple page load
                await page.goto("https://example.com", timeout=10000)
                title = await page.title()
                
                await browser.close()
                return title
                
        # Run the test
        result = asyncio.run(test_launch())
        print(f"✅ Browser test successful! Page title: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Railway Playwright Fix")
    print("=" * 50)
    
    # Install Playwright
    if install_playwright_railway():
        print("\n✅ Playwright installation completed!")
        
        # Test the installation
        if test_playwright_launch():
            print("🎉 Playwright is working perfectly!")
        else:
            print("⚠️  Installation succeeded but browser launch failed")
    else:
        print("❌ Playwright installation failed")
        print("💡 You may need to use HTTP-only detection mode")

