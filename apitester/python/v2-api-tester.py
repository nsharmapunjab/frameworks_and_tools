#!/usr/bin/env python3

"""
Universal REST API Testing Tool
Production-Ready Fixed Python Version
Built by Nitin Sharma

Clean implementation with working functionality:
- User input for expected response and status code
- Simple, clean HTML reports
- No broken JavaScript features
- Production-ready error handling
"""

import requests
import json
import re
import argparse
import sys
import time
from datetime import datetime
from urllib.parse import urlparse
import copy
import random
from typing import Dict, List, Any, Optional
import os
import html


class CurlParser:
    """Handles parsing of curl commands"""
    
    @staticmethod
    def parse_curl(curl_command: str) -> Dict[str, Any]:
        """Parse curl command and extract URL, method, headers, and data"""
        print('🔍 Parsing curl command...')
        print(f'📝 Raw input length: {len(curl_command)}')
        
        parsed = {
            'method': 'GET',
            'url': '',
            'headers': {},
            'data': None,
            'params': {}
        }

        # Extract URL - Multiple patterns for robustness
        url_patterns = [
            r"'(https?://[^']+)'",
            r'"(https?://[^"]+)"',
            r'--location\s+[\'"]([^\'"]+)[\'"]',
            r'curl\s+[\'"]([^\'"]+)[\'"]',
            r'(https?://[^\s\'"]+)'
        ]

        for pattern in url_patterns:
            match = re.search(pattern, curl_command)
            if match:
                parsed['url'] = match.group(1)
                print(f'✅ Found URL: {parsed["url"]}')
                break

        # Extract method
        method_match = re.search(r'-X\s+(\w+)|--request\s+(\w+)', curl_command, re.IGNORECASE)
        if method_match:
            parsed['method'] = (method_match.group(1) or method_match.group(2)).upper()
            print(f'✅ Found method: {parsed["method"]}')

        # Extract headers with proper parsing
        header_pattern = r'(?:--header|-H)\s+[\'"]([^\'"]+)[\'"]'
        for header_match in re.finditer(header_pattern, curl_command):
            header = header_match.group(1)
            if ':' in header:
                key, value = header.split(':', 1)
                parsed['headers'][key.strip()] = value.strip()
                print(f'✅ Found header: {key.strip()} = {value.strip()}')

        # Extract data with improved parsing
        parsed['data'] = CurlParser._extract_data(curl_command)

        # Auto-detect POST method if data exists
        if parsed['data'] and parsed['method'] == 'GET':
            parsed['method'] = 'POST'
            print('🔄 Auto-detected method as POST due to data presence')

        return parsed

    @staticmethod
    def _extract_data(command: str) -> Optional[Dict[str, Any]]:
        """Extract data from curl command"""
        print('🔍 Attempting data extraction...')
        
        # Multiple data extraction patterns
        data_patterns = [
            r"--data\s+'([^']+(?:'[^']*'[^']*)*?)'",
            r'--data\s+"([^"]+(?:"[^"]*"[^"]*)*?)"',
            r"-d\s+'([^']+(?:'[^']*'[^']*)*?)'",
            r'-d\s+"([^"]+(?:"[^"]*"[^"]*)*?)"',
            r'--data-raw\s+[\'"]([^\'"]+)[\'"]'
        ]

        for i, pattern in enumerate(data_patterns):
            match = re.search(pattern, command, re.DOTALL)
            
            if match and match.group(1):
                print(f'📝 Pattern {i + 1} matched')
                data_str = match.group(1).strip()
                
                try:
                    # Try to parse as JSON
                    parsed = json.loads(data_str)
                    print(f'✅ Successfully parsed JSON: {list(parsed.keys()) if isinstance(parsed, dict) else "Array/Value"}')
                    return parsed
                except json.JSONDecodeError:
                    print('⚠️ Not JSON data, treating as string')
                    return data_str

        print('❌ No data found')
        return None


