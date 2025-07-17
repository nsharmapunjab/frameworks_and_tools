# FluentTest Natural Language UI Locator
# ======================================
# Core module for converting natural language queries into dynamic Appium locators.

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import difflib
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocatorType(Enum):
    """Supported locator types for element identification"""
    XPATH = "xpath"
    ID = "id"
    CLASS_NAME = "class name"
    ACCESSIBILITY_ID = "accessibility id"
    ANDROID_UIAUTOMATOR = "android uiautomator"
    ANDROID_VIEWTAG = "android viewtag"


@dataclass
class UIElement:
    """Represents a UI element with its properties and locator information"""
    tag: str
    text: str
    content_desc: str
    resource_id: str
    class_name: str
    bounds: str
    clickable: bool
    enabled: bool
    scrollable: bool
    checkable: bool
    checked: bool
    selected: bool
    focused: bool
    package: str
    xpath: str
    index: int
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert UIElement to dictionary for JSON serialization"""
        return {
            'tag': self.tag,
            'text': self.text,
            'content_desc': self.content_desc,
            'resource_id': self.resource_id,
            'class_name': self.class_name,
            'bounds': self.bounds,
            'clickable': self.clickable,
            'enabled': self.enabled,
            'scrollable': self.scrollable,
            'checkable': self.checkable,
            'checked': self.checked,
            'selected': self.selected,
            'focused': self.focused,
            'package': self.package,
            'xpath': self.xpath,
            'index': self.index,
            'confidence_score': self.confidence_score
        }


class NaturalLanguageProcessor:
    """Processes natural language queries and matches them to UI elements"""
    
    def __init__(self):
        self.action_keywords = {
            'click': ['click', 'tap', 'press', 'select', 'choose', 'hit'],
            'type': ['type', 'enter', 'input', 'fill', 'write'],
            'scroll': ['scroll', 'swipe', 'slide'],
            'check': ['check', 'tick', 'mark'],
            'uncheck': ['uncheck', 'untick', 'unmark'],
            'wait': ['wait', 'pause', 'delay']
        }
        
        self.element_keywords = {
            'button': ['button', 'btn', 'submit', 'ok', 'cancel', 'yes', 'no'],
            'text': ['text', 'label', 'title', 'heading', 'caption'],
            'input': ['input', 'field', 'textbox', 'textfield', 'edittext'],
            'image': ['image', 'icon', 'picture', 'photo', 'img'],
            'list': ['list', 'listview', 'recyclerview', 'menu'],
            'checkbox': ['checkbox', 'check', 'tick'],
            'radio': ['radio', 'radiobutton', 'option'],
            'switch': ['switch', 'toggle'],
            'spinner': ['spinner', 'dropdown', 'select'],
            'tab': ['tab', 'tabs', 'tabhost'],
            'dialog': ['dialog', 'popup', 'modal', 'alert']
        }
    
    def extract_action(self, query: str) -> str:
        """Extract action from natural language query"""
        query_lower = query.lower()
        
        for action, keywords in self.action_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return action
        
        return 'click'  # Default action
    
    def extract_text_content(self, query: str) -> List[str]:
        """Extract quoted text or specific content from query"""
        # Find text in quotes
        quoted_text = re.findall(r'"([^"]*)"', query)
        quoted_text.extend(re.findall(r"'([^']*)'", query))
        
        if quoted_text:
            return quoted_text
        
        # Extract potential text content
        content_patterns = [
            r'with\s+text\s+["\']*([^"\']+)["\']*',
            r'containing\s+["\']*([^"\']+)["\']*',
            r'labeled\s+["\']*([^"\']+)["\']*',
            r'says\s+["\']*([^"\']+)["\']*'
        ]
        
        extracted_text = []
        for pattern in content_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            extracted_text.extend(matches)
        
        return extracted_text


class FluentDriver:
    """Main FluentTest driver for natural language UI automation"""
    
    def __init__(self, appium_driver, timeout: int = 10):
        self.driver = appium_driver
        self.timeout = timeout
        self.wait = WebDriverWait(appium_driver, timeout)
        self.nlp = NaturalLanguageProcessor()
        
        # Cache for performance
        self.element_cache = {}
        self.page_source_cache = None
        
    def find(self, query: str) -> Optional[WebElement]:
        """Find element using natural language query"""
        try:
            # Extract action and text content
            action = self.nlp.extract_action(query)
            text_content = self.nlp.extract_text_content(query)
            
            # Try different locator strategies
            element = self._try_locator_strategies(query, text_content)
            
            if element:
                logger.info(f"Found element for: {query}")
                return element
            else:
                logger.warning(f"Element not found for: {query}")
                return None
                
        except Exception as e:
            logger.error(f"Error finding element for '{query}': {e}")
            return None
    
    def _try_locator_strategies(self, query: str, text_content: List[str]) -> Optional[WebElement]:
        """Try different locator strategies to find element"""
        strategies = []
        
        # Strategy 1: Text-based search
        if text_content:
            for text in text_content:
                strategies.extend([
                    (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")'),
                    (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{text}")'),
                    (AppiumBy.ACCESSIBILITY_ID, text),
                    (AppiumBy.XPATH, f"//*[@text='{text}']"),
                    (AppiumBy.XPATH, f"//*[contains(@text, '{text}')]")
                ])
        
        # Strategy 2: Content description search
        if 'button' in query.lower():
            strategies.extend([
                (AppiumBy.XPATH, "//android.widget.Button"),
                (AppiumBy.CLASS_NAME, "android.widget.Button"),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.Button")')
            ])
        
        if 'input' in query.lower() or 'field' in query.lower():
            strategies.extend([
                (AppiumBy.XPATH, "//android.widget.EditText"),
                (AppiumBy.CLASS_NAME, "android.widget.EditText"),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.EditText")')
            ])
        
        # Try each strategy
        for locator_type, locator_value in strategies:
            try:
                element = self.driver.find_element(locator_type, locator_value)
                if element and element.is_displayed():
                    return element
            except NoSuchElementException:
                continue
            except Exception as e:
                logger.debug(f"Strategy failed {locator_type}={locator_value}: {e}")
                continue
        
        return None
    
    def click(self, query: str) -> bool:
        """Click element found by natural language query"""
        element = self.find(query)
        if element:
            element.click()
            return True
        return False
    
    def type_text(self, text: str, field_query: str) -> bool:
        """Type text into field found by natural language query"""
        element = self.find(field_query)
        if element:
            element.clear()
            element.send_keys(text)
            return True
        return False
    
    def wait_for(self, query: str, timeout: Optional[int] = None) -> Optional[WebElement]:
        """Wait for element to appear"""
        timeout = timeout or self.timeout
        
        try:
            return WebDriverWait(self.driver, timeout).until(
                lambda driver: self.find(query)
            )
        except TimeoutException:
            logger.warning(f"Element not found within {timeout} seconds: {query}")
            return None
    
    def is_present(self, query: str) -> bool:
        """Check if element is present"""
        return self.find(query) is not None
    
    def get_text(self, query: str) -> Optional[str]:
        """Get text from element"""
        element = self.find(query)
        return element.text if element else None
