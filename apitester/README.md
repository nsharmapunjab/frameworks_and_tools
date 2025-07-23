# 🧪 Universal REST API Testing Tool

**A comprehensive, production-ready API testing tool that generates 50+ test cases from a single cURL command.**

Transform your manual API testing into automated comprehensive test suites with security, edge case, and boundary testing - all from just pasting your cURL command!

## 🚀 Features

### 🎯 **Core Capabilities**
- **📝 cURL Command Parsing**: Convert any cURL command into comprehensive test cases
- **🔄 Auto-Detection**: Smart HTTP method detection (POST, GET, PUT, DELETE, etc.)
- **📊 50+ Test Cases**: Generates positive, negative, security, and edge case tests
- **⚡ Real HTTP Execution**: Actually makes requests to your API endpoints
- **📄 Beautiful HTML Reports**: Interactive reports with filtering and search
- **🔍 Response Time Analysis**: Performance insights for each test case

### 🔒 **Security Testing**
- **XSS Injection**: Cross-site scripting vulnerability detection
- **SQL Injection**: Database injection attack testing
- **NoSQL Injection**: MongoDB and similar database testing
- **Command Injection**: System command execution prevention
- **Path Traversal**: Directory traversal attack detection
- **LDAP Injection**: LDAP query manipulation testing
- **XXE Attacks**: XML External Entity vulnerability testing

### 🎯 **Edge Case Testing**
- **Boundary Values**: Maximum/minimum number testing
- **Long Strings**: 1000+ character input validation
- **Special Characters**: Unicode, symbols, escape sequences
- **Empty/Null Values**: Missing data handling
- **Type Mismatches**: Wrong data type validation
- **Header Manipulation**: Content-Type and authorization testing

### 📊 **Test Categories**
1. **Positive Tests** - Valid request validation
2. **Missing Field Tests** - Required field validation
3. **Type Mismatch Tests** - Data type validation
4. **Null/Empty Tests** - Empty value handling
5. **Security Tests** - Vulnerability detection
6. **Edge Case Tests** - Boundary condition testing
7. **Header Tests** - HTTP header validation
8. **Method Tests** - HTTP method validation
9. **URL Tests** - Endpoint existence validation

## 🛠️ Tech Stack

### **Core Technologies**
- **Python 3.7+** - Main programming language
- **Requests Library** - HTTP client for making API calls
- **Regular Expressions** - cURL command parsing
- **JSON** - Data serialization and parsing
- **HTML/CSS/JavaScript** - Interactive report generation

### **Dependencies**
```bash
requests>=2.25.0
```

### **Standard Library Modules**
- `argparse` - Command line argument parsing
- `json` - JSON data handling
- `re` - Regular expression operations
- `time` - Performance timing
- `datetime` - Timestamp generation
- `copy` - Deep object copying
- `random` - Test data generation
- `typing` - Type hints for better code quality

## 📦 Installation

### **Prerequisites**
- Python 3.7 or higher
- pip package manager

### **Quick Install**
```bash
# Clone the repository
git clone https://github.com/nsharmapunjab/frameworks_and_tools.git
cd apitester

# Install dependencies
pip install requests

# Make executable (Linux/Mac)
chmod +x api_tester.py

# Run the tool
python api_tester.py
```

## 🚀 Quick Start

### **Method 1: Interactive Mode (Recommended)**
```bash
python api_tester.py
```

Follow the prompts:
1. Paste your cURL command
2. Set expected status code (default: 200)
3. Optionally set expected response JSON
4. Watch comprehensive tests execute!

### **Method 2: Command Line Mode**
```bash
python api_tester.py --curl "curl -X POST 'https://api.example.com/users' -H 'Content-Type: application/json' -d '{\"name\":\"John\"}'"
```

### **Method 3: Quick Demo**
```bash
python api_tester.py --sample
```

## 📖 Usage Guide

### **Basic Usage**

#### **1. Interactive Mode**
```bash
python api_tester.py
```

