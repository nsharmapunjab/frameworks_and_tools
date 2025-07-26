#!/usr/bin/env python3
"""
Script to create all necessary files for the Kafka E2E Test Tool
Run this script to set up the complete project structure
"""

import os
from pathlib import Path

def create_file(filepath, content):
    """Create a file with the given content"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"✅ Created: {filepath}")

def main():
    print("🚀 Setting up Kafka E2E Test Tool project structure...")
    
    # Create __init__.py files
    init_files = [
        "src/__init__.py",
        "src/config/__init__.py", 
        "src/kafka/__init__.py",
        "src/validators/__init__.py",
        "src/reports/__init__.py",
        "src/utils/__init__.py"
    ]
    
    for init_file in init_files:
        create_file(init_file, "# Package initialization\n")
    
    # Create logger module
    logger_content = '''import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logger(name: str, log_file=None, verbose: bool = False):
    """Setup logger with console and optional file output"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
'''
    create_file("src/utils/logger.py", logger_content)
    
    # Create config parser module
    config_parser_content = '''import json
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
'''
    create_file("src/config/config_parser.py", config_parser_content)
    
    # Create kafka manager module
    kafka_manager_content = '''import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class KafkaMessage:
    """Represents a Kafka message"""
    key: Optional[str]
    value: str
    topic: str
    partition: int
    offset: int
    timestamp: datetime
    headers: Dict[str, str]

class MockKafkaManager:
    """Mock Kafka implementation"""
    
    def __init__(self):
        self.messages = {}
        self.consumers = {}
    
    def produce_message(self, topic: str, message: str, key: Optional[str] = None) -> bool:
        if topic not in self.messages:
            self.messages[topic] = []
        
        kafka_msg = KafkaMessage(
            key=key,
            value=message,
            topic=topic,
            partition=0,
            offset=len(self.messages[topic]),
            timestamp=datetime.now(),
            headers={}
        )
        
        self.messages[topic].append(kafka_msg)
        return True
    
    def consume_messages(self, topic: str, timeout: int = 30):
        if topic not in self.consumers:
            self.consumers[topic] = 0
        
        if topic in self.messages:
            available_messages = self.messages[topic][self.consumers[topic]:]
            for msg in available_messages:
                self.consumers[topic] += 1
                yield msg
    
    def reset_topic(self, topic: str):
        if topic in self.messages:
            self.messages[topic] = []
        if topic in self.consumers:
            self.consumers[topic] = 0

class KafkaManager:
    """Kafka manager with mock support"""
    
    def __init__(self, bootstrap_servers: str, use_mock: bool = False):
        self.bootstrap_servers = bootstrap_servers
        self.use_mock = use_mock
        
        if use_mock:
            self.mock_manager = MockKafkaManager()
        else:
            self.mock_manager = None
            try:
                # Try to import kafka-python
                from kafka import KafkaProducer, KafkaConsumer
                self.producer = KafkaProducer(
                    bootstrap_servers=bootstrap_servers,
                    value_serializer=lambda v: v.encode('utf-8')
                )
            except ImportError:
                print("Warning: kafka-python not installed. Using mock mode.")
                self.use_mock = True
                self.mock_manager = MockKafkaManager()
    
    def produce_message(self, topic: str, message: str, key: Optional[str] = None) -> bool:
        if self.use_mock:
            return self.mock_manager.produce_message(topic, message, key)
        
        try:
            future = self.producer.send(topic, value=message, key=key)
            future.get(timeout=10)
            return True
        except Exception as e:
            print(f"Failed to produce message: {e}")
            return False
    
    def produce_messages_batch(self, topic: str, messages: List[str]) -> Dict[str, Any]:
        start_time = time.time()
        success_count = 0
        
        for message in messages:
            if self.produce_message(topic, message):
                success_count += 1
        
        end_time = time.time()
        
        return {
            'total_messages': len(messages),
            'success_count': success_count,
            'failed_count': len(messages) - success_count,
            'duration_seconds': end_time - start_time,
            'messages_per_second': len(messages) / (end_time - start_time) if end_time > start_time else 0
        }
    
    def consume_messages(self, topic: str, timeout: int = 30, max_messages: Optional[int] = None) -> List[KafkaMessage]:
        if self.use_mock:
            messages = []
            for msg in self.mock_manager.consume_messages(topic, timeout):
                messages.append(msg)
                if max_messages and len(messages) >= max_messages:
                    break
            return messages
        
        # Real Kafka implementation would go here
        return []
    
    def cleanup(self):
        if not self.use_mock and hasattr(self, 'producer'):
            self.producer.close()
