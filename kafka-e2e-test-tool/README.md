# 🚀 Kafka E2E Test Tool
-- Built by Nitin Sharma

A production-ready CLI tool for comprehensive end-to-end testing of Kafka-based systems. Validate message flows, measure latency, detect duplicates, and ensure schema conformity with ease.

## ✨ Features

### Core Capabilities
- **End-to-End Message Flow Testing** - Validate complete producer-to-consumer message flows
- **Multiple Validation Strategies** - Order, schema, latency, duplicate detection, and retry behavior
- **Mock Kafka Support** - Test without a real Kafka cluster using built-in mocks
- **Comprehensive Reporting** - Beautiful HTML reports with detailed metrics and logs
- **Configuration-Driven** - YAML/JSON configuration files for repeatable tests
- **Production Ready** - Robust error handling, logging, and monitoring

### Validation Types
1. **Message Delivery** - Ensure all produced messages are consumed
2. **Message Ordering** - Validate message sequence preservation
3. **Latency Measurement** - Track end-to-end message latency with percentiles
4. **Schema Validation** - Validate JSON messages against schemas
5. **Duplicate Detection** - Identify and report duplicate messages
6. **Retry Behavior** - Test retry mechanisms and failure handling

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/kafka-e2e-test-tool.git
cd kafka-e2e-test-tool

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Basic Usage

```bash
# Run a simple test with mock Kafka
python main.py run-test \
  --producer-topic test-producer \
  --consumer-topic test-consumer \
  --use-mock \
  --messages "Hello Kafka!" "Test Message 2" \
  --verbose

# Generate a sample configuration
python main.py generate-config --output my-kafka-tests.yaml

# Run tests with configuration file
python main.py run-test \
  --producer-topic my-producer \
  --consumer-topic my-consumer \
  --config my-kafka-tests.yaml \
  --bootstrap-servers localhost:9092

# View latest test report
python main.py report --format summary
```

## 📋 Configuration

### Sample YAML Configuration

```yaml
kafka:
  bootstrap_servers: "localhost:9092"
  producer:
    topic: "test-producer-topic"
    config:
      acks: "all"
      retries: 3
      compression_type: "snappy"
  consumer:
    topic: "test-consumer-topic"
    config:
      group_id: "kafka-e2e-test-group"
      auto_offset_reset: "earliest"

test_cases:
  - name: "basic_message_flow"
    description: "Test basic producer-consumer message flow"
    enabled: true
    messages:
      - "Hello Kafka!"
      - "Message 2"
      - "Final message"
    validations: ["delivery", "order", "latency"]

  - name: "json_schema_validation"
    description: "Validate JSON message schema"
    enabled: true
    messages:
      - '{"user_id": 123, "action": "login"}'
      - '{"user_id": 456, "action": "logout"}'
    validations: ["delivery", "schema"]
    schema_file: "schemas/user_action.json"

validation_config:
  timeout: 30
  max_latency_ms: 5000
  expected_order: true
  allow_duplicates: false
  retry_attempts: 3
```