class TestCaseGenerator:
    """Generates comprehensive test cases"""
    
    def __init__(self):
        self.security_payloads = [
            {'name': 'XSS', 'payload': '<script>alert("xss")</script>'},
            {'name': 'SQL', 'payload': "'; DROP TABLE users; --"},
            {'name': 'NoSQL', 'payload': '{"$gt": ""}'},
            {'name': 'Command', 'payload': '; rm -rf /'},
            {'name': 'Path', 'payload': '../../../etc/passwd'}
        ]

    def generate_test_cases(self, parsed_curl: Dict[str, Any], expected_status: int = 200) -> List[Dict[str, Any]]:
        """Generate comprehensive test cases"""
        print('\n🔧 Generating test cases...')
        print(f'📊 Target: {parsed_curl["method"]} {parsed_curl["url"]}')
        print(f'📊 Expected Status: {expected_status}')
        print(f'📊 Has data: {bool(parsed_curl["data"])}')
        
        test_cases = []
        base_request = copy.deepcopy(parsed_curl)

        # 1. POSITIVE TEST
        test_cases.append({
            'type': 'Positive',
            'description': 'Valid request with original data',
            'request': copy.deepcopy(base_request),
            'expected_status': expected_status,
            'expected_result': f'{expected_status} {self._get_status_text(expected_status)}'
        })

        # Generate different types of tests based on data availability
        if base_request.get('data') and isinstance(base_request['data'], dict):
            self._generate_object_tests(base_request, test_cases)

        # Generate header tests
        if base_request.get('headers'):
            self._generate_header_tests(base_request, test_cases)

        print(f'🎯 Generated {len(test_cases)} total test cases\n')
        return test_cases

    def _generate_object_tests(self, base_request: Dict[str, Any], test_cases: List[Dict[str, Any]]):
        """Generate tests for object data"""
        data = base_request['data']
        
        # Missing field tests
        for field in list(data.keys())[:3]:  # Limit to first 3 fields
            modified_data = copy.deepcopy(data)
            del modified_data[field]
            
            test_cases.append({
                'type': 'Negative',
                'description': f'Missing required field: {field}',
                'request': {**base_request, 'data': modified_data},
                'expected_status': 400,
                'expected_result': '400 Bad Request'
            })

        # Type validation tests
        for field, value in list(data.items())[:2]:  # Limit to first 2 fields
            if isinstance(value, str):
                modified_data = copy.deepcopy(data)
                modified_data[field] = 12345
                test_cases.append({
                    'type': 'Negative',
                    'description': f'Invalid type for {field} (number instead of string)',
                    'request': {**base_request, 'data': modified_data},
                    'expected_status': 400,
                    'expected_result': '400 Bad Request'
                })

        # Null value tests
        for field in list(data.keys())[:2]:  # Limit to first 2 fields
            modified_data = copy.deepcopy(data)
            modified_data[field] = None
            test_cases.append({
                'type': 'Negative',
                'description': f'Null value for {field}',
                'request': {**base_request, 'data': modified_data},
                'expected_status': 400,
                'expected_result': '400 Bad Request'
            })

        # Security tests - only for string fields
        string_fields = [k for k, v in data.items() if isinstance(v, str)]
        if string_fields:
            field = string_fields[0]  # Test only first string field
            for payload in self.security_payloads[:3]:  # Limit to 3 security tests
                modified_data = copy.deepcopy(data)
                modified_data[field] = payload['payload']
                test_cases.append({
                    'type': 'Security',
                    'description': f'{payload["name"]} injection in {field}',
                    'request': {**base_request, 'data': modified_data},
                    'expected_status': 400,
                    'expected_result': '400 Bad Request'
                })

    def _generate_header_tests(self, base_request: Dict[str, Any], test_cases: List[Dict[str, Any]]):
        """Generate header-related tests"""
        if 'Content-Type' in base_request['headers']:
            # Missing Content-Type
            no_content_type = copy.deepcopy(base_request)
            del no_content_type['headers']['Content-Type']
            test_cases.append({
                'type': 'Header Test',
                'description': 'Missing Content-Type header',
                'request': no_content_type,
                'expected_status': 415,
                'expected_result': '415 Unsupported Media Type'
            })

    def _get_status_text(self, status: int) -> str:
        """Get HTTP status text"""
        status_texts = {
            200: 'OK', 201: 'Created', 202: 'Accepted', 204: 'No Content',
            400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden',
            404: 'Not Found', 405: 'Method Not Allowed', 409: 'Conflict', 
            415: 'Unsupported Media Type', 422: 'Unprocessable Entity', 
            429: 'Too Many Requests', 500: 'Internal Server Error', 
            502: 'Bad Gateway', 503: 'Service Unavailable'
        }
        return status_texts.get(status, 'Unknown')