'''
    create_file("src/kafka/kafka_manager.py", kafka_manager_content)
    
    # Create test validator module
    test_validator_content = '''import time
from datetime import datetime
from typing import List, Dict, Any

class TestValidator:
    """Test validator with basic validation strategies"""
    
    def __init__(self, kafka_manager):
        self.kafka_manager = kafka_manager
    
    def run_all_tests(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run all test cases"""
        test_results = []
        
        for test_case in config.get('test_cases', []):
            if not test_case.get('enabled', True):
                continue
            
            result = self._run_single_test(test_case, config)
            test_results.append(result)
        
        return test_results
    
    def _run_single_test(self, test_case: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case"""
        start_time = datetime.now()
        
        try:
            messages = test_case.get('messages', [])
            if not messages:
                return self._create_error_result(test_case, start_time, "No test messages specified")
            
            # Reset mock topics if using mock
            if self.kafka_manager.use_mock:
                producer_topic = config['kafka']['producer']['topic']
                consumer_topic = config['kafka']['consumer']['topic']
                self.kafka_manager.mock_manager.reset_topic(producer_topic)
                self.kafka_manager.mock_manager.reset_topic(consumer_topic)
            
            # Produce messages
            producer_topic = config['kafka']['producer']['topic']
            production_stats = self.kafka_manager.produce_messages_batch(producer_topic, messages)
            
            # Small delay
            time.sleep(0.1)
            
            # Consume messages
            consumer_topic = config['kafka']['consumer']['topic']
            timeout = config.get('validation_config', {}).get('timeout', 30)
            consumed_messages = self.kafka_manager.consume_messages(consumer_topic, timeout=timeout)
            
            # Basic validation - check if all messages were delivered
            consumed_values = [msg.value for msg in consumed_messages]
            missing_messages = [msg for msg in messages if msg not in consumed_values]
            
            validation_results = {
                'delivery': {
                    'success': len(missing_messages) == 0,
                    'produced_count': len(messages),
                    'consumed_count': len(consumed_messages),
                    'missing_messages': missing_messages
                }
            }
            
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            status = 'PASSED' if validation_results['delivery']['success'] else 'FAILED'
            
            return {
                'test_name': test_case['name'],
                'description': test_case.get('description', ''),
                'status': status,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_ms': duration_ms,
                'production_stats': production_stats,
                'consumption_stats': {'messages_consumed': len(consumed_messages)},
                'validation_results': validation_results,
                'errors': []
            }
            
        except Exception as e:
            return self._create_error_result(test_case, start_time, str(e))
    
    def _create_error_result(self, test_case: Dict[str, Any], start_time: datetime, error: str):
        """Create error result"""
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        return {
            'test_name': test_case['name'],
            'description': test_case.get('description', ''),
            'status': 'FAILED',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_ms': duration_ms,
            'production_stats': {},
            'consumption_stats': {},
            'validation_results': {},
            'errors': [error]
        }
'''
    create_file("src/validators/test_validator.py", test_validator_content)
    
    # Create HTML reporter module
    html_reporter_content = '''import json
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

class HTMLReporter:
    """Simple HTML report generator"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, test_results: List[Dict[str, Any]], config: Dict[str, Any]) -> str:
        """Generate simple HTML report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"kafka-e2e-report-{timestamp}.html"
        report_path = self.output_dir / report_filename
        
        # Calculate summary
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result['status'] == 'PASSED')
        failed_tests = total_tests - passed_tests
        
        # Generate simple HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Kafka E2E Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ background: #e8f5e8; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .test-result {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .passed {{ background: #d4edda; }}
        .failed {{ background: #f8d7da; }}
        pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Kafka E2E Test Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Bootstrap Servers:</strong> {config.get('kafka', {}).get('bootstrap_servers', 'N/A')}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Tests:</strong> {total_tests}</p>
        <p><strong>Passed:</strong> {passed_tests}</p>
        <p><strong>Failed:</strong> {failed_tests}</p>
        <p><strong>Pass Rate:</strong> {(passed_tests/total_tests*100):.1f}%</p>
    </div>
    
    <h2>Test Results</h2>
"""
        
        for result in test_results:
            status_class = result['status'].lower()
            html_content += f"""
    <div class="test-result {status_class}">
        <h3>{result['status']} - {result['test_name']}</h3>
        <p><strong>Description:</strong> {result.get('description', 'N/A')}</p>
        <p><strong>Duration:</strong> {result.get('duration_ms', 0):.2f} ms</p>
        <details>
            <summary>Details</summary>
            <pre>{json.dumps(result, indent=2)}</pre>
        </details>
    </div>
"""
        
        html_content += """
    <h2>Configuration</h2>
    <pre>{}</pre>
</body>
</html>
""".format(json.dumps(config, indent=2))
        
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        return str(report_path)
'''
    create_file("src/reports/html_reporter.py", html_reporter_content)
    
    # Create directories
    dirs_to_create = [
        "test-results",
        "test-results/logs", 
        "schemas",
        "examples"
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {dir_path}")
    
    # Create a simple requirements.txt
    requirements_content = """# Core dependencies
click>=8.0.0
PyYAML>=6.0

# Kafka (optional - will use mock if not available)
kafka-python>=2.0.2

# Validation (optional)
jsonschema>=4.0.0

# Testing with containers (optional)
testcontainers>=3.4.0
"""
    create_file("requirements.txt", requirements_content)
    
    # Create a sample config file
    sample_config = """{
  "kafka": {
    "bootstrap_servers": "localhost:9092",
    "producer": {
      "topic": "test-producer-topic",
      "config": {
        "acks": "all",
        "retries": 3
      }
    },
    "consumer": {
      "topic": "test-consumer-topic", 
      "config": {
        "group_id": "kafka-e2e-test-group",
        "auto_offset_reset": "earliest"
      }
    }
  },
  "test_cases": [
    {
      "name": "basic_message_flow",
      "description": "Basic producer-consumer message flow test",
      "enabled": true,
      "messages": [
        "Hello, Kafka E2E Testing!",
        "Message 2",
        "Final test message"
      ],
      "validations": ["delivery"]
    }
  ],
  "validation_config": {
    "timeout": 30,
    "max_latency_ms": 5000,
    "expected_order": true,
    "allow_duplicates": false,
    "retry_attempts": 3
  }
}"""
    create_file("examples/sample-config.json", sample_config)
    
    # Create a README for quick start
    readme_content = """# Kafka E2E Test Tool - Quick Start

## Setup
1. Run the setup: `python3 create_files.py`
2. Install dependencies: `pip3 install --user click PyYAML` (optional: kafka-python)

## Usage

### Basic test with mock Kafka (no Kafka cluster needed):
```bash
python3 main.py run-test --producer-topic test --consumer-topic test --use-mock --verbose
```

### Generate a sample configuration:
```bash
python3 main.py generate-config --output my-config.json --format json
```

### Run with configuration file:
```bash
python3 main.py run-test --config examples/sample-config.json --use-mock
```

### View latest report:
```bash
python3 main.py report
```

## Features
- ✅ Mock Kafka support (no real Kafka needed for testing)
- ✅ Configuration-driven tests (JSON/YAML)
- ✅ HTML report generation
- ✅ Fallback mode (works even without Click/PyYAML)
- ✅ Message delivery validation
- ✅ Extensible architecture

The tool automatically falls back to mock mode if kafka-python is not installed, and uses argparse if Click is not available.
"""
    create_file("README.md", readme_content)
    
    print("\n🎉 Project setup complete!")
    print("\n📋 Next steps:")
    print("1. Install basic dependencies: pip3 install --user click PyYAML")
    print("2. Test the tool: python3 main.py run-test --producer-topic test --consumer-topic test --use-mock")
    print("3. Check the generated report in ./test-results/")
    print("\n💡 The tool works even without kafka-python - it will use mock mode automatically!")

if __name__ == "__main__":
    main()
