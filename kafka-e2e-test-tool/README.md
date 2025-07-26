# Kafka E2E Test Tool - Quick Start

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