### Sample JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["user_id", "action"],
  "properties": {
    "user_id": {
      "type": "integer",
      "minimum": 1
    },
    "action": {
      "type": "string",
      "enum": ["login", "logout", "view", "purchase"]
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

## 🔧 CLI Commands

### `run-test`
Execute end-to-end tests for Kafka message flows.

```bash
python main.py run-test [OPTIONS]
```

**Options:**
- `-p, --producer-topic TEXT` - Producer topic name [required]
- `-c, --consumer-topic TEXT` - Consumer topic name [required]
- `-f, --config PATH` - Test configuration file (YAML/JSON)
- `-b, --bootstrap-servers TEXT` - Kafka bootstrap servers [default: localhost:9092]
- `-m, --messages TEXT` - Test messages (can be specified multiple times)
- `-o, --output-dir TEXT` - Output directory for reports [default: ./test-results]
- `-t, --timeout INTEGER` - Test timeout in seconds [default: 30]
- `--use-mock` - Use mock Kafka for testing
- `-v, --verbose` - Verbose logging

### `generate-config`
Generate a sample configuration file.

```bash
python main.py generate-config [OPTIONS]
```

**Options:**
- `-o, --output TEXT` - Output config file path [default: kafka-test-config.yaml]
- `-f, --format [yaml|json]` - Config file format [default: yaml]
- `-p, --producer-topic TEXT` - Default producer topic [default: test-producer-topic]
- `-c, --consumer-topic TEXT` - Default consumer topic [default: test-consumer-topic]

### `report`
Display test report summary.

```bash
python main.py report [OPTIONS]
```

**Options:**
- `-d, --report-dir TEXT` - Directory containing test reports [default: ./test-results]
- `-f, --format [summary|detailed]` - Report format [default: summary]

## 📊 Test Reports

The tool generates comprehensive HTML reports with:

### Dashboard Overview
- Total tests executed
- Pass/fail statistics
- Overall pass rate
- Total execution time

### Detailed Test Results
- Individual test case status
- Execution timing
- Validation results
- Error details and logs

### Metrics and Analytics
- **Latency Analysis** - Min, max, average, and percentile latencies
- **Throughput Metrics** - Messages per second
- **Delivery Statistics** - Success/failure rates
- **Order Analysis** - Out-of-order message detection
- **Schema Compliance** - Validation error details

## 🏗️ Architecture

### Modular Design
```
kafka-e2e-test-tool/
├── main.py                     # CLI entry point
├── src/
│   ├── config/
│   │   └── config_parser.py    # Configuration handling
│   ├── kafka/
│   │   └── kafka_manager.py    # Kafka operations
│   ├── validators/
│   │   └── test_validator.py   # Test validation logic
│   ├── reports/
│   │   └── html_reporter.py    # Report generation
│   └── utils/
│       └── logger.py           # Logging utilities
├── schemas/                    # JSON schema files
├── examples/                   # Example configurations
└── tests/                      # Unit tests
```

### Key Components

#### KafkaManager
- Handles producer/consumer operations
- Supports both real and mock Kafka
- Thread-safe message handling
- Connection management

#### TestValidator
- Orchestrates test execution
- Pluggable validation strategies
- Error handling and recovery
- Metrics collection

#### HTMLReporter
- Generates interactive reports
- Responsive design
- Detailed metrics visualization
- Export capabilities

## 🐳 Docker Support

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .
RUN pip install -e .

# Create output directory
RUN mkdir -p /app/test-results

ENTRYPOINT ["python", "main.py"]
```

### Build and Run

```bash
# Build image
docker build -t kafka-e2e-test-tool .

# Run with mock Kafka
docker run --rm -v $(pwd)/test-results:/app/test-results \
  kafka-e2e-test-tool run-test \
  --producer-topic test-topic \
  --consumer-topic test-topic \
  --use-mock

# Run with external Kafka
docker run --rm --network host \
  -v $(pwd)/test-results:/app/test-results \
  -v $(pwd)/config.yaml:/app/config.yaml \
  kafka-e2e-test-tool run-test \
  --config /app/config.yaml \
  --bootstrap-servers localhost:9092
```

## 🧪 Testing Modes

### Mock Mode
Perfect for development and CI/CD pipelines:
- No external Kafka required
- Fast execution
- Predictable behavior
- Isolated testing

### Testcontainers Mode
Isolated testing with real Kafka:
- Uses Docker containers
- Clean environment per test
- Real Kafka behavior
- Automatic cleanup

### Production Mode
Testing against real Kafka clusters:
- Full integration testing
- Performance validation
- Real-world scenarios
- Production readiness verification

## 📈 Performance Considerations

### Scalability
- Supports high-volume message testing
- Configurable batch sizes
- Parallel processing where appropriate
- Memory-efficient message handling

### Monitoring
- Built-in metrics collection
- Performance tracking
- Resource usage monitoring
- Alerting capabilities

## 🔒 Security

### Authentication
- SASL/SSL support (when using real Kafka)
- Configurable security protocols
- Credential management
- Environment variable support

### Data Privacy
- No sensitive data logging
- Configurable log levels
- Secure credential handling
- Test data isolation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -am 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/nsharmapunjab/frameworks_and_tools.git
cd kafka-e2e-test-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Run tests
pytest tests/

# Run linting
flake8 src/
black src/
mypy src/
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

### Upcoming Features
- [ ] Avro schema support
- [ ] Kafka Streams testing
- [ ] Performance benchmarking
- [ ] Custom validation plugins
- [ ] Grafana dashboard integration
- [ ] CI/CD pipeline templates
- [ ] Advanced retry strategies
- [ ] Message encryption testing

### Version History

#### v1.0.0 (Current)
- Initial release
- Core validation features
- HTML reporting
- Mock Kafka support
- Configuration-driven testing

---

**Built with ❤️  by Nitin Sharma**
