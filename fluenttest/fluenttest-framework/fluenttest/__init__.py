# FluentTest - Natural Language UI Automation for Android
# ======================================================
# 
# FluentTest allows you to write UI automation tests using plain English,
# eliminating the need for complex XPath expressions or element locators.
#
# Example:
#     from fluenttest import FluentDriver
#     
#     # Setup with your Appium driver
#     fluent = FluentDriver(appium_driver)
#     
#     # Use natural language
#     fluent.find("click login button")
#     fluent.type_text("username", "email field")

from .nl_ui_locator import FluentDriver
from .runtime_parser import QueryParser
from .test_suite import FluentTestSuite

__version__ = "1.0.0"
__author__ = "FluentTest Team"

__all__ = [
    "FluentDriver",
    "QueryParser", 
    "FluentTestSuite"
]