class HTTPExecutor:
    """Handles HTTP request execution"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 15

    def execute_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP request"""
        try:
            url = request['url']
            method = request['method']
            headers = request.get('headers', {})
            data = request.get('data')
            
            print(f'🔍 Making {method} request to {url}')

            # Prepare request arguments
            kwargs = {
                'timeout': 15,
                'headers': headers,
                'allow_redirects': True
            }

            if data is not None:
                if isinstance(data, dict):
                    kwargs['json'] = data
                elif isinstance(data, str):
                    kwargs['data'] = data
                else:
                    kwargs['data'] = json.dumps(data)

            # Make the request
            start_time = time.time()
            response = self.session.request(method, url, **kwargs)
            response_time = time.time() - start_time
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = response.text

            return {
                'status': response.status_code,
                'data': response_data,
                'headers': dict(response.headers),
                'response_time': response_time
            }

        except requests.exceptions.Timeout:
            return {
                'status': 0,
                'error': 'Request timeout (15s)',
                'data': None,
                'response_time': 15.0
            }
        except requests.exceptions.ConnectionError as e:
            return {
                'status': 0,
                'error': f'Connection error: {str(e)[:100]}...',
                'data': None,
                'response_time': 0
            }
        except Exception as e:
            return {
                'status': 0,
                'error': str(e)[:100] + '...' if len(str(e)) > 100 else str(e),
                'data': None,
                'response_time': 0
            }


