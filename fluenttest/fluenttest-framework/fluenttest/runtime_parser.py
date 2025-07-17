# FluentTest Runtime Parser
# ========================
# Advanced query processing engine for natural language patterns.

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of natural language queries"""
    SIMPLE_ACTION = "simple_action"
    CONDITIONAL = "conditional"
    SEQUENCE = "sequence"
    CONTEXTUAL = "contextual"
    DESCRIPTIVE = "descriptive"


@dataclass
class ParsedQuery:
    """Parsed natural language query with structured information"""
    original_query: str
    query_type: QueryType
    action: str
    target_element: Dict[str, Any]
    modifiers: Dict[str, Any]
    conditions: List[Dict[str, Any]]
    confidence: float


class QueryParser:
    """Advanced natural language query parser"""
    
    def __init__(self):
        self.action_patterns = {
            'click': r'(?:click|tap|press|select)\s+(.+)',
            'type': r'(?:type|enter|input)\s+"([^"]+)"\s+(?:in|into)\s+(.+)',
            'scroll': r'(?:scroll|swipe)\s+(up|down|left|right)',
            'wait': r'wait\s+(?:for\s+)?(.+)',
            'verify': r'(?:verify|check|assert)\s+(?:that\s+)?(.+)'
        }
        
        self.element_patterns = {
            'button': r'(?:button|btn)(?:\s+(?:with|containing|labeled)\s+"([^"]+)")?',
            'input': r'(?:input|field|textbox)(?:\s+(?:with|containing|labeled)\s+"([^"]+)")?',
            'text': r'(?:text|label)(?:\s+(?:with|containing|saying)\s+"([^"]+)")?'
        }
    
    def parse(self, query: str) -> ParsedQuery:
        """Parse natural language query"""
        query = query.strip().lower()
        
        # Determine query type
        query_type = self._classify_query(query)
        
        # Extract action
        action = self._extract_action(query)
        
        # Extract target element info
        target_element = self._extract_target_element(query)
        
        # Extract modifiers
        modifiers = self._extract_modifiers(query)
        
        # Extract conditions for conditional queries
        conditions = self._extract_conditions(query)
        
        # Calculate confidence
        confidence = self._calculate_confidence(query, action, target_element)
        
        return ParsedQuery(
            original_query=query,
            query_type=query_type,
            action=action,
            target_element=target_element,
            modifiers=modifiers,
            conditions=conditions,
            confidence=confidence
        )
    
    def _classify_query(self, query: str) -> QueryType:
        """Classify the type of query"""
        if re.search(r'\bif\b|\bwhen\b|\bunless\b', query):
            return QueryType.CONDITIONAL
        elif re.search(r'\bthen\b|\bafter\b|\bnext\b', query):
            return QueryType.SEQUENCE
        elif re.search(r'\bcontaining\b|\bwith\b|\bthat\b', query):
            return QueryType.DESCRIPTIVE
        else:
            return QueryType.SIMPLE_ACTION
    
    def _extract_action(self, query: str) -> str:
        """Extract the main action from query"""
        for action, pattern in self.action_patterns.items():
            if re.search(pattern, query):
                return action
        
        # Default action detection
        if any(word in query for word in ['click', 'tap', 'press']):
            return 'click'
        elif any(word in query for word in ['type', 'enter', 'input']):
            return 'type'
        elif any(word in query for word in ['scroll', 'swipe']):
            return 'scroll'
        else:
            return 'click'  # Default
    
    def _extract_target_element(self, query: str) -> Dict[str, Any]:
        """Extract target element information"""
        target = {
            'element_type': None,
            'text_content': [],
            'attributes': {}
        }
        
        # Extract quoted text
        quoted_text = re.findall(r'"([^"]*)"', query)
        if quoted_text:
            target['text_content'] = quoted_text
        
        # Extract element type
        for element_type, pattern in self.element_patterns.items():
            if re.search(pattern, query):
                target['element_type'] = element_type
                break
        
        return target
    
    def _extract_modifiers(self, query: str) -> Dict[str, Any]:
        """Extract query modifiers"""
        modifiers = {}
        
        # Extract timing
        if 'slowly' in query:
            modifiers['speed'] = 'slow'
        elif 'quickly' in query:
            modifiers['speed'] = 'fast'
        
        # Extract wait times
        wait_match = re.search(r'wait\s+(\d+)\s*(?:second|sec)', query)
        if wait_match:
            modifiers['wait_time'] = int(wait_match.group(1))
        
        return modifiers
    
    def _extract_conditions(self, query: str) -> List[Dict[str, Any]]:
        """Extract conditional statements"""
        conditions = []
        
        # Look for conditional patterns
        if_match = re.search(r'if\s+(.+?)\s+then', query)
        if if_match:
            conditions.append({
                'type': 'if',
                'condition': if_match.group(1)
            })
        
        return conditions
    
    def _calculate_confidence(self, query: str, action: str, target: Dict[str, Any]) -> float:
        """Calculate confidence score for the parsed query"""
        confidence = 0.5  # Base confidence
        
        # Boost for clear actions
        if action in ['click', 'type', 'scroll']:
            confidence += 0.2
        
        # Boost for quoted text
        if target['text_content']:
            confidence += 0.2
        
        # Boost for element type
        if target['element_type']:
            confidence += 0.1
        
        return min(confidence, 1.0)