**Example Session:**
```
🧪 Universal REST API Testing Tool
==================================
   Built by Nitin Sharma

📝 Enter your curl command:
> curl --location 'https://api.restful-api.dev/objects' \
> --header 'Content-Type: application/json' \
> --data '{
>   "name": "Apple MacBook Pro 16",
>   "data": {
>     "year": 2019,
>     "price": 1849.99
>   }
> }'
> 

🔢 Enter expected status code (default: 200): 201
✅ Expected status code set to: 201

🎯 Enter expected response JSON (or press Enter to skip): 
✅ Skipping response validation

🚀 Starting API Test Suite
===============================
📡 Target: POST https://api.restful-api.dev/objects
✅ Original request successful: 201 Created
🎯 Generated 68 total test cases

✅ All tests completed!
📄 HTML Report Generated: api-test-report-2024-01-15_14-30-25.html
```

#### **2. Command Line Mode**
```bash
# Basic usage
python api_tester.py --curl "your_curl_command_here"

# With custom expected status
python api_tester.py --curl "your_curl_command" --status 201

# With expected response validation
python api_tester.py --curl "your_curl_command" --response '{"status":"success"}'
```

### **Advanced Usage**

#### **Testing Different HTTP Methods**

**GET Request:**
```bash
python api_tester.py --curl "curl -X GET 'https://api.example.com/users/123' -H 'Authorization: Bearer token'"
```

**PUT Request:**
```bash
python api_tester.py --curl "curl -X PUT 'https://api.example.com/users/123' -H 'Content-Type: application/json' -d '{\"name\":\"Updated Name\"}'"
```

**DELETE Request:**
```bash
python api_tester.py --curl "curl -X DELETE 'https://api.example.com/users/123' -H 'Authorization: Bearer token'"
```

#### **Complex JSON Data:**
```bash
python api_tester.py --curl "curl -X POST 'https://api.example.com/orders' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer your-token' \
-d '{
  \"customer\": {
    \"name\": \"John Doe\",
    \"email\": \"john@example.com\"
  },
  \"items\": [
    {\"product_id\": 1, \"quantity\": 2},
    {\"product_id\": 2, \"quantity\": 1}
  ],
  \"total\": 299.99
}'"
```

### **Understanding Test Results**

#### **Test Categories Explained:**

1. **✅ Positive Tests**: Validates your original request works
2. **❌ Negative - Missing Field**: Tests what happens when required fields are missing
3. **❌ Negative - Type Mismatch**: Tests wrong data types (string vs number)
4. **❌ Negative - Null Value**: Tests null/empty value handling
5. **🔒 Security Tests**: Tests for common vulnerabilities
6. **🎯 Edge Case Tests**: Tests boundary conditions
7. **📋 Header Tests**: Tests header manipulation
8. **🔧 Method Tests**: Tests wrong HTTP methods
9. **🌐 URL Tests**: Tests non-existent endpoints

#### **HTML Report Features:**
- **📊 Statistics Dashboard**: Pass/fail rates and category breakdown
- **🔍 Test Details Table**: Complete test results with response codes
- **📋 Expandable cURL Commands**: Click to see exact request for each test
- **⏱️ Performance Metrics**: Response times for each test
- **📱 Mobile Responsive**: Works on all device sizes

## ⚙️ Configuration Options

### **Command Line Arguments**
```bash
python api_tester.py [OPTIONS]

Options:
  --curl, -c COMMAND     cURL command to test
  --status, -s CODE      Expected success status code (default: 200)
  --response, -r JSON    Expected response JSON (optional)
  --interactive, -i      Force interactive mode
  --sample              Use built-in sample for quick testing
  --help, -h            Show help message
```

### **Environment Variables**
```bash
# Set default timeout (optional)
export API_TESTER_TIMEOUT=30

# Set default rate limiting (optional)
export API_TESTER_DELAY=0.1
```

## 🎯 Examples

