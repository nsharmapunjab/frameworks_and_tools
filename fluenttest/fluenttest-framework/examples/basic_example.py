#!/usr/bin/env python3
# FluentTest Basic Example v1.0
# =============================
# This example demonstrates basic usage of FluentTest for Android automation.

import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from appium import webdriver
from appium.options.android import UiAutomator2Options
from fluenttest import FluentDriver


def setup_driver():
    """Setup Appium driver for Android"""
    print("Setting up Appium driver...")
    
    capabilities = {
        'platformName': 'Android',
        'deviceName': 'emulator-5554',
        'appPackage': 'com.android.settings',
        'appActivity': '.Settings',
        'automationName': 'UiAutomator2',
        'noReset': True,
        'newCommandTimeout': 300
    }
    
    try:
        options = UiAutomator2Options().load_capabilities(capabilities)
        driver = webdriver.Remote('http://localhost:4723', options=options)
        print("Driver setup successful!")
        return driver
    except Exception as e:
        print(f"Driver setup failed: {e}")
        print("Make sure Appium server is running: appium")
        return None


def main():
    """Main example function"""
    print("FluentTest Basic Example v2.0")
    print("=" * 40)
    
    # Setup driver
    appium_driver = setup_driver()
    if not appium_driver:
        return
    
    # Initialize FluentTest
    fluent = FluentDriver(appium_driver)
    print("FluentTest initialized!")
    
    try:
        print("\nTesting natural language queries...")
        
        # Test 1: Basic element finding
        print("\nTest 1: Finding WiFi settings...")
        wifi_element = fluent.find("WiFi")
        if wifi_element:
            print("Found WiFi settings!")
            wifi_element.click()
            time.sleep(2)
        else:
            print("WiFi settings not found, trying alternative...")
            network_element = fluent.find("Network")
            if network_element:
                print("Found Network settings!")
                network_element.click()
                time.sleep(2)
        
        # Test 2: Natural language click
        print("\nTest 2: Using natural language click...")
        success = fluent.click("Display")
        if success:
            print("Successfully clicked display settings!")
            time.sleep(2)
        else:
            print("Could not click display settings")
        
        # Test 3: Check element presence
        print("\nTest 3: Checking element presence...")
        is_present = fluent.is_present("Settings")
        print(f"Settings element present: {is_present}")
        
        print("\nAll tests completed!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        
    finally:
        print("\nClosing driver...")
        appium_driver.quit()
        print("Driver closed successfully!")


if __name__ == "__main__":
    main()
