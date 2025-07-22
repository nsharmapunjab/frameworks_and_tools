#!/usr/bin/env python3

"""
Enhanced Universal REST API Testing Tool
Comprehensive Test Case Generation
Author : Nitin Sharma

Features:
- Comprehensive test case coverage
- Advanced payload manipulation
- Better data type testing
- Enhanced security testing
- Boundary value analysis
- Real-world scenario testing
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
import uuid
from itertools import combinations


class CurlParser:
    """Handles parsing of curl commands"""
    
    @staticmethod
    def parse_curl(curl_command: str) -> Dict[str, Any]:
        """Parse curl command and extract URL, method, headers, and data"""
        print('🔍 Parsing curl command...')
        print(f'📝 Raw input length: {len(curl_command)}')
        
        # Clean up the curl command - remove line breaks and extra spaces
        cleaned_command = re.sub(r'\s*\\\s*', ' ', curl_command)
        cleaned_command = re.sub(r'\s+', ' ', cleaned_command).strip()
        print(f'📝 Cleaned command length: {len(cleaned_command)}')
        print(f'📝 Cleaned preview: {cleaned_command[:300]}...')
        
        parsed = {
            'method': 'GET',
            'url': '',
            'headers': {},
            'data': None,
            'params': {}
        }

        # Extract URL - Multiple patterns for robustness
        url_patterns = [
            r"--location\s+--request\s+\w+\s+['\"]([^'\"]+)['\"]",
            r"--location\s+['\"]([^'\"]+)['\"]",
            r"curl\s+--location\s+['\"]([^'\"]+)['\"]",
            r"curl\s+['\"]([^'\"]+)['\"]",
            r"'(https?://[^']+)'",
            r'"(https?://[^"]+)"',
            r'(https?://[^\s\'"\\]+)'
        ]

        for pattern in url_patterns:
            match = re.search(pattern, cleaned_command)
            if match:
                parsed['url'] = match.group(1)
                print(f'✅ Found URL: {parsed["url"]}')
                break

        if not parsed['url']:
            print('❌ Could not find URL in curl command')

        # Extract method - check for explicit method first
        method_match = re.search(r'--request\s+(\w+)|-X\s+(\w+)', cleaned_command, re.IGNORECASE)
        if method_match:
            parsed['method'] = (method_match.group(1) or method_match.group(2)).upper()
            print(f'✅ Found explicit method: {parsed["method"]}')
        
        # Extract headers with completely rewritten logic for better JSON handling
        print('🔍 Starting header extraction...')
        
        # First, let's find all --header occurrences and extract them properly
        header_matches = []
        
        # Pattern to find all --header flags and their content
        # This captures everything between the quotes, including complex JSON
        basic_header_pattern = r"--header\s+(['\"])(.*?)\1"
        
        for match in re.finditer(basic_header_pattern, cleaned_command, re.DOTALL):
            quote_char = match.group(1)
            header_content = match.group(2)
            print(f'🔍 Raw header found: {header_content}')
            
            # Split on first colon to separate key and value
            if ':' in header_content:
                key, value = header_content.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Special handling for JSON values (detect by starting with {)
                if value.startswith('{'):
                    # For JSON values, we need to be more careful
                    # Let's try to extract the complete JSON from the original command
                    json_pattern = rf"--header\s+['\"]({re.escape(key)}:\s*\{{[^}}]*\}})['\"]"
                    json_match = re.search(json_pattern, cleaned_command)
                    if json_match:
                        full_header = json_match.group(1)
                        if ':' in full_header:
                            _, json_value = full_header.split(':', 1)
                            value = json_value.strip()
                            print(f'🔍 Extracted JSON value: {value}')
                
                parsed['headers'][key] = value
                print(f'✅ Found header: {key} = {value}')
                header_matches.append((key, value))
        
        # If the above didn't work well, try a more aggressive approach
        if not header_matches or any('user' not in str(parsed['headers']).lower() for _ in [1]):
            print('🔍 Trying alternative header extraction...')
            
            # Split the command into parts and look for headers manually
            parts = cleaned_command.split('--header')
            for i, part in enumerate(parts[1:], 1):  # Skip first part (before first --header)
                part = part.strip()
                print(f'🔍 Processing header part {i}: {part[:100]}...')
                
                # Extract the quoted content
                quote_patterns = [
                    r"^['\"]([^'\"]*(?:\{[^}]*\}[^'\"]*)*)['\"]",  # Handle JSON in quotes
                    r"^['\"]([^'\"]+)['\"]",  # Simple quoted content
                ]
                
                for pattern in quote_patterns:
                    match = re.match(pattern, part)
                    if match:
                        header_content = match.group(1)
                        print(f'🔍 Extracted header content: {header_content}')
                        
                        if ':' in header_content:
                            key, value = header_content.split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Override if we didn't get this header before or if it was truncated
                            if key not in parsed['headers'] or len(parsed['headers'][key]) < len(value):
                                parsed['headers'][key] = value
                                print(f'✅ Updated header: {key} = {value}')
                        break
        
        print(f'🔍 Final headers extracted: {len(parsed["headers"])} headers')
        
        # Special fix for the user header that was being truncated
        # Look specifically for the user header pattern in the original command
        user_header_patterns = [
            r"--header\s+['\"]user:\s*(\{[^}]+\})['\"]",
            r"--header\s+['\"]user:\s*(\{.*?\})['\"]",
            r"user:\s*(\{[^}]+\})",
        ]
        
        for pattern in user_header_patterns:
            user_match = re.search(pattern, curl_command)  # Search in original command
            if user_match:
                user_value = user_match.group(1)
                parsed['headers']['user'] = user_value
                print(f'🔧 FIXED user header: {user_value}')
                break
        
        # Validate that user header is properly formatted
        if 'user' in parsed['headers']:
            user_val = parsed['headers']['user']
            if user_val == '{' or not user_val.endswith('}'):
                print(f'⚠️ WARNING: user header appears truncated: {user_val}')
                # Try to extract from original command one more time
                user_search = re.search(r'user[\'"]?\s*:\s*[\'"]?(\{[^}]*\})', curl_command)
                if user_search:
                    fixed_user = user_search.group(1)
                    parsed['headers']['user'] = fixed_user
                    print(f'🔧 RECOVERED user header: {fixed_user}')
                else:
                    print('❌ Could not recover user header - authentication may fail')

        # Extract data with improved parsing
        parsed['data'] = CurlParser._extract_data(cleaned_command)

        # IMPORTANT: Auto-detect POST method if data exists but no method specified
        if parsed['data'] and parsed['method'] == 'GET':
            parsed['method'] = 'POST'
            print('🔄 Auto-detected method as POST due to data presence (curl default behavior)')
        
        # Debug output
        print('\n🔧 PARSING SUMMARY:')
        print(f'   Method: {parsed["method"]}')
        print(f'   URL: {parsed["url"]}')
        print(f'   Headers count: {len(parsed["headers"])}')
        for key, value in parsed["headers"].items():
            print(f'     {key}: {value[:100]}...' if len(value) > 100 else f'     {key}: {value}')
        print(f'   Data type: {type(parsed["data"]).__name__}')
        if parsed["data"]:
            if isinstance(parsed["data"], dict):
                print(f'   Data keys: {list(parsed["data"].keys())}')
            else:
                print(f'   Data preview: {str(parsed["data"])[:100]}...')
        print('')

        return parsed

    @staticmethod
    def _extract_data(command: str) -> Optional[Any]:
        """Extract data from curl command with improved parsing"""
        print('🔍 Attempting data extraction...')
        
        # Clean up the command first
        cleaned_command = re.sub(r'\s*\\\s*', ' ', command)
        cleaned_command = re.sub(r'\s+', ' ', cleaned_command).strip()
        
        # Multiple data extraction patterns - more comprehensive
        data_patterns = [
            r"--data-raw\s+'([^']+(?:'[^']*'[^']*)*?)'",
            r'--data-raw\s+"([^"]+(?:"[^"]*"[^"]*)*?)"',
            r"--data\s+'([^']+(?:'[^']*'[^']*)*?)'",
            r'--data\s+"([^"]+(?:"[^"]*"[^"]*)*?)"',
            r"-d\s+'([^']+(?:'[^']*'[^']*)*?)'",
            r'-d\s+"([^"]+(?:"[^"]*"[^"]*)*?)"',
            r'--data-binary\s+[\'"]([^\'"]+)[\'"]'
        ]

        for i, pattern in enumerate(data_patterns):
            match = re.search(pattern, cleaned_command, re.DOTALL)
            
            if match:
                data_str = match.group(1).strip()
                
                print(f'📝 Pattern {i + 1} matched')
                print(f'📝 Raw data extracted: {data_str[:200]}...')
                
                # Remove escape characters that might be from shell escaping
                data_str = data_str.replace('\\"', '"').replace("\\'", "'")
                data_str = data_str.strip()
                
                try:
                    # Try to parse as JSON first
                    parsed = json.loads(data_str)
                    print(f'✅ Successfully parsed JSON')
                    return parsed
                except json.JSONDecodeError as e:
                    print(f'⚠️ JSON parse error: {e}')
                    # Try to fix common JSON issues
                    try:
                        # Fix common formatting issues
                        fixed_data = data_str.replace("'", '"')  # Replace single quotes with double
                        fixed_data = re.sub(r'(\w+):', r'"\1":', fixed_data)  # Quote unquoted keys
                        parsed = json.loads(fixed_data)
                        print(f'✅ Fixed and parsed JSON')
                        return parsed
                    except json.JSONDecodeError:
                        print('⚠️ Not valid JSON, treating as string data')
                        return data_str

        print('❌ No data found in curl command')
        return None


class EnhancedTestCaseGenerator:
    """Enhanced test case generator with comprehensive coverage"""
    
    def __init__(self):
        self.security_payloads = [
            {'name': 'XSS Basic', 'payload': '<script>alert("xss")</script>'},
            {'name': 'XSS Advanced', 'payload': '"><script>alert(String.fromCharCode(88,83,83))</script>'},
            {'name': 'SQL Injection', 'payload': "'; DROP TABLE users; --"},
            {'name': 'SQL Union', 'payload': "' UNION SELECT null,version(),null--"},
            {'name': 'NoSQL Injection', 'payload': '{"$gt": ""}'},
            {'name': 'NoSQL Where', 'payload': '{"$where": "function(){return true}"}'},
            {'name': 'Command Injection', 'payload': '; rm -rf /'},
            {'name': 'Command Pipe', 'payload': '| cat /etc/passwd'},
            {'name': 'Path Traversal', 'payload': '../../../etc/passwd'},
            {'name': 'Path Windows', 'payload': '..\\..\\..\\windows\\system32\\drivers\\etc\\hosts'},
            {'name': 'LDAP Injection', 'payload': '*)(uid=*))(|(uid=*'},
            {'name': 'XXE Attack', 'payload': '<?xml version="1.0"?><!DOCTYPE test [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><test>&xxe;</test>'},
            {'name': 'SSTI', 'payload': '{{7*7}}'},
            {'name': 'SSTI Advanced', 'payload': '${7*7}'},
            {'name': 'Code Injection', 'payload': '__import__("os").system("id")'}
        ]
        
        self.edge_cases = [
            {'name': 'Very Long String', 'value': 'A' * 10000},
            {'name': 'Special Characters', 'value': '!@#$%^&*()_+{}[]|\\:";\'<>?,.`~'},
            {'name': 'Unicode Emojis', 'value': '🚀💻🔥🎯📊✅❌🧪'},
            {'name': 'Unicode Mixed', 'value': 'Test-测试-тест-テスト-🌟'},
            {'name': 'Empty String', 'value': ''},
            {'name': 'Only Whitespace', 'value': '   '},
            {'name': 'Tab and Newlines', 'value': '\t\n\r\n'},
            {'name': 'Null String', 'value': 'null'},
            {'name': 'Boolean True', 'value': 'true'},
            {'name': 'Boolean False', 'value': 'false'},
            {'name': 'Number String', 'value': '12345'},
            {'name': 'Float String', 'value': '123.456'},
            {'name': 'Negative Number', 'value': '-999'},
            {'name': 'Scientific Notation', 'value': '1.23e-10'},
            {'name': 'Extremely Long', 'value': 'X' * 100000},
            {'name': 'Control Characters', 'value': '\x00\x01\x02\x03\x04\x05'},
            {'name': 'High Unicode', 'value': '\u2028\u2029\ufeff'},
            {'name': 'JSON Injection', 'value': '","malicious":"value'},
            {'name': 'Format String', 'value': '%s%s%s%s%s%s%s%s%s%s'},
            {'name': 'Buffer Overflow', 'value': 'A' * 65536}
        ]

        self.type_variations = {
            'string': [123, True, False, [], {}, None, 3.14],
            'number': ['string', True, False, [], {}, None, '123abc'],
            'boolean': ['true', 'false', 1, 0, [], {}, None],
            'array': ['string', 123, True, {}, None],
            'object': ['string', 123, True, [], None]
        }

        self.boundary_values = {
            'integers': [0, 1, -1, 2147483647, -2147483648, 4294967295, -4294967296],
            'floats': [0.0, 1.0, -1.0, 3.14159, 1.7976931348623157e+308, 2.2250738585072014e-308],
            'strings': ['', 'a', 'A' * 255, 'A' * 256, 'A' * 65535, 'A' * 65536]
        }

    def generate_comprehensive_test_cases(self, parsed_curl: Dict[str, Any], expected_status: int = 200) -> List[Dict[str, Any]]:
        """Generate comprehensive test cases covering all scenarios"""
        print('\n🔧 Generating comprehensive test cases...')
        print(f'📊 Target: {parsed_curl["method"]} {parsed_curl["url"]}')
        print(f'📊 Expected Status: {expected_status}')
        print(f'📊 Has data: {bool(parsed_curl["data"])}')
        
        test_cases = []
        base_request = copy.deepcopy(parsed_curl)

        # 1. POSITIVE TESTS
        test_cases.extend(self._generate_positive_tests(base_request, expected_status))
        
        # 2. FIELD VALIDATION TESTS
        if base_request.get('data') and isinstance(base_request['data'], dict):
            test_cases.extend(self._generate_field_validation_tests(base_request))
            test_cases.extend(self._generate_required_field_tests(base_request))
            test_cases.extend(self._generate_type_validation_tests(base_request))
            test_cases.extend(self._generate_null_empty_tests(base_request))
            test_cases.extend(self._generate_nested_field_tests(base_request))
            test_cases.extend(self._generate_array_field_tests(base_request))
            
        # 3. SECURITY TESTS
        test_cases.extend(self._generate_security_tests(base_request))
        
        # 4. EDGE CASE TESTS
        test_cases.extend(self._generate_edge_case_tests(base_request))
        
        # 5. BOUNDARY TESTS
        test_cases.extend(self._generate_boundary_tests(base_request))
        
        # 6. FORMAT TESTS
        test_cases.extend(self._generate_format_tests(base_request))
        
        # 7. HEADER TESTS
        test_cases.extend(self._generate_header_tests(base_request))
        
        # 8. METHOD TESTS
        test_cases.extend(self._generate_method_tests(base_request))
        
        # 9. URL TESTS
        test_cases.extend(self._generate_url_tests(base_request))
        
        # 10. AUTHENTICATION TESTS
        test_cases.extend(self._generate_auth_tests(base_request))
        
        # 11. PERFORMANCE TESTS
        test_cases.extend(self._generate_performance_tests(base_request))

        print(f'🎯 Generated {len(test_cases)} total test cases\n')
        return test_cases

    def _generate_positive_tests(self, base_request: Dict[str, Any], expected_status: int) -> List[Dict[str, Any]]:
        """Generate positive test cases"""
        tests = []
        
        # Original valid request
        tests.append({
            'type': 'Positive - Original',
            'description': 'Valid request with original data',
            'request': copy.deepcopy(base_request),
            'expected_status': expected_status,
            'expected_result': f'{expected_status} {self._get_status_text(expected_status)}'
        })
        
        # Minimal valid request (if has optional fields)
        if base_request.get('data') and isinstance(base_request['data'], dict):
            minimal_data = self._create_minimal_valid_payload(base_request['data'])
            if minimal_data != base_request['data']:
                tests.append({
                    'type': 'Positive - Minimal',
                    'description': 'Minimal valid request with only required fields',
                    'request': {**base_request, 'data': minimal_data},
                    'expected_status': expected_status,
                    'expected_result': f'{expected_status} {self._get_status_text(expected_status)}'
                })
        
        return tests

    def _generate_field_validation_tests(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive field validation tests"""
        tests = []
        data = base_request['data']
        
        if not isinstance(data, dict):
            return tests
        
        # Test each field individually
        for field_name, field_value in data.items():
            # Test missing field
            modified_data = copy.deepcopy(data)
            del modified_data[field_name]
            tests.append({
                'type': 'Negative - Missing Field',
                'description': f'Missing required field: {field_name}',
                'request': {**base_request, 'data': modified_data},
                'expected_status': 400,
                'expected_result': '400 Bad Request'
            })
            
            # Test field with different data types
            if isinstance(field_value, str):
                wrong_types = [123, True, [], {}, None]
            elif isinstance(field_value, (int, float)):
                wrong_types = ["string", True, [], {}, None]
            elif isinstance(field_value, bool):
                wrong_types = ["string", 123, [], {}, None]
            elif isinstance(field_value, list):
                wrong_types = ["string", 123, True, {}, None]
            elif isinstance(field_value, dict):
                wrong_types = ["string", 123, True, [], None]
            else:
                wrong_types = ["string", 123, True, [], {}]
            
            for wrong_type in wrong_types[:3]:  # Test first 3 wrong types
                modified_data = copy.deepcopy(data)
                modified_data[field_name] = wrong_type
                tests.append({
                    'type': 'Negative - Wrong Type',
                    'description': f'Wrong type for {field_name}: {type(wrong_type).__name__} instead of {type(field_value).__name__}',
                    'request': {**base_request, 'data': modified_data},
                    'expected_status': 400,
                    'expected_result': '400 Bad Request'
                })
        
        return tests

    def _generate_required_field_tests(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate tests for missing combinations of fields"""
        tests = []
        data = base_request['data']
        
        if not isinstance(data, dict) or len(data) <= 1:
            return tests
        
        fields = list(data.keys())
        
        # Test missing pairs of fields
        for field1, field2 in list(combinations(fields, 2))[:5]:  # Test first 5 combinations
            modified_data = copy.deepcopy(data)
            del modified_data[field1]
            del modified_data[field2]
            tests.append({
                'type': 'Negative - Missing Multiple',
                'description': f'Missing multiple fields: {field1}, {field2}',
                'request': {**base_request, 'data': modified_data},
                'expected_status': 400,
                'expected_result': '400 Bad Request'
            })
        
        # Test with only one field present
        for field in fields[:3]:  # Test first 3 fields
            modified_data = {field: data[field]}
            tests.append({
                'type': 'Negative - Only One Field',
                'description': f'Only one field present: {field}',
                'request': {**base_request, 'data': modified_data},
                'expected_status': 400,
                'expected_result': '400 Bad Request'
            })
        
        return tests

    def _generate_type_validation_tests(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive type validation tests"""
        tests = []
        data = base_request['data']
        
        if not isinstance(data, dict):
            return tests
        
        for field_name, field_value in list(data.items())[:5]:  # Test first 5 fields
            field_type = type(field_value).__name__
            
            if field_type in self.type_variations:
                for wrong_value in self.type_variations[field_type][:4]:  # Test first 4 variations
                    modified_data = copy.deepcopy(data)
                    modified_data[field_name] = wrong_value
                    tests.append({
                        'type': 'Negative - Type Validation',
                        'description': f'Invalid type for {field_name}: {type(wrong_value).__name__} (expected {field_type})',
                        'request': {**base_request, 'data': modified_data},
                        'expected_status': 400,
                        'expected_result': '400 Bad Request'
                    })
        
        return tests

    def _generate_null_empty_tests(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate null and empty value tests"""
        tests = []
        data = base_request['data']
        
        if not isinstance(data, dict):
            return tests
        
        for field_name in list(data.keys())[:5]:  # Test first 5 fields
            # Test null value
            modified_data = copy.deepcopy(data)
            modified_data[field_name] = None
            tests.append({
                'type': 'Negative - Null Value',
                'description': f'Null value for {field_name}',
                'request': {**base_request, 'data': modified_data},
                'expected_status': 400,
                'expected_result': '400 Bad Request'
            })
            
            # Test empty string (for string fields)
            if isinstance(data[field_name], str):
                modified_data = copy.deepcopy(data)
                modified_data[field_name] = ""
                tests.append({
                    'type': 'Negative - Empty String',
                    'description': f'Empty string for {field_name}',
                    'request': {**base_request, 'data': modified_data},
                    'expected_status': 400,
                    'expected_result': '400 Bad Request'
                })
            
            # Test empty array (for array fields)
            if isinstance(data[field_name], list):
                modified_data = copy.deepcopy(data)
                modified_data[field_name] = []
                tests.append({
                    'type': 'Negative - Empty Array',
                    'description': f'Empty array for {field_name}',
                    'request': {**base_request, 'data': modified_data},
                    'expected_status': 400,
                    'expected_result': '400 Bad Request'
                })
            
            # Test empty object (for object fields)
            if isinstance(data[field_name], dict):
                modified_data = copy.deepcopy(data)
                modified_data[field_name] = {}
                tests.append({
                    'type': 'Negative - Empty Object',
                    'description': f'Empty object for {field_name}',
                    'request': {**base_request, 'data': modified_data},
                    'expected_status': 400,
                    'expected_result': '400 Bad Request'
                })
        
        # Test completely empty payload
        tests.append({
            'type': 'Negative - Empty Payload',
            'description': 'Completely empty JSON object',
            'request': {**base_request, 'data': {}},
            'expected_status': 400,
            'expected_result': '400 Bad Request'
        })
        
        return tests

    def _generate_nested_field_tests(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate tests for nested objects"""
        tests = []
        data = base_request['data']
        
        if not isinstance(data, dict):
            return tests
        
        # Find nested objects
        for field_name, field_value in data.items():
            if isinstance(field_value, dict) and field_value:
                # Test missing nested fields
                for nested_field in list(field_value.keys())[:3]:  # Test first 3 nested fields
                    modified_data = copy.deepcopy(data)
                    del modified_data[field_name][nested_field]
                    tests.append({
                        'type': 'Negative - Missing Nested',
                        'description': f'Missing nested field: {field_name}.{nested_field}',
                        'request': {**base_request, 'data': modified_data},
                        'expected_status': 400,
                        'expected_result': '400 Bad Request'
                    })
                
                # Test wrong types in nested fields
                for nested_field, nested_value in list(field_value.items())[:2]:  # Test first 2 nested fields
                    if isinstance(nested_value, str):
                        wrong_values = [123, True, [], {}]
                    elif isinstance(nested_value, (int, float)):
                        wrong_values = ["string", True, [], {}]
                    else:
                        wrong_values = ["string", 123, True]
                    
                    for wrong_value in wrong_values[:2]:  # Test first 2 wrong values
                        modified_data = copy.deepcopy(data)
                        modified_data[field_name][nested_field] = wrong_value
                        tests.append({
                            'type': 'Negative - Nested Type',
                            'description': f'Wrong type for {field_name}.{nested_field}',
                            'request': {**base_request, 'data': modified_data},
                            'expected_status': 400,
                            'expected_result': '400 Bad Request'
                        })
        
        return tests

    def _generate_array_field_tests(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate tests for array fields"""
        tests = []
        data = base_request['data']
        
        if not isinstance(data, dict):
            return tests
        
        # Find array fields
        for field_name, field_value in data.items():
            if isinstance(field_value, list) and field_value:
                # Test with wrong array element types
                if field_value:
                    first_element = field_value[0]
                    if isinstance(first_element, dict):
                        # Test missing required fields in array elements
                        if first_element:
                            for key in list(first_element.keys())[:2]:  # Test first 2 keys
                                modified_data = copy.deepcopy(data)
                                if modified_data[field_name]:
                                    del modified_data[field_name][0][key]
                                    tests.append({
                                        'type': 'Negative - Array Element',
                                        'description': f'Missing {key} in {field_name} array element',
                                        'request': {**base_request, 'data': modified_data},
                                        'expected_status': 400,
                                        'expected_result': '400 Bad Request'
                                    })
                    
                    # Test with wrong element types
                    modified_data = copy.deepcopy(data)
                    if isinstance(first_element, str):
                        modified_data[field_name][0] = 123
                    elif isinstance(first_element, (int, float)):
                        modified_data[field_name][0] = "string"
                    elif isinstance(first_element, dict):
                        modified_data[field_name][0] = "string"
                    
                    tests.append({
                        'type': 'Negative - Array Type',
                        'description': f'Wrong type for {field_name} array element',
                        'request': {**base_request, 'data': modified_data},
                        'expected_status': 400,
                        'expected_result': '400 Bad Request'
                    })
                
                # Test with too many array elements
                if len(field_value) < 100:  # Only if current array is not already large
                    modified_data = copy.deepcopy(data)
                    # Add many duplicate elements
                    modified_data[field_name] = field_value * 50
                    tests.append({
                        'type': 'Negative - Array Size',
                        'description': f'Too many elements in {field_name} array',
                        'request': {**base_request, 'data': modified_data},
                        'expected_status': 400,
                        'expected_result': '400 Bad Request'
                    })
        
        return tests

    def _generate_security_tests(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive security tests"""
        tests = []
        
        if not base_request.get('data'):
            return tests
        
        # Find string fields for security testing
        string_fields = self._find_string_fields(base_request['data'])
        
        # Apply security payloads to string fields
        for field_path in string_fields[:3]:  # Test first 3 string fields
            for payload in self.security_payloads[:10]:  # Test first 10 security payloads
                modified_data = copy.deepcopy(base_request['data'])
                self._set_nested_value(modified_data, field_path, payload['payload'])
                
                tests.append({
                    'type': 'Security Test',
                    'description': f'{payload["name"]} injection in {field_path}',
                    'request': {**base_request, 'data': modified_data},
                    'expected_status': 400,
                    'expected_result': '400 Bad Request'
                })
        
        # Test with malformed JSON in string fields
        for field_path in string_fields[:2]:  # Test first 2 string fields
            modified_data = copy.deepcopy(base_request['data'])
            self._set_nested_value(modified_data, field_path, '{"malformed": json}')
            
            tests.append({
                'type': 'Security Test',
                'description': f'Malformed JSON injection in {field_path}',
                'request': {**base_request, 'data': modified_data},
                'expected_status': 400,
                'expected_result': '400 Bad Request'
            })
        
        return tests

    def _generate_edge_case_tests(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive edge case tests"""
        tests = []
        
        if not base_request.get('data'):
            return tests
        
        # Find string fields for edge case testing
        string_fields = self._find_string_fields(base_request['data'])
        
        if string_fields:
            field_path = string_fields[0]  # Test first string field
            for edge_case in self.edge_cases[:15]:  # Test first 15 edge cases
                modified_data = copy.deepcopy(base_request['data'])
                self._set_nested_value(modified_data, field_path, edge_case['value'])
                
                tests.append({
                    'type': 'Edge Case Test',
                    'description': f'{edge_case["name"]} value for {field_path}',
                    'request': {**base_request, 'data': modified_data},
                    'expected_status': 400,
                    'expected_result': '400 Bad Request'
                })
        
        return tests

    def _generate_boundary_tests(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive boundary value tests"""
        tests = []
        data = base_request['data']
        
        if not isinstance(data, dict):
            return tests
        
        # Test boundary values for different data types
        for field_name, field_value in list(data.items())[:5]:  # Test first 5 fields
            if isinstance(field_value, (int, float)):
                boundary_type = 'integers' if isinstance(field_value, int) else 'floats'
                for boundary in self.boundary_values[boundary_type][:5]:  # Test first 5 boundary values
                    modified_data = copy.deepcopy(data)
                    modified_data[field_name] = boundary
                    tests.append({
                        'type': 'Boundary Test',
                        'description': f'Boundary value {boundary} for {field_name}',
                        'request': {**base_request, 'data': modified_data},
                        'expected_status': 400,
                        'expected_result': '400 Bad Request'
                    })
            
            elif isinstance(field_value, str):
                for boundary in self.boundary_values['strings'][:4]:  # Test first 4 boundary values
                    modified_data = copy.deepcopy(data)
                    modified_data[field_name] = boundary
                    tests.append({
                        'type': 'Boundary Test',
                        'description': f'Boundary string length for {field_name}',
                        'request': {**base_request, 'data': modified_data},
                        'expected_status': 400,
                        'expected_result': '400 Bad Request'
                    })
        
        return tests

    def _generate_format_tests(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate format and structure tests"""
        tests = []
        
        # Test invalid JSON formats
        invalid_formats = [
            '{"invalid": json}',
            '{"missing": "quote}',
            '{"trailing": "comma",}',
            '{invalid: "key"}',
            '{"duplicate": "key", "duplicate": "key2"}',
            '',
            'not json at all',
            '[]',  # Array instead of object
            'null',
            'true',
            '123'
        ]
        
        for invalid_format in invalid_formats:
            tests.append({
                'type': 'Format Test',
                'description': f'Invalid JSON format: {invalid_format[:30]}...',
                'request': {**base_request, 'data': invalid_format},
                'expected_status': 400,
                'expected_result': '400 Bad Request'
            })
        
        # Test with different content encodings
        if base_request.get('data') and isinstance(base_request['data'], dict):
            # Test with extra fields
            modified_data = copy.deepcopy(base_request['data'])
            modified_data['extraField'] = 'unexpected'
            modified_data['anotherExtra'] = 123
            tests.append({
                'type': 'Format Test',
                'description': 'Extra unexpected fields in payload',
                'request': {**base_request, 'data': modified_data},
                'expected_status': 400,
                'expected_result': '400 Bad Request'
            })
        
        return tests

    def _generate_header_tests(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive header tests"""
        tests = []
        
        # Test missing Content-Type
        if any(k.lower() == 'content-type' for k in base_request.get('headers', {})):
            no_content_type = copy.deepcopy(base_request)
            no_content_type['headers'] = {k: v for k, v in no_content_type['headers'].items() 
                                        if k.lower() != 'content-type'}
            tests.append({
                'type': 'Header Test',
                'description': 'Missing Content-Type header',
                'request': no_content_type,
                'expected_status': 415,
                'expected_result': '415 Unsupported Media Type'
            })

            # Test wrong Content-Type values
            wrong_content_types = [
                'text/plain',
                'application/xml',
                'text/html',
                'application/x-www-form-urlencoded',
                'multipart/form-data',
                'invalid/content-type'
            ]
            
            for wrong_type in wrong_content_types:
                wrong_content_type = copy.deepcopy(base_request)
                # Update all variations of Content-Type
                for key in list(wrong_content_type['headers'].keys()):
                    if key.lower() == 'content-type':
                        wrong_content_type['headers'][key] = wrong_type
                        break
                else:
                    wrong_content_type['headers']['Content-Type'] = wrong_type
                
                tests.append({
                    'type': 'Header Test',
                    'description': f'Invalid Content-Type: {wrong_type}',
                    'request': wrong_content_type,
                    'expected_status': 415,
                    'expected_result': '415 Unsupported Media Type'
                })

        # Test missing custom headers
        custom_headers = ['user', 'channel-name', 'city', 'channel-host', 'appversion']
        for header in custom_headers:
            if any(k.lower() == header.lower() for k in base_request.get('headers', {})):
                no_header = copy.deepcopy(base_request)
                no_header['headers'] = {k: v for k, v in no_header['headers'].items() 
                                      if k.lower() != header.lower()}
                tests.append({
                    'type': 'Header Test',
                    'description': f'Missing required header: {header}',
                    'request': no_header,
                    'expected_status': 400,
                    'expected_result': '400 Bad Request'
                })

        # Test invalid header values
        for header_name, header_value in list(base_request.get('headers', {}).items())[:5]:
            if header_name.lower() not in ['content-type', 'content-length']:
                # Test empty header value
                empty_header = copy.deepcopy(base_request)
                empty_header['headers'][header_name] = ''
                tests.append({
                    'type': 'Header Test',
                    'description': f'Empty value for header: {header_name}',
                    'request': empty_header,
                    'expected_status': 400,
                    'expected_result': '400 Bad Request'
                })
                
                # Test malformed header value
                malformed_header = copy.deepcopy(base_request)
                malformed_header['headers'][header_name] = 'malformed\nheader\rvalue'
                tests.append({
                    'type': 'Header Test',
                    'description': f'Malformed value for header: {header_name}',
                    'request': malformed_header,
                    'expected_status': 400,
                    'expected_result': '400 Bad Request'
                })

        # Test missing Authorization (if present in original)
        if any(k.lower() == 'authorization' for k in base_request.get('headers', {})):
            no_auth = copy.deepcopy(base_request)
            no_auth['headers'] = {k: v for k, v in no_auth['headers'].items() 
                                if k.lower() != 'authorization'}
            tests.append({
                'type': 'Security Test',
                'description': 'Missing Authorization header',
                'request': no_auth,
                'expected_status': 401,
                'expected_result': '401 Unauthorized'
            })
            
            # Test invalid Authorization format
            invalid_auth = copy.deepcopy(base_request)
            for key in list(invalid_auth['headers'].keys()):
                if key.lower() == 'authorization':
                    invalid_auth['headers'][key] = 'InvalidFormat'
                    break
            tests.append({
                'type': 'Security Test',
                'description': 'Invalid Authorization header format',
                'request': invalid_auth,
                'expected_status': 401,
                'expected_result': '401 Unauthorized'
            })

        return tests

    def _generate_method_tests(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate HTTP method tests"""
        tests = []
        original_method = base_request['method']
        
        # Test wrong methods
        all_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT']
        wrong_methods = [m for m in all_methods if m != original_method]
        
        for method in wrong_methods[:6]:  # Test 6 wrong methods
            tests.append({
                'type': 'Method Test',
                'description': f'Wrong HTTP method ({method} instead of {original_method})',
                'request': {**base_request, 'method': method},
                'expected_status': 405,
                'expected_result': '405 Method Not Allowed'
            })

        return tests

    def _generate_url_tests(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate URL-related tests"""
        tests = []
        original_url = base_request['url']
        
        # Test non-existent endpoints
        url_variations = [
            original_url + '/nonexistent',
            original_url.rstrip('/') + '/invalid',
            original_url.replace('api/', 'api/v999/'),
            original_url.replace('api/', 'invalid/'),
            original_url + '?invalid=param'
        ]
        
        for wrong_url in url_variations:
            tests.append({
                'type': 'URL Test',
                'description': f'Invalid endpoint: {wrong_url.split("/")[-1]}',
                'request': {**base_request, 'url': wrong_url},
                'expected_status': 404,
                'expected_result': '404 Not Found'
            })

        return tests

    def _generate_auth_tests(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate authentication and authorization tests"""
        tests = []
        
        # Test with modified user header (if present)
        user_headers = ['user', 'authorization', 'x-api-key', 'token']
        for header_name in user_headers:
            matching_headers = [k for k in base_request.get('headers', {}) if k.lower() == header_name.lower()]
            if matching_headers:
                original_header = matching_headers[0]
                
                # Test with invalid user data
                invalid_user = copy.deepcopy(base_request)
                if header_name.lower() == 'user':
                    invalid_user['headers'][original_header] = '{"_id":"invalid_user_id"}'
                else:
                    invalid_user['headers'][original_header] = 'invalid_token'
                
                tests.append({
                    'type': 'Auth Test',
                    'description': f'Invalid {header_name} credentials',
                    'request': invalid_user,
                    'expected_status': 401,
                    'expected_result': '401 Unauthorized'
                })
                
                # Test with expired/malformed data
                expired_auth = copy.deepcopy(base_request)
                if header_name.lower() == 'user':
                    expired_auth['headers'][original_header] = '{"_id":"","expired":true}'
                else:
                    expired_auth['headers'][original_header] = 'expired.token.here'
                
                tests.append({
                    'type': 'Auth Test',
                    'description': f'Expired/malformed {header_name}',
                    'request': expired_auth,
                    'expected_status': 401,
                    'expected_result': '401 Unauthorized'
                })

        return tests

    def _generate_performance_tests(self, base_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance and stress tests"""
        tests = []
        
        if not base_request.get('data'):
            return tests
        
        # Test with very large payload
        large_payload = copy.deepcopy(base_request['data'])
        if isinstance(large_payload, dict):
            # Add a very large field
            large_payload['largeField'] = 'X' * 1000000  # 1MB string
            tests.append({
                'type': 'Performance Test',
                'description': 'Very large payload (1MB)',
                'request': {**base_request, 'data': large_payload},
                'expected_status': 413,
                'expected_result': '413 Payload Too Large'
            })
            
            # Test with many duplicate fields
            many_fields = copy.deepcopy(base_request['data'])
            for i in range(1000):
                many_fields[f'duplicateField{i}'] = f'value{i}'
            tests.append({
                'type': 'Performance Test',
                'description': 'Payload with many fields (1000)',
                'request': {**base_request, 'data': many_fields},
                'expected_status': 400,
                'expected_result': '400 Bad Request'
            })

        return tests

    def _find_string_fields(self, data: Any, path: str = '') -> List[str]:
        """Find all string fields in nested data structure"""
        fields = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, str):
                    fields.append(current_path)
                elif isinstance(value, (dict, list)):
                    fields.extend(self._find_string_fields(value, current_path))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                if isinstance(item, str):
                    fields.append(current_path)
                elif isinstance(item, (dict, list)):
                    fields.extend(self._find_string_fields(item, current_path))
        
        return fields

    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any):
        """Set value in nested data structure using dot notation"""
        if '.' not in path and '[' not in path:
            data[path] = value
            return
        
        # Handle array indices
        if '[' in path:
            # Simple handling for array[index] patterns
            parts = path.replace('[', '.').replace(']', '').split('.')
        else:
            parts = path.split('.')
        
        current = data
        for part in parts[:-1]:
            if part.isdigit():
                current = current[int(part)]
            else:
                current = current[part]
        
        final_key = parts[-1]
        if final_key.isdigit():
            current[int(final_key)] = value
        else:
            current[final_key] = value

    def _create_minimal_valid_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create minimal valid payload by removing optional fields"""
        # This is a simplified version - in real scenarios, you'd know which fields are required
        # For now, we'll assume all fields are required
        return data

    def _get_status_text(self, status: int) -> str:
        """Get HTTP status text"""
        status_texts = {
            200: 'OK', 201: 'Created', 202: 'Accepted', 204: 'No Content',
            400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden',
            404: 'Not Found', 405: 'Method Not Allowed', 409: 'Conflict', 
            413: 'Payload Too Large', 415: 'Unsupported Media Type', 
            422: 'Unprocessable Entity', 429: 'Too Many Requests', 
            500: 'Internal Server Error', 502: 'Bad Gateway', 
            503: 'Service Unavailable'
        }
        return status_texts.get(status, 'Unknown')


class HTTPExecutor:
    """Handles HTTP request execution"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 15

    def execute_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP request with exact curl replication"""
        try:
            url = request['url']
            method = request['method']
            headers = request.get('headers', {}).copy()
            data = request.get('data')
            
            # CRITICAL: Validate user header before making request
            if 'user' in headers:
                user_value = headers['user']
                if user_value in ['{', '', 'NOT FOUND'] or not user_value.strip():
                    print(f'⚠️ WARNING: Invalid user header detected: "{user_value}"')
                    print('⚠️ This will likely result in 401 Unauthorized')
                    return {
                        'status': 401,
                        'error': 'Invalid user header - authentication will fail',
                        'data': {'message': 'User header is malformed or empty'},
                        'response_time': 0
                    }
                elif not user_value.startswith('{') or not user_value.endswith('}'):
                    print(f'⚠️ WARNING: User header may be malformed: "{user_value}"')
            
            print(f'🔍 Making {method} request to {url}')

            kwargs = {
                'timeout': 15,
                'allow_redirects': True
            }

            # Handle headers
            if headers:
                clean_headers = {}
                for key, value in headers.items():
                    clean_headers[key] = value
                kwargs['headers'] = clean_headers
                
                # Debug critical headers
                if 'user' in clean_headers:
                    print(f'🔑 User header: {clean_headers["user"]}')

            # Handle data
            if data is not None:
                if isinstance(data, dict):
                    kwargs['json'] = data
                elif isinstance(data, str):
                    try:
                        json_data = json.loads(data)
                        kwargs['json'] = json_data
                    except json.JSONDecodeError:
                        kwargs['data'] = data
                        if 'headers' not in kwargs:
                            kwargs['headers'] = {}
                        if 'Content-Type' not in kwargs['headers']:
                            kwargs['headers']['Content-Type'] = 'application/json'
                else:
                    kwargs['json'] = data

            # Make the request
            start_time = time.time()
            response = self.session.request(method, url, **kwargs)
            response_time = time.time() - start_time
            
            # Try to parse JSON response
            try:
                if response.text.strip():
                    response_data = response.json()
                else:
                    response_data = {}
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
        """Add test result with enhanced response data"""
        passed = self._is_expected_result(response['status'], expected_status, test_case['type'])
        
        # Format response data for better display
        formatted_response = self._format_response_data(response)
        
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
            'request': test_case['request'],
            'response_data': formatted_response,
            'response_headers': response.get('headers', {}),
            'raw_response': response  # Keep raw response for debugging
        })

    def _format_response_data(self, response: Dict[str, Any]) -> str:
        """Format response data for display in HTML report"""
        if response.get('error'):
            return f"ERROR: {response['error']}"
        
        if response.get('data'):
            try:
                if isinstance(response['data'], dict):
                    # Pretty format JSON with syntax highlighting hints
                    formatted = json.dumps(response['data'], indent=2, ensure_ascii=False)
                    # Truncate very long responses for better UX
                    if len(formatted) > 5000:
                        lines = formatted.split('\n')
                        if len(lines) > 100:
                            truncated = '\n'.join(lines[:100])
                            return f"{truncated}\n\n... (Response truncated - showing first 100 lines of {len(lines)} total lines)"
                        else:
                            return f"{formatted[:5000]}\n\n... (Response truncated - showing first 5000 characters)"
                    return formatted
                elif isinstance(response['data'], str):
                    # Try to parse as JSON for pretty formatting
                    try:
                        parsed = json.loads(response['data'])
                        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
                        # Apply same truncation logic
                        if len(formatted) > 5000:
                            return f"{formatted[:5000]}\n\n... (Response truncated)"
                        return formatted
                    except json.JSONDecodeError:
                        # Return as-is if not JSON, but truncate if too long
                        if len(response['data']) > 2000:
                            return f"{response['data'][:2000]}\n\n... (Response truncated)"
                        return response['data']
                else:
                    return str(response['data'])
            except Exception:
                return str(response.get('data', 'No response data'))
        
        # Handle different status codes with helpful messages
        status = response.get('status', 'Unknown')
        if status == 0:
            return "Connection failed - No response received"
        elif status in [204, 304]:
            return f"Status: {status} - No content (this is normal)"
        else:
            return f"Status: {status} - No response body"

    def _get_response_size(self, response_data: str) -> str:
        """Get human-readable response size"""
        size_bytes = len(response_data.encode('utf-8'))
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _is_expected_result(self, actual_status: int, expected_status: int, test_type: str) -> bool:
        """Check if result matches expectations"""
        if 'Positive' in test_type:
            return actual_status in [expected_status, 200, 201, 202]
        elif any(keyword in test_type for keyword in ['Negative', 'Security', 'Edge Case', 'Boundary', 'Format']):
            return actual_status >= 400
        elif 'Header Test' in test_type:
            return actual_status in [400, 415]
        elif 'Method Test' in test_type:
            return actual_status == 405
        elif 'URL Test' in test_type:
            return actual_status == 404
        elif 'Auth Test' in test_type:
            return actual_status in [401, 403]
        elif 'Performance Test' in test_type:
            return actual_status in [400, 413, 429]
        else:
            return actual_status == expected_status

    def print_console_summary(self):
        """Print detailed console summary"""
        print('\n📊 Comprehensive Test Execution Summary')
        print('=' * 50)
        
        passed = sum(1 for r in self.results if r['passed'])
        failed = len(self.results) - passed
        pass_rate = (passed / len(self.results) * 100) if self.results else 0
        
        print(f'✅ Passed: {passed}')
        print(f'❌ Failed: {failed}')
        print(f'📈 Total: {len(self.results)}')
        print(f'📊 Pass Rate: {pass_rate:.1f}%')
        
        # Detailed category breakdown
        categories = {}
        for result in self.results:
            cat = result['test_type']
            if cat not in categories:
                categories[cat] = {'total': 0, 'passed': 0}
            categories[cat]['total'] += 1
            if result['passed']:
                categories[cat]['passed'] += 1
        
        print('\n📋 Detailed Category Breakdown:')
        for cat, stats in sorted(categories.items()):
            rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status = '✅' if rate > 80 else '⚠️' if rate > 50 else '❌'
            print(f'  {status} {cat}: {stats["passed"]}/{stats["total"]} ({rate:.1f}%)')
        
        # Performance stats
        avg_time = sum(r["response_time"] for r in self.results) / len(self.results) if self.results else 0
        max_time = max(r["response_time"] for r in self.results) if self.results else 0
        min_time = min(r["response_time"] for r in self.results) if self.results else 0
        
        print(f'\n⏱️ Performance Analysis:')
        print(f'  Average Response Time: {avg_time:.2f}s')
        print(f'  Maximum Response Time: {max_time:.2f}s')
        print(f'  Minimum Response Time: {min_time:.2f}s')
        
        # Security test results
        security_tests = [r for r in self.results if 'Security' in r['test_type']]
        if security_tests:
            security_passed = sum(1 for r in security_tests if r['passed'])
            print(f'\n🔒 Security Test Results: {security_passed}/{len(security_tests)} passed')
        
        print(f'\n📄 HTML Report Features:')
        print(f'  • Expandable cURL commands for each test')
        print(f'  • Complete API responses with headers and body')
        print(f'  • Response time and size information')
        print(f'  • Color-coded status indicators')
        print(f'  • Mobile-responsive design')

    def generate_html_report(self, original_curl: str):
        """Generate enhanced HTML report"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'comprehensive-api-test-report-{timestamp}.html'
        
        passed = sum(1 for r in self.results if r['passed'])
        failed = len(self.results) - passed
        pass_rate = (passed / len(self.results) * 100) if self.results else 0
        
        # Group results by category
        categories = {}
        for result in self.results:
            cat = result['test_type']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        html_content = self._build_enhanced_html_content(passed, failed, pass_rate, original_curl, categories)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f'\n📄 Enhanced HTML Report Generated: {filename}')
            print(f'🌐 Open in browser: file://{os.path.abspath(filename)}')
        except Exception as error:
            print(f'❌ Could not save HTML report: {error}')

    def _build_enhanced_html_content(self, passed: int, failed: int, pass_rate: float, 
                                   original_curl: str, categories: Dict[str, List]) -> str:
        """Build enhanced HTML report content with better organization"""
        
        # Build category sections
        category_sections = []
        for cat_name, cat_results in sorted(categories.items()):
            cat_passed = sum(1 for r in cat_results if r['passed'])
            cat_total = len(cat_results)
            cat_rate = (cat_passed / cat_total * 100) if cat_total > 0 else 0
            
            table_rows = []
            for result in cat_results:
                status_class = 'pass' if result['passed'] else 'fail'
                status_text = '✅ PASS' if result['passed'] else '❌ FAIL'
                
                if result.get('error'):
                    status_text = '❌ ERROR'
                    status_class = 'error'
                
                curl_command = self._generate_curl_command(result['request'])
                response_data = result.get('response_data', 'No response data')
                response_headers = result.get('response_headers', {})
                response_size = self._get_response_size(response_data)
                
                # Format response headers for display
                formatted_headers = []
                important_headers = ['content-type', 'content-length', 'server', 'x-powered-by', 'cache-control']
                
                # Show important headers first
                for header in important_headers:
                    for key, value in response_headers.items():
                        if key.lower() == header:
                            formatted_headers.append(f"{key}: {value}")
                
                # Add remaining headers
                for key, value in response_headers.items():
                    header_line = f"{key}: {value}"
                    if header_line not in formatted_headers:
                        formatted_headers.append(header_line)
                
                response_headers_text = "\n".join(formatted_headers) if formatted_headers else "No response headers"
                
                # Determine response status color
                response_status = result['actual']
                if response_status == 0:
                    response_class = 'error'
                    status_text_detail = 'Connection Failed'
                elif 200 <= response_status < 300:
                    response_class = 'success'
                    status_text_detail = 'Success'
                elif 300 <= response_status < 400:
                    response_class = 'info'
                    status_text_detail = 'Redirect'
                elif 400 <= response_status < 500:
                    response_class = 'client-error'
                    status_text_detail = 'Client Error'
                elif 500 <= response_status:
                    response_class = 'server-error'
                    status_text_detail = 'Server Error'
                else:
                    response_class = 'info'
                    status_text_detail = 'Unknown'
                
                table_rows.append(f'''
                <tr>
                    <td class="description">{html.escape(result["description"])}</td>
                    <td class="curl-cell">
                        <details>
                            <summary>📋 View cURL</summary>
                            <pre class="curl-code">{html.escape(curl_command)}</pre>
                        </details>
                    </td>
                    <td class="response-cell">
                        <details>
                            <summary class="response-summary">📄 View Response</summary>
                            <div class="response-container">
                                <div class="response-status">
                                    <span class="status-badge {response_class}">
                                        {response_status} - {status_text_detail}
                                    </span>
                                    <div class="response-meta">
                                        <span class="response-time">{result["response_time"]:.2f}s</span>
                                        <span class="response-size">{response_size}</span>
                                    </div>
                                </div>
                                <div class="response-section">
                                    <h4>📋 Response Headers ({len(response_headers)}):</h4>
                                    <pre class="response-headers">{html.escape(response_headers_text)}</pre>
                                </div>
                                <div class="response-section">
                                    <h4>📄 Response Body:</h4>
                                    <pre class="response-body">{html.escape(response_data)}</pre>
                                </div>
                            </div>
                        </details>
                    </td>
                    <td>{result["expected"]}</td>
                    <td>{result["actual"]}</td>
                    <td>{result["response_time"]:.2f}s</td>
                    <td><span class="status {status_class}">{status_text}</span></td>
                </tr>''')
            
            category_sections.append(f'''
            <div class="category-section">
                <div class="category-header">
                    <h3>{html.escape(cat_name)}</h3>
                    <div class="category-stats">
                        <span class="stat-badge {'pass' if cat_rate > 80 else 'warning' if cat_rate > 50 else 'fail'}">
                            {cat_passed}/{cat_total} ({cat_rate:.1f}%)
                        </span>
                    </div>
                </div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Description</th>
                                <th>cURL Command</th>
                                <th>API Response</th>
                                <th>Expected</th>
                                <th>Actual</th>
                                <th>Response Time</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(table_rows)}
                        </tbody>
                    </table>
                </div>
            </div>''')
        
        category_sections_html = '\n'.join(category_sections)
        original_curl_escaped = html.escape(original_curl)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive API Test Report - {current_time}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            padding: 20px; 
        }}
        .container {{ 
            max-width: 1600px; 
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
        .progress-bar {{ 
            width: 100%; 
            height: 12px; 
            background: rgba(255,255,255,0.2); 
            border-radius: 6px; 
            overflow: hidden; 
            margin: 20px 0; 
        }}
        .progress-fill {{ 
            height: 100%; 
            background: linear-gradient(90deg, #27ae60, #2ecc71); 
            width: {pass_rate}%; 
            transition: width 0.3s ease;
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
            transition: transform 0.2s ease;
        }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-number {{ font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }}
        .stat-label {{ font-size: 1.1em; color: #666; text-transform: uppercase; letter-spacing: 1px; }}
        .passed {{ color: #27ae60; }}
        .failed {{ color: #e74c3c; }}
        .total {{ color: #3498db; }}
        .security {{ color: #9b59b6; }}
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
        .category-section {{
            margin: 20px 30px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .category-header {{
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .category-header h3 {{
            margin: 0;
            font-size: 1.5em;
            font-weight: 300;
        }}
        .category-stats {{
            display: flex;
            gap: 10px;
        }}
        .stat-badge {{
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
        }}
        .stat-badge.pass {{ background: #d5f4e6; color: #27ae60; }}
        .stat-badge.warning {{ background: #fef9e7; color: #f39c12; }}
        .stat-badge.fail {{ background: #fadbd8; color: #e74c3c; }}
        .table-container {{ padding: 0; overflow-x: auto; }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            background: white; 
        }}
        th {{ 
            background: #f8f9fa; 
            color: #2c3e50; 
            padding: 15px 10px; 
            text-align: left; 
            font-weight: 600; 
            font-size: 0.9em; 
            text-transform: uppercase; 
            border-bottom: 2px solid #ecf0f1;
        }}
        td {{ 
            padding: 12px 10px; 
            border-bottom: 1px solid #ecf0f1; 
            vertical-align: top;
        }}
        tr:hover td {{ background: #f8f9fa; }}
        .status {{ 
            padding: 6px 12px; 
            border-radius: 15px; 
            font-weight: 600; 
            font-size: 0.8em; 
        }}
        .status.pass {{ background: #d5f4e6; color: #27ae60; }}
        .status.fail {{ background: #fadbd8; color: #e74c3c; }}
        .status.error {{ background: #d5dbdb; color: #566573; }}
        .description {{ max-width: 300px; word-wrap: break-word; }}
        .curl-cell {{ max-width: 200px; }}
        .response-cell {{ max-width: 250px; }}
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
        .response-container {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
            max-width: 400px;
        }}
        .response-status {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #dee2e6;
        }}
        .response-meta {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .status-badge {{
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
        }}
        .status-badge.success {{ background: #d4edda; color: #155724; }}
        .status-badge.client-error {{ background: #f8d7da; color: #721c24; }}
        .status-badge.server-error {{ background: #f5c6cb; color: #721c24; }}
        .status-badge.error {{ background: #d6d8db; color: #383d41; }}
        .status-badge.info {{ background: #d1ecf1; color: #0c5460; }}
        .response-time {{
            font-size: 0.8em;
            color: #6c757d;
            background: #e9ecef;
            padding: 3px 8px;
            border-radius: 8px;
        }}
        .response-size {{
            font-size: 0.8em;
            color: #6c757d;
            background: #f8f9fa;
            padding: 3px 8px;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }}; }}
        .response-time {{
            font-size: 0.8em;
            color: #6c757d;
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 8px;
        }}
        .response-size {{
            font-size: 0.8em;
            color: #6c757d;
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }}
        .response-section {{
            margin-bottom: 15px;
        }}
        .response-section h4 {{
            margin: 0 0 8px 0;
            font-size: 0.9em;
            color: #495057;
            font-weight: 600;
        }}
        .response-headers {{
            background: #495057;
            color: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
            font-size: 11px;
            max-height: 120px;
            overflow-y: auto;
            margin: 0;
            white-space: pre-wrap;
        }}
        .response-body {{
            background: #343a40;
            color: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            font-size: 11px;
            max-height: 200px;
            overflow-y: auto;
            margin: 0;
            white-space: pre-wrap;
            word-break: break-word;
        }}
        details {{ cursor: pointer; }}
        summary {{ 
            background: #3498db; 
            color: white; 
            padding: 6px 12px; 
            border-radius: 5px; 
            font-size: 0.8em; 
            outline: none;
            transition: background 0.2s ease;
        }}
        summary:hover {{ background: #2980b9; }}
        .response-summary {{
            background: #28a745;
        }}
        .response-summary:hover {{
            background: #218838;
        }}
        summary::marker {{
            display: none;
        }}
        summary::before {{
            content: "▶ ";
            display: inline-block;
            transition: transform 0.2s ease;
        }}
        details[open] summary::before {{
            transform: rotate(90deg);
        }}
        .footer {{ 
            background: #2c3e50; 
            color: white; 
            text-align: center; 
            padding: 20px; 
            font-size: 0.9em; 
        }}
        .enhanced-badge {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            display: inline-block;
            margin-top: 10px;
        }}
        @media (max-width: 768px) {{
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .header h1 {{ font-size: 2em; }}
            th, td {{ padding: 8px 6px; font-size: 0.8em; }}
            .original-curl {{ margin: 10px; padding: 15px; font-size: 12px; }}
            .curl-code {{ font-size: 10px; }}
            .category-section {{ margin: 10px; }}
            .response-container {{ max-width: 300px; }}
            .response-body {{ max-height: 150px; }}
            .response-headers {{ max-height: 100px; }}
            .curl-cell, .response-cell {{ max-width: 150px; }}
        }}
        @media (max-width: 480px) {{
            .stats-grid {{ grid-template-columns: 1fr; }}
            .category-header {{ flex-direction: column; text-align: center; }}
            .category-header h3 {{ margin-bottom: 10px; }}
            .response-container {{ max-width: 250px; }}
            .response-status {{ flex-direction: column; gap: 5px; }}
            th, td {{ padding: 6px 4px; font-size: 0.7em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Comprehensive API Test Report</h1>
            <div class="subtitle">Advanced Testing with Enhanced Coverage</div>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <div style="margin-top: 15px; font-size: 1.3em;">Pass Rate: {pass_rate:.1f}%</div>
            <div class="enhanced-badge">Generic API Test Tool by Nitin Sharma</div>
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
                <div class="stat-number security">{len([r for cat_results in categories.values() for r in cat_results if 'Security' in r['test_type']])}</div>
                <div class="stat-label">Security Tests</div>
            </div>
        </div>
        
        <div class="original-curl">
            <h3>Original cURL Command:</h3>
            <div>{original_curl_escaped}</div>
        </div>
        
        {category_sections_html}
        
        <div class="footer">
            <div>Generated by Enhanced Universal REST API Testing Tool</div>
            <div style="margin-top: 10px; opacity: 0.8;">
                Comprehensive test coverage with {passed + failed} test cases and {pass_rate:.1f}% pass rate
            </div>
            <div style="margin-top: 5px; opacity: 0.6; font-size: 0.8em;">
                Enhanced with ❤️  by Nitin Sharma - Advanced Security & Edge Case Testing
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
                    if lines:
                        break
                    else:
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
    
    def show_welcome_message(self):
        """Show enhanced welcome message"""
        print('🧪 Enhanced Universal REST API Testing Tool')
        print('============================================')
        print('Built by Nitin Sharma - Enhanced Version with Comprehensive Coverage')
        print('')
        print('✨ Enhanced Features:')
        print('  🚀 Comprehensive test case generation (100+ scenarios)')
        print('  🔒 Advanced security vulnerability testing')
        print('  🎯 Enhanced edge case and boundary testing')
        print('  📊 Real HTTP request execution with detailed analysis')
        print('  📄 Rich HTML reports with expandable cURL & API responses')
        print('  ⏱️  Performance analysis and response time tracking')
        print('  🛡️  Authentication and authorization testing')
        print('  📋 Format validation and structure testing')
        print('  🔍 Nested field and array validation')
        print('  💾 Large payload and stress testing')
        print('')
        print('🆕 New in this version:')
        print('  📱 Complete API response viewing in HTML reports')
        print('  📊 Response size and metadata display')
        print('  🎨 Beautiful expandable sections for requests & responses')
        print('  📱 Mobile-responsive design')
        print('')
        print('💡 This enhanced version generates significantly more test cases')
        print('   covering all aspects of API security and functionality.')
        print('   Each test result includes both the cURL request and API response!')
        print('')


class EnhancedAPITester:
    """Main enhanced API testing orchestrator"""
    
    def __init__(self):
        self.parser = CurlParser()
        self.generator = EnhancedTestCaseGenerator()
        self.executor = HTTPExecutor()
        self.reporter = ReportGenerator()
        self.cli = CLIInterface()

    def run_comprehensive_tests(self, curl_command: str, expected_status: int = 200):
        """Run the comprehensive test suite"""
        print('\n🚀 Starting Enhanced API Test Suite')
        print('=' * 60)
        
        # Parse curl command
        parsed = self.parser.parse_curl(curl_command)
        
        if not parsed['url']:
            print('❌ Could not extract URL from curl command')
            return
        
        print(f'\n📡 Target: {parsed["method"]} {parsed["url"]}')
        print(f'📋 Headers: {len(parsed["headers"])} found')
        print(f'📊 Data: {"Yes" if parsed["data"] else "No"}')
        print(f'🎯 Expected Status: {expected_status}')
        
        # Test original request first
        print('\n🧪 Testing Original Request First...')
        print('=' * 50)
        
        original_response = self.executor.execute_request(parsed)
        
        if original_response['status'] == 0:
            print(f'❌ Original request failed: {original_response.get("error", "Unknown error")}')
            print('❌ Cannot proceed with testing if original request fails')
            return
        elif original_response['status'] >= 400:
            print(f'⚠️  Original request returned {original_response["status"]}')
            print('⚠️  This might indicate an issue with the curl command or API')
            print('⚠️  Proceeding with tests, but positive test may fail...')
        else:
            print(f'✅ Original request successful: {original_response["status"]}')
            if expected_status == 200 and original_response['status'] in [200, 201, 202]:
                expected_status = original_response['status']
                print(f'🔄 Updated expected status to: {expected_status}')
        
        # Generate comprehensive test cases
        test_cases = self.generator.generate_comprehensive_test_cases(parsed, expected_status)
        
        # Execute tests with progress tracking
        print('\n⏳ Executing Comprehensive Test Suite...')
        print('=' * 60)
        
        category_counts = {}
        for test_case in test_cases:
            cat = test_case['type']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        print('📊 Test Categories:')
        for cat, count in sorted(category_counts.items()):
            print(f'   • {cat}: {count} tests')
        print('')
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                # Show progress
                progress = (i / len(test_cases)) * 100
                print(f'\r🔄 Progress: {progress:.1f}% ({i}/{len(test_cases)}) - {test_case["type"]}', end='', flush=True)
                
                # Execute request
                response = self.executor.execute_request(test_case['request'])
                
                # Add result to reporter
                self.reporter.add_result(test_case, response, test_case['expected_status'])
                
                # Show detailed output for first few tests and every 20th test
                if i <= 5 or i % 20 == 0:
                    status = '✅' if response['status'] != 0 else '❌'
                    print(f'\r{status} Test {i}: {test_case["type"]} → {response["status"]}' + ' ' * 20)
                
                # Rate limiting
                time.sleep(0.05)  # Small delay to be respectful
                
            except Exception as error:
                print(f'\n❌ Error in test {i}: {error}')
                continue
        
        print('\r✅ All comprehensive tests completed!' + ' ' * 50)
        
        # Generate detailed reports
        self.reporter.print_console_summary()
        self.reporter.generate_html_report(curl_command)

    def run_interactive_mode(self):
        """Run in enhanced interactive mode"""
        try:
            self.cli.show_welcome_message()
            
            # Get curl command
            curl_command = self.cli.get_multiline_input('📝 Enter your curl command:')
            
            if not curl_command.strip():
                print('❌ No curl command provided. Exiting...')
                sys.exit(1)
            
            # Show what we got
            print(f'\n✅ Curl command received ({len(curl_command)} characters)')
            print('📋 First 100 characters:', curl_command[:100] + ('...' if len(curl_command) > 100 else ''))
            
            # Get expected status code
            expected_status = self.cli.get_expected_status_code()
            
            # Run comprehensive tests
            self.run_comprehensive_tests(curl_command, expected_status)
            
        except Exception as error:
            print(f'❌ Error: {error}')
            import traceback
            print('Debug info:', traceback.format_exc())


def test_curl_parsing():
    """Test function to debug cURL parsing with your specific command"""
    sample_curl = '''curl --location --request POST 'http://pricing-service.svc.staging.internal/api/fare-estimates' \\
--header 'appversion: 412' \\
--header 'Content-Type: application/json' \\
--header 'user: {"_id":"5f97f46a9663d80a60400ed2"}' \\
--header 'channel-name: app' \\
--header 'city: Vijayawada' \\
--header 'channel-host: android' \\
--data-raw '{    "requestId": "12345",    "requests": [        {            "couponCode": "",            "estimateId": "681082dea18f1427fa75fe88",            "upiAppName": "",            "paymentType": "",            "pickupLocation": {                "lat": 16.514236152,                "lng": 80.6469466315            },            "dropLocation": {                "lat": 16.48522157319,                "lng": 80.7478835212                 },            "services": [                {                    "id": "5bd6c6e2e79cc313a94728d0",                    "serviceDetailId": "611d0b1cd74f4855b6fa061e"                }            ],            "isReturnToOriginOrder": false        }    ]}'
'''
    
    print("🧪 Testing cURL Parsing with Your Sample Command")
    print("=" * 60)
    
    parser = CurlParser()
    result = parser.parse_curl(sample_curl)
    
    print("\n🎯 CRITICAL VALIDATION - USER HEADER:")
    expected_user = '{"_id":"5f97f46a9663d80a60400ed2"}'
    actual_user = result['headers'].get('user', 'NOT FOUND')
    
    print(f"Expected: {expected_user}")
    print(f"Actual  : {actual_user}")
    
    if actual_user == expected_user:
        print("✅ SUCCESS: User header parsed correctly!")
    elif actual_user == 'NOT FOUND':
        print("❌ CRITICAL ERROR: User header not found!")
    elif actual_user == '{':
        print("❌ CRITICAL ERROR: User header truncated!")
    else:
        print("⚠️ WARNING: User header differs from expected!")
    
    print(f"\n📊 All Headers Found ({len(result['headers'])}):")
    for key, value in result['headers'].items():
        status = "✅" if len(value) > 2 else "⚠️"
        print(f"  {status} {key}: {value}")
    
    # Test if this would cause 401
    if actual_user in ['{', 'NOT FOUND', '']:
        print("\n❌ This configuration will likely result in 401 Unauthorized!")
        print("💡 The API expects a valid user ID in the format: {\"_id\":\"...\"}")
    else:
        print("\n✅ Authentication headers look good!")
    
    return result


def main():
    """Enhanced main function"""
    args = parse_arguments()
    tester = EnhancedAPITester()
    
    # Add a test flag for debugging
    if hasattr(args, 'test') and args.test:
        test_curl_parsing()
        return
    
    # If no arguments provided or interactive flag, run interactive mode
    if len(sys.argv) == 1 or args.interactive or not args.curl:
        tester.run_interactive_mode()
        return
    
    # Command line mode
    print('🧪 Running Enhanced API Tests (Command Line Mode)...')
    print('Enhanced by Nitin Sharma\n')
    
    tester.run_comprehensive_tests(args.curl, args.status)


def parse_arguments():
    """Enhanced argument parsing"""
    parser = argparse.ArgumentParser(
        description='🧪 Enhanced Universal REST API Testing Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Enhanced Features:
  🚀 Comprehensive test case generation (100+ scenarios per API)
  🔒 Advanced security testing: XSS, SQL injection, command injection, path traversal
  🎯 Enhanced edge case testing: Unicode, special characters, boundary values
  📊 Real HTTP execution with detailed performance analysis
  📄 Rich HTML reports with category organization and expandable cURL commands
  🛡️  Authentication and authorization testing
  📋 Format validation and structure testing
  🔍 Nested field and array validation
  💾 Large payload and stress testing
  ⏱️  Response time analysis and performance insights

Examples:
  Interactive mode (RECOMMENDED):
    python enhanced_api_tester.py

  Command line mode:
    python enhanced_api_tester.py --curl 'curl -X POST "https://api.example.com/test" -H "Content-Type: application/json" -d "{\"name\":\"test\"}"'

  With expected status:
    python enhanced_api_tester.py --curl 'curl -X POST ...' --status 201

  Test parsing (DEBUG):
    python enhanced_api_tester.py --test

👨‍💻 Enhanced with ❤️  by Nitin Sharma - Comprehensive API Testing Solution
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
        '--interactive', '-i',
        help='Force interactive mode',
        action='store_true',
        default=False
    )
    
    parser.add_argument(
        '--test', '-t',
        help='Test cURL parsing with sample command (DEBUG)',
        action='store_true',
        default=False
    )
    
    return parser.parse_args()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n❌ Operation cancelled by user.')
        sys.exit(1)
    except Exception as error:
        print(f'❌ Fatal error: {error}')
        sys.exit(1)
