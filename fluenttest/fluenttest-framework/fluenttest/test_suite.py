# FluentTest Test Suite
# ====================
# Comprehensive test framework for natural language UI automation.

import unittest
import time
import logging
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
import json
from datetime import datetime

from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import WebDriverException

from .nl_ui_locator import FluentDriver
from .runtime_parser import QueryParser

logger = logging.getLogger(__name__)


class FluentTestSuite:
    """Complete test suite using natural language UI automation"""
    
    def __init__(self, app_package: str, app_activity: str, device_name: str = "emulator-5554"):
        self.app_package = app_package
        self.app_activity = app_activity
        self.device_name = device_name
        self.driver = None
        self.fluent = None
        self.parser = QueryParser()
        self.test_results = []
        
        # Test configuration
        self.capabilities = {
            'platformName': 'Android',
            'deviceName': device_name,
            'appPackage': app_package,
            'appActivity': app_activity,
            'automationName': 'UiAutomator2',
            'noReset': True,
            'fullReset': False,
            'newCommandTimeout': 300,
            'autoGrantPermissions': True
        }
    
    def setup(self):
        """Initialize Appium driver and FluentTest"""
        try:
            options = UiAutomator2Options().load_capabilities(self.capabilities)
            self.driver = webdriver.Remote('http://localhost:4723', options=options)
            self.fluent = FluentDriver(self.driver)
            
            logger.info("FluentTest setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False
    
    def teardown(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver closed")
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")
    
    @contextmanager
    def test_context(self, test_name: str):
        """Context manager for individual tests"""
        start_time = time.time()
        test_result = {
            'test_name': test_name,
            'start_time': datetime.now().isoformat(),
            'success': False,
            'error': None,
            'duration': 0,
            'queries_used': []
        }
        
        try:
            logger.info(f"Starting test: {test_name}")
            yield test_result
            test_result['success'] = True
            logger.info(f"Test passed: {test_name}")
            
        except Exception as e:
            test_result['error'] = str(e)
            test_result['success'] = False
            logger.error(f"Test failed: {test_name} - {e}")
        
        finally:
            test_result['duration'] = time.time() - start_time
            self.test_results.append(test_result)
    
    def execute_query(self, query: str) -> bool:
        """Execute natural language query"""
        try:
            parsed = self.parser.parse(query)
            logger.info(f"Executing: {query}")
            
            if parsed.action == 'click':
                return self.fluent.click(query)
            elif parsed.action == 'type':
                if parsed.target_element['text_content']:
                    text = parsed.target_element['text_content'][0]
                    field_query = query.split('in')[-1].strip() if 'in' in query else 'input field'
                    return self.fluent.type_text(text, field_query)
            elif parsed.action == 'wait':
                element = self.fluent.wait_for(query)
                return element is not None
            elif parsed.action == 'verify':
                return self.fluent.is_present(query)
            else:
                # Default to click
                return self.fluent.click(query)
                
        except Exception as e:
            logger.error(f"Error executing query '{query}': {e}")
            return False
    
    def run_login_test(self, username: str, password: str):
        """Example login test"""
        with self.test_context("Login Test") as test_result:
            queries = [
                f'type "{username}" in username field',
                f'type "{password}" in password field',
                'click login button'
            ]
            
            for query in queries:
                test_result['queries_used'].append(query)
                assert self.execute_query(query), f"Failed: {query}"
                time.sleep(1)
    
    def run_search_test(self, search_term: str):
        """Example search test"""
        with self.test_context("Search Test") as test_result:
            queries = [
                'click search button',
                f'type "{search_term}" in search field',
                'click search or press enter'
            ]
            
            for query in queries:
                test_result['queries_used'].append(query)
                assert self.execute_query(query), f"Failed: {query}"
                time.sleep(1)
    
    def generate_report(self, filename: str = "test_report.html"):
        """Generate HTML test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>FluentTest Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f8ff; padding: 20px; border-radius: 5px; }
        .summary { display: flex; gap: 20px; margin: 20px 0; }
        .stat { background: #e8f4f8; padding: 15px; border-radius: 5px; text-align: center; }
        .test { margin: 10px 0; padding: 15px; border-radius: 5px; }
        .passed { background: #d4edda; }
        .failed { background: #f8d7da; }
    </style>
</head>
<body>
    <div class="header">
        <h1>FluentTest Report</h1>
        <p>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        <p>App: """ + self.app_package + """</p>
    </div>
    
    <div class="summary">
        <div class="stat">
            <h3>Total Tests</h3>
            <h2>""" + str(total_tests) + """</h2>
        </div>
        <div class="stat">
            <h3>Passed</h3>
            <h2 style="color: green;">""" + str(passed_tests) + """</h2>
        </div>
        <div class="stat">
            <h3>Success Rate</h3>
            <h2>""" + (f"{(passed_tests/total_tests*100):.1f}" if total_tests > 0 else "0") + """%</h2>
        </div>
    </div>
    
    <h2>Test Results</h2>"""
        
        for result in self.test_results:
            status = "passed" if result['success'] else "failed"
            status_text = "PASSED" if result['success'] else "FAILED"
            
            html_content += f"""
            <div class="test {status}">
                <h3>{result['test_name']} - {status_text}</h3>
                <p>Duration: {result['duration']:.2f}s</p>
                <p>Queries: {', '.join(result['queries_used'])}</p>
                {f"<p>Error: {result['error']}</p>" if result['error'] else ""}
            </div>
            """
        
        html_content += "</body></html>"
        
        with open(filename, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Report generated: {filename}")