### **E-commerce API Testing**
```bash
# Test product creation
python api_tester.py --curl "curl -X POST 'https://shop-api.com/products' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...' \
-d '{
  \"name\": \"Wireless Headphones\",
  \"price\": 199.99,
  \"category\": \"Electronics\",
  \"stock\": 50
}'" --status 201
```

### **User Authentication API**
```bash
# Test user login
python api_tester.py --curl "curl -X POST 'https://auth-api.com/login' \
-H 'Content-Type: application/json' \
-d '{
  \"email\": \"user@example.com\",
  \"password\": \"securePassword123\"
}'" --response '{"token":"jwt_token","user_id":123}'
```

### **File Upload API**
```bash
# Test file upload endpoint
python api_tester.py --curl "curl -X POST 'https://api.example.com/upload' \
-H 'Authorization: Bearer token' \
-F 'file=@document.pdf' \
-F 'description=Important document'"
```

## 🔧 Troubleshooting

### **Common Issues & Solutions**

#### **Issue: 405 Method Not Allowed**
**Solution:** Ensure your cURL command has the correct HTTP method
```bash
# Add explicit method if missing
curl -X POST 'https://api.example.com/endpoint' ...
```

#### **Issue: cURL Parsing Errors**
**Solution:** Use command line mode for complex commands
```bash
python api_tester.py --curl 'your_entire_curl_command_in_quotes'
```

#### **Issue: JSON Parsing Errors**
**Solution:** Escape quotes properly in JSON data
```bash
# Correct format
-d '{\"key\":\"value\"}'

# Or use single quotes
-d '{"key":"value"}'
```

#### **Issue: Connection Timeouts**
**Solution:** Check your internet connection and API availability
```bash
# Test the cURL manually first
curl -X POST 'https://api.example.com/test' -v
```

### **Debug Mode**
Enable verbose output to troubleshoot issues:
```bash
# The tool automatically shows debug information
python api_tester.py --curl "your_command" 2>&1 | tee debug.log
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### **Ways to Contribute**
- 🐛 **Bug Reports**: Found an issue? Please report it!
- ✨ **Feature Requests**: Have an idea? We'd love to hear it!
- 📖 **Documentation**: Help improve our docs
- 🧪 **Test Cases**: Add more test scenarios
- 🔧 **Code**: Submit pull requests with improvements

### **Development Setup**
```bash
# Fork and clone the repository
git clone https://github.com/nsharmapunjab/frameworks_and_tools.git
cd apitester

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Submit your changes
git add .
git commit -m "Your meaningful commit message"
git push origin your-feature-branch
```

### **Coding Standards**
- Follow PEP 8 style guidelines
- Add type hints for better code quality
- Include docstrings for all functions
- Write tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Nitin Sharma

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 📈 Roadmap

### **Upcoming Features**
- [ ] **GraphQL Support**: Testing for GraphQL APIs
- [ ] **OpenAPI Integration**: Import from Swagger/OpenAPI specs
- [ ] **CI/CD Integration**: GitHub Actions, Jenkins plugins
- [ ] **Database Testing**: SQL injection with real database connections
- [ ] **Load Testing**: Performance testing capabilities
- [ ] **Mock Server**: Built-in mock server for testing
- [ ] **Test Templates**: Pre-built test templates for common APIs
- [ ] **API Documentation Generation**: Auto-generate API docs from tests

---

## 📞 Contact

- **📧 Email**: [nsharmapunjab@gmail.com](mailto:nsharmapunjab@gmail.com)
- **💼 LinkedIn**: [Connect with me](https://www.linkedin.com/in/nitin-sharma-23512743/)
- **🌐 Website**: [Learn with Nitin](https://learnwithnitin.blogspot.com/)

---

## 🌟 Support the Project

If this tool has helped you in your API testing journey, consider:

- ⭐ **Starring** the repository
- 🐛 **Reporting** bugs and issues
- 💡 **Suggesting** new features
- 🤝 **Contributing** code improvements
- 📢 **Sharing** with your team and network

---

**Made with ❤️  by Nitin Sharma**

*Happy API Testing! 🚀*
