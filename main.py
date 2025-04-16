#!/usr/bin/env python3
"""
UniFi Monitor Snapshot Script
Uses Selenium instead of Playwright for better compatibility with WebRTC streams
"""

import os
import time
import shutil
import pathlib
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, StaleElementReferenceException

# Configuration
TARGET_URL = "https://monitor.ui.com/21835928-0b07-459b-8600-096cb7ef9709"
INTERVAL_SECONDS = 2  # Time between snapshots
COLLECT_DIR = pathlib.Path("/home/samuel-penido/dev/shud/coletar")  # Where to save snapshots
DOWNLOADS_DIR = pathlib.Path(os.path.expanduser("~/Downloads"))  # Default downloads location
MAX_RUNTIME_SECONDS = 3600  # 1 hour maximum runtime

# Snapshot button selectors to try (in order of preference)
SELECTORS = [
    "svg[viewBox='0 0 25 25']",
    "svg path[d^='M15.9237 4.652']",
    ".css-1fvzjsv"
]

def setup_chrome():
    """Set up Chrome with appropriate options for media streaming."""
    options = Options()
    options.add_argument("--start-maximized")  # Start maximized
    options.add_argument("--disable-infobars")  # Disable infobars
    options.add_argument("--disable-extensions")  # Disable extensions
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    
    # Media streaming settings
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    options.add_argument("--use-fake-ui-for-media-stream")  # Auto-accept media permissions
    
    # Create chrome service
    service = Service()
    
    # Create driver
    driver = webdriver.Chrome(service=service, options=options)
    
    # Set download preferences
    driver.execute_cdp_cmd("Page.setDownloadBehavior", {
        "behavior": "allow",
        "downloadPath": str(DOWNLOADS_DIR)
    })
    
    return driver

def find_latest_download():
    """Find the most recent file in the downloads directory."""
    files = list(DOWNLOADS_DIR.glob("*.jpg")) + list(DOWNLOADS_DIR.glob("*.png"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def click_button_safely(driver, selector):
    """Find and click a button using the given selector, handling potential stale elements."""
    try:
        # Find the element fresh each time instead of reusing a reference
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        element.click()
        return True
    except StaleElementReferenceException:
        # Try again if the element was stale
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
            return True
        except Exception as e:
            print(f"Error clicking button (retry): {e}")
            return False
    except Exception as e:
        print(f"Error clicking button: {e}")
        return False

def find_working_selector(driver):
    """Try each selector and return the first one that works."""
    for selector in SELECTORS:
        try:
            print(f"Looking for snapshot button with selector: {selector}")
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            print(f"Found snapshot button with selector: {selector}")
            return selector
        except TimeoutException:
            print(f"Button not found with selector: {selector}")
    return None

def main():
    """Main function to run the snapshot automation."""
    # Ensure collection directory exists
    COLLECT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Snapshots will be saved to: {COLLECT_DIR}")
    
    driver = setup_chrome()
    start_time = time.time()
    snapshot_count = 0
    latest_file_before = find_latest_download()
    
    try:
        # Navigate to the URL
        print(f"Navigating to: {TARGET_URL}")
        driver.get(TARGET_URL)
        
        # Wait for the page to load
        print("Waiting for page to load (30 seconds)...")
        time.sleep(30)
        
        # Find a working selector
        working_selector = find_working_selector(driver)
        
        if not working_selector:
            print("Error: Could not find snapshot button with any selector. Exiting.")
            return
        
        # Main loop
        while time.time() - start_time < MAX_RUNTIME_SECONDS:
            try:
                # Take a snapshot - find and click the button fresh each time
                print(f"Taking snapshot #{snapshot_count+1}...")
                
                if click_button_safely(driver, working_selector):
                    # Wait for download
                    time.sleep(3)
                    
                    # Check for new downloads
                    latest_file = find_latest_download()
                    if latest_file and (not latest_file_before or latest_file.stat().st_mtime > latest_file_before.stat().st_mtime):
                        # New file found!
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        destination = COLLECT_DIR / f"snapshot_{timestamp}_{snapshot_count}{latest_file.suffix}"
                        
                        # Copy the file (don't move - we'll use it for comparison next time)
                        shutil.copy2(latest_file, destination)
                        print(f"Saved snapshot to: {destination}")
                        
                        # Update reference
                        latest_file_before = latest_file
                        snapshot_count += 1
                    else:
                        print("No new download detected.")
                else:
                    print("Failed to click snapshot button. Trying to find it again...")
                    working_selector = find_working_selector(driver)
                    if not working_selector:
                        print("Could not recover button. Exiting.")
                        break
                
                # Wait for next interval
                print(f"Waiting {INTERVAL_SECONDS} seconds...")
                time.sleep(INTERVAL_SECONDS)
                
            except KeyboardInterrupt:
                print("\nScript interrupted by user. Exiting.")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                # Try to find the button again without reloading
                print("Trying to find snapshot button again...")
                working_selector = find_working_selector(driver)
                if not working_selector:
                    print("Could not recover button. Exiting.")
                    break
        
        print(f"Script completed after {snapshot_count} snapshots.")
    
    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    main()
