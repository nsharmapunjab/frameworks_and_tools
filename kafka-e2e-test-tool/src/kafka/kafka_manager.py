import time
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
