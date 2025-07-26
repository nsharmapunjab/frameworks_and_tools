# 🚀 FluentTest Generator v1.0

**Natural Language UI Automation Framework Generator for Android Apps**

FluentTest Generator is a **single-script tool** that interactively generates a complete, production-ready Python framework for UI automation using natural language queries.

---

## How to Use

### Step 1: Save the Script  
Save the generator file as:

```bash
fluenttest_generator.py

Step 2: Run the Script

Execute the script:
python fluenttest_generator.py

Step 3: Follow the Prompts

The generator will:
    •Display an ASCII banner
    •Prompt for project name (default: fluenttest-framework)
    •Check and avoid overwriting existing directories
    •Generate a full-featured framework
    •Show a tree structure of the project
    •Offer to install dependencies automatically

-->What’s Generated

📁 Project Structure
fluenttest-framework/
├── fluenttest/                    # Main Python package
│   ├── __init__.py
│   ├── nl_ui_locator.py          # Core locator engine
│   ├── runtime_parser.py         # Query processor
│   └── test_suite.py             # Test framework
├── examples/                     # Ready-to-run examples
│   ├── basic_example.py
│   └── advanced_example.py
├── scripts/                      # Installation scripts
│   ├── install.sh                # Mac/Linux installer
│   └── install.bat               # Windows installer
├── config/
│   └── default_config.json       # Default configuration
├── docs/
│   └── user_guide.md             # User guide
├── requirements.txt              # Python dependencies
├── setup.py                      # Python packaging
├── README.md                     # This file
├── Makefile                      # Build automation
└── LICENSE                       # MIT License

-->Key Features
    • Natural Language UI Locator with smart element discovery
    • Advanced Query Parser for complex NL queries
    • Integrated Test Suite with HTML reporting
    • One-Click Installation for Windows/Mac/Linux
    • Ready-to-Run Examples
    • Professional Documentation
    • Makefile Support for CI integration
    • Proper Python Packaging (setup.py)


-->Interactive Experience

Here’s a glimpse of the banner you’ll see:

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    ███████╗██╗     ██╗   ██╗███████╗███╗   ██╗████████╗      ║
║    ██╔════╝██║     ██║   ██║██╔════╝████╗  ██║╚══██╔══╝      ║
║    █████╗  ██║     ██║   ██║█████╗  ██╔██╗ ██║   ██║         ║
║    ██╔══╝  ██║     ██║   ██║██╔══╝  ██║╚██╗██║   ██║         ║
║    ██║     ███████╗╚██████╔╝███████╗██║ ╚████║   ██║         ║
║    ╚═╝     ╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝         ║
║                                                               ║
║              Natural Language UI Automation                   ║
║                     Framework Generator                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

-->Quick Start After Generation

cd fluenttest-framework

# Install dependencies (optional if chosen during generation)
./scripts/install.sh         # or scripts\install.bat on Windows

# Activate virtual environment
source venv/bin/activate

# Start Appium (in a separate terminal)
appium

# Run examples
python examples/basic_example.py
python examples/advanced_example.py


-->Why Choose This Generator?
    • Single File Deployment: One Python script to distribute
    • Interactive & User-Friendly: No config, no manual steps
    • Fully Structured: Framework with modules, examples, docs
    • Cross-Platform: Compatible with Windows, Mac, and Linux
    • Ready for Testing: Works out-of-the-box
    • Includes Docs & Best Practices
    • Zero Manual Work: Everything is automated!

---

## 📞 Contact

- **📧 Email**: [nsharmapunjab@gmail.com](mailto:nsharmapunjab@gmail.com)
- **💼 LinkedIn**: [Connect with me](https://www.linkedin.com/in/nitin-sharma-23512743/)
- **🌐 Website**: [Learn with Nitin](https://learnwithnitin.blogspot.com/)

---

## 🌟 Support the Project

If this tool has helped you in your UI testing journey, consider:

- ⭐ **Starring** the repository
- 🐛 **Reporting** bugs and issues
- 💡 **Suggesting** new features
- 🤝 **Contributing** code improvements
- 📢 **Sharing** with your team and network

---

**Made with ❤️  by Nitin Sharma**

*Happy UI Testing! 🚀*
