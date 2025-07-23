import json
from pathlib import Path
from typing import Dict, Any, List

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

class ConfigParser:
    """Simple configuration parser"""
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            if config_file.suffix.lower() in ['.yaml', '.yml'] and HAS_YAML:
                return yaml.safe_load(f)
            else:
                return json.load(f)
    
    def create_default_config(self, producer_topic: str, consumer_topic: str, 
                            bootstrap_servers: str, messages: List[str], 
                            timeout: int) -> Dict[str, Any]:
        """Create default configuration"""
        return {
            "kafka": {
                "bootstrap_servers": bootstrap_servers,
                "producer": {
                    "topic": producer_topic,
                    "config": {"acks": "all", "retries": 3}
                },
                "consumer": {
                    "topic": consumer_topic,
                    "config": {
                        "group_id": "kafka-e2e-test-group",
                        "auto_offset_reset": "earliest"
                    }
                }
            },
            "test_cases": [
                {
                    "name": "basic_message_flow",
                    "description": "Basic producer-consumer test",
                    "enabled": True,
                    "messages": messages,
                    "validations": ["delivery"]
                }
            ],
            "validation_config": {
                "timeout": timeout,
                "max_latency_ms": 5000,
                "expected_order": True,
                "allow_duplicates": False,
                "retry_attempts": 3
            }
        }
    
    def generate_sample_config(self, producer_topic: str, consumer_topic: str, format: str = 'yaml'):
        """Generate sample configuration"""
        return {
            "kafka": {
                "bootstrap_servers": "localhost:9092",
                "producer": {
                    "topic": producer_topic,
                    "config": {"acks": "all", "retries": 3}
                },
                "consumer": {
                    "topic": consumer_topic,
                    "config": {
                        "group_id": "kafka-e2e-test-group",
                        "auto_offset_reset": "earliest"
                    }
                }
            },
            "test_cases": [
                {
                    "name": "basic_test",
                    "description": "Basic message flow test",
                    "enabled": True,
                    "messages": ["Hello Kafka!", "Test Message 2"],
                    "validations": ["delivery", "order"]
                }
            ],
            "validation_config": {
                "timeout": 30,
                "max_latency_ms": 5000,
                "expected_order": True,
                "allow_duplicates": False
            }
        }