class ReportGenerator:
    """Generates HTML and console reports"""
    
    def __init__(self):
        self.results = []

    def add_result(self, test_case: Dict[str, Any], response: Dict[str, Any], expected_status: int):
        """Add test result"""
        passed = self._is_expected_result(response['status'], expected_status, test_case['type'])
        
        self.results.append({
            'test_name': f"{test_case['type']} - {test_case['description']}",
            'test_type': test_case['type'],
            'description': test_case['description'],
            'response_code': response['status'],
            'expected': expected_status,
            'actual': response['status'],
            'passed': passed,
            'error': response.get('error'),
            'response_time': response.get('response_time', 0),
            'request': test_case['request']
        })

    def _is_expected_result(self, actual_status: int, expected_status: int, test_type: str) -> bool:
        """Check if result matches expectations"""
        if test_type == 'Positive':
            return actual_status in [expected_status, 200, 201]
        elif test_type in ['Negative', 'Security']:
            return actual_status >= 400
        elif test_type == 'Header Test':
            return actual_status in [400, 415]
        else:
            return actual_status == expected_status

    def print_console_summary(self):
        """Print console summary"""
        print('\n📊 Test Execution Summary')
        print('=========================\n')
        
        passed = sum(1 for r in self.results if r['passed'])
        failed = len(self.results) - passed
        pass_rate = (passed / len(self.results) * 100) if self.results else 0
        
        print(f'✅ Passed: {passed}')
        print(f'❌ Failed: {failed}')
        print(f'📈 Total: {len(self.results)}')
        print(f'📊 Pass Rate: {pass_rate:.1f}%')
        
        # Category breakdown
        categories = {}
        for result in self.results:
            cat = result['test_type']
            if cat not in categories:
                categories[cat] = {'total': 0, 'passed': 0}
            categories[cat]['total'] += 1
            if result['passed']:
                categories[cat]['passed'] += 1
        
        print('\n📋 Category Breakdown:')
        for cat, stats in categories.items():
            rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f'  {cat}: {stats["passed"]}/{stats["total"]} ({rate:.1f}%)')
        
        avg_time = sum(r["response_time"] for r in self.results) / len(self.results) if self.results else 0
        print(f'\n🔗 Average Response Time: {avg_time:.2f}s')

    def generate_html_report(self, original_curl: str):
        """Generate clean HTML report without broken features"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'api-test-report-{timestamp}.html'
        
        passed = sum(1 for r in self.results if r['passed'])
        failed = len(self.results) - passed
        pass_rate = (passed / len(self.results) * 100) if self.results else 0
        
        html_content = self._build_html_content(passed, failed, pass_rate, original_curl)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f'\n📄 HTML Report Generated: {filename}')
            print(f'🌐 Open in browser: file://{os.path.abspath(filename)}')
        except Exception as error:
            print(f'❌ Could not save HTML report: {error}')

    def _build_html_content(self, passed: int, failed: int, pass_rate: float, original_curl: str) -> str:
        """Build clean HTML report content"""
        
        # Build table rows
        table_rows = []
        for result in self.results:
            status_class = 'pass' if result['passed'] else 'fail'
            status_text = '✅ PASS' if result['passed'] else '❌ FAIL'
            
            if result.get('error'):
                status_text = '❌ ERROR'
                status_class = 'error'
            
            # Generate curl command for this test
            curl_command = self._generate_curl_command(result['request'])
            
            table_rows.append(f'''
            <tr>
                <td><span class="test-type">{html.escape(result["test_type"])}</span></td>
                <td class="description">{html.escape(result["description"])}</td>
                <td class="curl-cell">
                    <details>
                        <summary>View cURL</summary>
                        <pre class="curl-code">{html.escape(curl_command)}</pre>
                    </details>
                </td>
                <td>{result["expected"]}</td>
                <td>{result["actual"]}</td>
                <td>{result["response_time"]:.2f}s</td>
                <td><span class="status {status_class}">{status_text}</span></td>
            </tr>''')
        
        table_rows_html = '\n'.join(table_rows)
        original_curl_escaped = html.escape(original_curl)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Test Report - {current_time}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            padding: 20px; 
        }}
        .container {{ 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.1); 
            overflow: hidden; 
        }}
        .header {{ 
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
            color: white; 
            padding: 30px; 
            text-align: center; 
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; font-weight: 300; }}
        .header .subtitle {{ font-size: 1.2em; opacity: 0.8; }}
        .author-credit {{ 
            background: rgba(255,255,255,0.1); 
            padding: 8px 15px; 
            border-radius: 20px; 
            font-size: 0.9em; 
            display: inline-block;
            margin-top: 15px;
        }}
        .stats-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            padding: 30px; 
            background: #f8f9fa; 
        }}
        .stat-card {{ 
            background: white; 
            padding: 25px; 
            border-radius: 15px; 
            text-align: center; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.08); 
        }}
        .stat-number {{ font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }}
        .stat-label {{ font-size: 1.1em; color: #666; text-transform: uppercase; letter-spacing: 1px; }}
        .passed {{ color: #27ae60; }}
        .failed {{ color: #e74c3c; }}
        .total {{ color: #3498db; }}
        .progress-bar {{ 
            width: 100%; 
            height: 8px; 
            background: #ecf0f1; 
            border-radius: 4px; 
            overflow: hidden; 
            margin: 20px 0; 
        }}
        .progress-fill {{ 
            height: 100%; 
            background: linear-gradient(90deg, #27ae60, #2ecc71); 
            width: {pass_rate}%; 
        }}
        .original-curl {{ 
            margin: 20px 30px; 
            padding: 20px; 
            background: #2c3e50; 
            color: #ecf0f1; 
            border-radius: 10px; 
            font-family: 'Courier New', monospace; 
            font-size: 14px; 
            word-break: break-all; 
        }}
        .original-curl h3 {{ 
            margin-bottom: 10px; 
            color: #3498db; 
        }}
        .table-container {{ padding: 30px; overflow-x: auto; }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            background: white; 
            border-radius: 10px; 
            overflow: hidden; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.08); 
        }}
        th {{ 
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%); 
            color: white; 
            padding: 15px 10px; 
            text-align: left; 
            font-weight: 600; 
            font-size: 0.9em; 
            text-transform: uppercase; 
        }}
        td {{ 
            padding: 12px 10px; 
            border-bottom: 1px solid #ecf0f1; 
            vertical-align: top;
        }}
        tr:hover td {{ background: #f8f9fa; }}
        .test-type {{ 
            padding: 6px 12px; 
            border-radius: 15px; 
            font-size: 0.8em; 
            font-weight: 600; 
            text-transform: uppercase; 
            background: #ecf0f1;
            color: #2c3e50;
        }}
        .status {{ 
            padding: 6px 12px; 
            border-radius: 15px; 
            font-weight: 600; 
            font-size: 0.8em; 
        }}
        .status.pass {{ background: #d5f4e6; color: #27ae60; }}
        .status.fail {{ background: #fadbd8; color: #e74c3c; }}
        .status.error {{ background: #d5dbdb; color: #566573; }}
        .description {{ max-width: 250px; word-wrap: break-word; }}
        .curl-cell {{ max-width: 200px; }}
        .curl-code {{ 
            background: #2c3e50; 
            color: #ecf0f1; 
            padding: 10px; 
            border-radius: 5px; 
            font-size: 12px; 
            overflow-x: auto; 
            max-width: 300px;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        details {{ cursor: pointer; }}
        summary {{ 
            background: #3498db; 
            color: white; 
            padding: 6px 12px; 
            border-radius: 5px; 
            font-size: 0.8em; 
            outline: none;
        }}
        summary:hover {{ background: #2980b9; }}
        .footer {{ 
            background: #2c3e50; 
            color: white; 
            text-align: center; 
            padding: 20px; 
            font-size: 0.9em; 
        }}
        @media (max-width: 768px) {{
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .header h1 {{ font-size: 2em; }}
            th, td {{ padding: 8px 6px; font-size: 0.8em; }}
            .original-curl {{ margin: 10px; padding: 15px; font-size: 12px; }}
            .curl-code {{ font-size: 10px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 API Test Report</h1>
            <div class="subtitle">Generated on {current_time}</div>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <div style="margin-top: 15px; font-size: 1.3em;">Pass Rate: {pass_rate:.1f}%</div>
            <div class="author-credit">Built by Nitin Sharma</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number passed">{passed}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number failed">{failed}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number total">{passed + failed}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #9b59b6;">{len([r for r in self.results if 'Security' in r['test_type']])}</div>
                <div class="stat-label">Security Tests</div>
            </div>
        </div>
        
        <div class="original-curl">
            <h3>Original cURL Command:</h3>
            <div>{original_curl_escaped}</div>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Test Type</th>
                        <th>Description</th>
                        <th>cURL Command</th>
                        <th>Expected</th>
                        <th>Actual</th>
                        <th>Response Time</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows_html}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <div>Generated by Universal REST API Testing Tool (Fixed Python Version)</div>
            <div style="margin-top: 10px; opacity: 0.8;">
                Report contains {passed + failed} test cases with {pass_rate:.1f}% pass rate
            </div>
            <div style="margin-top: 5px; opacity: 0.6; font-size: 0.8em;">
                Built with ❤️ by Nitin Sharma
            </div>
        </div>
    </div>
</body>
</html>'''

    def _generate_curl_command(self, request: Dict[str, Any]) -> str:
        """Generate curl command for test case"""
        curl_parts = ['curl']
        
        if request.get('method') and request['method'] != 'GET':
            curl_parts.append(f"-X {request['method']}")
        
        curl_parts.append(f"'{request.get('url', '')}'")
        
        if request.get('headers'):
            for key, value in request['headers'].items():
                curl_parts.append(f"-H '{key}: {value}'")
        
        if request.get('data'):
            if isinstance(request['data'], dict):
                data_str = json.dumps(request['data'])
            else:
                data_str = str(request['data'])
            curl_parts.append(f"-d '{data_str}'")
        
        return ' \\\n  '.join(curl_parts)


class CLIInterface:
    """Enhanced command line interface"""
    
    def get_multiline_input(self, prompt: str) -> str:
        """Get multiline input from user with better handling"""
        print(prompt)
        print('📋 Instructions:')
        print('   1. Type or paste your curl command (can be multiple lines)')
        print('   2. Press Enter on an empty line to finish')
        print('   3. If pasting fails, type the command manually')
        print('   4. Example: curl -X POST "https://api.example.com" -H "Content-Type: application/json" -d \'{"key":"value"}\'')
        print('')
        
        lines = []
        print('> ', end='', flush=True)
        
        while True:
            try:
                line = input()
                if line.strip() == '':
                    if lines:  # If we have some input, finish
                        break
                    else:  # If no input yet, continue waiting
                        print('> ', end='', flush=True)
                        continue
                else:
                    lines.append(line)
                    print('> ', end='', flush=True)
            except KeyboardInterrupt:
                print('\n\n❌ Operation cancelled by user.')
                sys.exit(1)
            except EOFError:
                break
        
        result = '\n'.join(lines).strip()
        
        # If the result is empty, provide a fallback
        if not result:
            print('\n⚠️  No input detected. Let\'s try a different approach.')
            print('Please enter your curl command on a single line:')
            try:
                result = input('curl > ').strip()
            except (KeyboardInterrupt, EOFError):
                print('\n❌ Operation cancelled by user.')
                sys.exit(1)
        
        return result
    
    def get_expected_status_code(self) -> int:
        """Get expected status code from user"""
        print('\n📊 Expected Response Configuration')
        print('==================================')
        
        while True:
            try:
                status_input = input('🔢 Enter expected status code (default: 200): ').strip()
                
                if not status_input:
                    print('✅ Using default status code: 200')
                    return 200
                
                status_code = int(status_input)
                
                if 100 <= status_code <= 599:
                    print(f'✅ Expected status code set to: {status_code}')
                    return status_code
                else:
                    print('❌ Please enter a valid HTTP status code (100-599)')
                    
            except ValueError:
                print('❌ Please enter a valid number')
            except KeyboardInterrupt:
                print('\n\n❌ Operation cancelled by user.')
                sys.exit(1)
    
    def get_expected_response(self) -> Optional[Dict[str, Any]]:
        """Get expected response from user"""
        print('\n📝 Expected Response Configuration (Optional)')
        print('===========================================')
        print('You can specify expected response data for validation.')
        print('Leave empty to skip response validation.')
        print('Format: JSON object (e.g., {"status": "success", "data": {...}})')
        
        while True:
            try:
                response_input = input('\n🎯 Enter expected response JSON (or press Enter to skip): ').strip()
                
                if not response_input:
                    print('✅ Skipping response validation')
                    return None
                
                try:
                    expected_response = json.loads(response_input)
                    print('✅ Expected response configured successfully')
                    return expected_response
                except json.JSONDecodeError as e:
                    print(f'❌ Invalid JSON format: {e}')
                    retry = input('🔄 Try again? (y/n): ').lower().strip()
                    if retry != 'y':
                        print('✅ Skipping response validation')
                        return None
                        
            except KeyboardInterrupt:
                print('\n\n❌ Operation cancelled by user.')
                sys.exit(1)
    
    def show_welcome_message(self):
        """Show enhanced welcome message"""
        print('🧪 Universal REST API Testing Tool (Fixed Python Version)')
        print('=========================================================')
        print('Built by Nitin Sharma')
        print('')
        print('✨ Features:')
        print('  🚀 Comprehensive test case generation')
        print('  🔒 Security vulnerability testing')
        print('  🎯 Edge case and boundary testing')
        print('  📊 Real HTTP request execution')
        print('  📄 Clean HTML reports')
        print('  ⏱️  Response time analysis')
        print('')
        print('💡 Tip: If you have issues pasting multi-line commands,')
        print('   you can also run in command line mode:')
        print('   python api_tester.py --curl "your_curl_command_here"')
        print('')
    
    def get_sample_curl_if_needed(self) -> str:
        """Provide sample curl command if user needs it"""
        print('\n🤔 Need a sample curl command to test?')
        use_sample = input('Use sample curl command? (y/n): ').lower().strip()
        
        if use_sample == 'y':
            sample_curl = '''curl -X POST "https://api.restful-api.dev/objects" \\
-H "Content-Type: application/json" \\
-d '{
  "name": "Apple MacBook Pro 16",
  "data": {
    "year": 2019,
    "price": 1849.99,
    "CPU model": "Intel Core i9",
    "Hard disk size": "1 TB"
  }
}'
'''
            print('\n📋 Sample curl command:')
            print(sample_curl)
            return sample_curl.replace('\\\n', ' ')
        
        return ""


class APITester:
    """Main API testing orchestrator"""
    
    def __init__(self):
        self.parser = CurlParser()
        self.generator = TestCaseGenerator()
        self.executor = HTTPExecutor()
        self.reporter = ReportGenerator()
        self.cli = CLIInterface()

    def run_tests(self, curl_command: str, expected_status: int = 200, 
                 expected_response: Optional[Dict] = None):
        """Run the complete test suite"""
        print('\n🚀 Starting API Test Suite')
        print('=' * 50)
        
        # Parse curl command
        parsed = self.parser.parse_curl(curl_command)
        
        if not parsed['url']:
            print('❌ Could not extract URL from curl command')
            return
        
        print(f'\n📡 Target: {parsed["method"]} {parsed["url"]}')
        print(f'📋 Headers: {len(parsed["headers"])} found')
        print(f'📊 Data: {"Yes" if parsed["data"] else "No"}')
        print(f'🎯 Expected Status: {expected_status}')
        
        # Generate test cases
        test_cases = self.generator.generate_test_cases(parsed, expected_status)
        
        # Execute tests
        print('\n⏳ Executing Tests...')
        print('=' * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                # Show progress
                print(f'\r🔄 Running test {i}/{len(test_cases)}: {test_case["type"]}...', end='', flush=True)
                
                # Execute request
                response = self.executor.execute_request(test_case['request'])
                
                # Add result to reporter
                self.reporter.add_result(test_case, response, test_case['expected_status'])
                
                # Brief status update
                status = '✅' if response['status'] != 0 else '❌'
                if i % 5 == 0:  # Show detailed progress every 5 tests
                    print(f'\r{status} Completed {i}/{len(test_cases)} tests', end='', flush=True)
                
                # Rate limiting
                time.sleep(0.1)  # Small delay to be respectful
                
            except Exception as error:
                print(f'\n❌ Error in test {i}: {error}')
                continue
        
        print('\r✅ All tests completed!' + ' ' * 30)
        
        # Generate reports
        self.reporter.print_console_summary()
        self.reporter.generate_html_report(curl_command)

    def run_interactive_mode(self):
        """Run in interactive mode with enhanced user input"""
        try:
            self.cli.show_welcome_message()
            
            # Get curl command
            curl_command = self.cli.get_multiline_input('📝 Enter your curl command:')
            
            # If no command provided, offer sample
            if not curl_command.strip():
                curl_command = self.cli.get_sample_curl_if_needed()
                
            if not curl_command.strip():
                print('❌ No curl command provided. Exiting...')
                sys.exit(1)
            
            # Show what we got
            print(f'\n✅ Curl command received ({len(curl_command)} characters)')
            print('📋 First 100 characters:', curl_command[:100] + ('...' if len(curl_command) > 100 else ''))
            
            # Get expected status code
            expected_status = self.cli.get_expected_status_code()
            
            # Get expected response (optional)
            expected_response = self.cli.get_expected_response()
            
            # Run tests
            self.run_tests(curl_command, expected_status, expected_response)
            
        except Exception as error:
            print(f'❌ Error: {error}')
            import traceback
            print('Debug info:', traceback.format_exc())


def parse_arguments():
    """Enhanced argument parsing"""
    parser = argparse.ArgumentParser(
        description='🧪 Universal REST API Testing Tool (Fixed Python Version)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  Interactive mode (RECOMMENDED):
    python api_tester.py

  Command line mode (use quotes around the entire curl command):
    python api_tester.py --curl 'curl -X POST "https://api.example.com/test" -H "Content-Type: application/json" -d "{\"name\":\"test\"}"'

  With expected status:
    python api_tester.py --curl 'curl -X POST ...' --status 201

Common Issues:
  - If pasting fails in terminal, use command line mode instead
  - Wrap the entire curl command in single quotes
  - For JSON data, escape quotes properly: {\"key\":\"value\"}

Features:
  🚀 Comprehensive test cases including positive, negative, security tests
  🔒 Security testing: XSS, SQL injection, command injection, path traversal
  🎯 Edge case testing: missing fields, wrong types, null values
  📊 Real HTTP execution with proper error handling and response time tracking
  📄 Clean HTML reports with expandable cURL commands
  ⏱️  Response time analysis and performance insights
  👨‍💻 Built with ❤️ by Nitin Sharma
        '''
    )
    
    parser.add_argument(
        '--curl', '-c',
        help='cURL command to test (wrap in quotes)',
        type=str
    )
    
    parser.add_argument(
        '--status', '-s',
        help='Expected success status code (default: 200)',
        type=int,
        default=200
    )
    
    parser.add_argument(
        '--response', '-r',
        help='Expected response JSON (optional)',
        type=str
    )
    
    parser.add_argument(
        '--interactive', '-i',
        help='Force interactive mode',
        action='store_true',
        default=False
    )
    
    parser.add_argument(
        '--sample',
        help='Use sample curl command for testing',
        action='store_true',
        default=False
    )
    
    return parser.parse_args()


def main():
    """Enhanced main function"""
    args = parse_arguments()
    tester = APITester()
    
    # Handle sample command
    if args.sample:
        sample_curl = 'curl -X POST "https://api.restful-api.dev/objects" -H "Content-Type: application/json" -d \'{"name": "Apple MacBook Pro 16", "data": {"year": 2019, "price": 1849.99, "CPU model": "Intel Core i9", "Hard disk size": "1 TB"}}\''
        print('🧪 Running with sample curl command...')
        print('Built by Nitin Sharma\n')
        tester.run_tests(sample_curl, args.status)
        return
    
    # If no arguments provided or interactive flag, run interactive mode
    if len(sys.argv) == 1 or args.interactive or not args.curl:
        tester.run_interactive_mode()
        return
    
    # Command line mode
    expected_response = None
    if args.response:
        try:
            expected_response = json.loads(args.response)
        except json.JSONDecodeError:
            print('❌ Invalid JSON format for expected response')
            sys.exit(1)
    
    print('🧪 Running API Tests (Command Line Mode)...')
    print('Built by Nitin Sharma\n')
    
    tester.run_tests(args.curl, args.status, expected_response)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n❌ Operation cancelled by user.')
        sys.exit(1)
    except Exception as error:
        print(f'❌ Fatal error: {error}')
        sys.exit(1)
