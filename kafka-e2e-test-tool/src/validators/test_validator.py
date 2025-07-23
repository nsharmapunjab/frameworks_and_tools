import time
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
