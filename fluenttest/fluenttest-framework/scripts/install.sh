#!/bin/bash

# FluentTest Installation Script v1.0
# ===================================

set -e  # Exit on any error

echo "Installing FluentTest Framework v2.0..."

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )[0-9]+\.[0-9]+' || echo "0.0")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi
echo "Python $python_version found"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Appium Server (if Node.js is available)
if command -v npm &> /dev/null; then
    echo "Installing Appium Server..."
    npm install -g appium@next
    
    # Install Appium drivers
    echo "Installing Appium UiAutomator2 driver..."
    appium driver install uiautomator2
else
    echo "Node.js not found. Please install Appium manually:"
    echo "1. Install Node.js from https://nodejs.org"
    echo "2. Run: npm install -g appium@next"
    echo "3. Run: appium driver install uiautomator2"
fi

# Install FluentTest package
echo "Installing FluentTest package..."
pip install -e .

# Create necessary directories
echo "Creating project directories..."
mkdir -p screenshots logs reports

echo ""
echo "FluentTest installation complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Configure your Android device/emulator"
echo "3. Start Appium server: appium"
echo "4. Run example: python examples/basic_example.py"
