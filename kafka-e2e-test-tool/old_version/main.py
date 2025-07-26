#!/usr/bin/env python3
"""
Kafka E2E Test Tool - Main CLI Module
A production-ready CLI tool for end-to-end Kafka testing
"""

import click
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
import json
from datetime import datetime

# Local imports
from src.config.config_parser import ConfigParser
from src.kafka.kafka_manager import KafkaManager
from src.validators.test_validator import TestValidator
from src.reports.html_reporter import HTMLReporter
from src.utils.logger import setup_logger


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Kafka E2E Test Tool - Validate your Kafka message flows"""
    pass


@cli.command()
@click.option('--producer-topic', '-p', required=True, help='Producer topic name')
@click.option('--consumer-topic', '-c', required=True, help='Consumer topic name')
@click.option('--config', '-f', type=click.Path(exists=True), help='Test configuration file (YAML/JSON)')
@click.option('--bootstrap-servers', '-b', default='localhost:9092', help='Kafka bootstrap servers')
@click.option('--messages', '-m', multiple=True, help='Test messages (can be specified multiple times)')
@click.option('--output-dir', '-o', default='./test-results', help='Output directory for reports')
@click.option('--timeout', '-t', default=30, type=int, help='Test timeout in seconds')
@click.option('--use-mock', is_flag=True, help='Use mock Kafka for testing')
@click.option('--verbose', '-v', is_flag=True, help='Verbose logging')
def run_test(producer_topic: str, consumer_topic: str, config: Optional[str], 
             bootstrap_servers: str, messages: tuple, output_dir: str, 
             timeout: int, use_mock: bool, verbose: bool):
    """Run end-to-end tests for Kafka message flows"""
    
    # Setup logging
    logger = setup_logger('kafka_e2e', verbose=verbose)
    logger.info("Starting Kafka E2E Test Tool")
    
    try:
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Parse configuration
        config_parser = ConfigParser()
        if config:
            test_config = config_parser.load_config(config)
        else:
            # Create default config from CLI arguments
            test_config = config_parser.create_default_config(
                producer_topic=producer_topic,
                consumer_topic=consumer_topic,
                bootstrap_servers=bootstrap_servers,
                messages=list(messages) if messages else ["Hello Kafka!", "Test Message 2"],
                timeout=timeout
            )
        
        logger.info(f"Test configuration loaded: {len(test_config.get('test_cases', []))} test cases")
        
        # Initialize Kafka manager
        kafka_manager = KafkaManager(
            bootstrap_servers=test_config['kafka']['bootstrap_servers'],
            use_mock=use_mock
        )
        
        # Initialize test validator
        validator = TestValidator(kafka_manager)
        
        # Run tests
        test_results = validator.run_all_tests(test_config)
        
        # Generate HTML report
        reporter = HTMLReporter(output_dir)
        report_path = reporter.generate_report(test_results, test_config)
        
        # Print summary
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result['status'] == 'PASSED')
        failed_tests = total_tests - passed_tests
        
        click.echo(f"\n{'='*50}")
        click.echo(f"TEST SUMMARY")
        click.echo(f"{'='*50}")
        click.echo(f"Total Tests: {total_tests}")
        click.echo(f"Passed: {click.style(str(passed_tests), fg='green')}")
        click.echo(f"Failed: {click.style(str(failed_tests), fg='red')}")
        click.echo(f"Report generated: {report_path}")
        click.echo(f"{'='*50}")
        
        # Exit with appropriate code
        sys.exit(0 if failed_tests == 0 else 1)
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
    finally:
        if 'kafka_manager' in locals():
            kafka_manager.cleanup()


@cli.command()
@click.option('--output', '-o', default='kafka-test-config.yaml', help='Output config file path')
@click.option('--format', '-f', type=click.Choice(['yaml', 'json']), default='yaml', help='Config file format')
@click.option('--producer-topic', '-p', default='test-producer-topic', help='Default producer topic')
@click.option('--consumer-topic', '-c', default='test-consumer-topic', help='Default consumer topic')
def generate_config(output: str, format: str, producer_topic: str, consumer_topic: str):
    """Generate a sample configuration file"""
    
    config_parser = ConfigParser()
    sample_config = config_parser.generate_sample_config(
        producer_topic=producer_topic,
        consumer_topic=consumer_topic,
        format=format
    )
    
    # Write to file
    with open(output, 'w') as f:
        if format == 'yaml':
            yaml.dump(sample_config, f, default_flow_style=False, indent=2)
        else:
            json.dump(sample_config, f, indent=2)
    
    click.echo(f"Sample configuration generated: {output}")


@cli.command()
@click.option('--report-dir', '-d', default='./test-results', help='Directory containing test reports')
@click.option('--format', '-f', type=click.Choice(['summary', 'detailed']), default='summary', help='Report format')
def report(report_dir: str, format: str):
    """Display test report summary"""
    
    report_dir_path = Path(report_dir)
    if not report_dir_path.exists():
        click.echo(f"Report directory not found: {report_dir}", err=True)
        sys.exit(1)
    
    # Find latest HTML report
    html_files = list(report_dir_path.glob("kafka-e2e-report-*.html"))
    if not html_files:
        click.echo("No test reports found", err=True)
        sys.exit(1)
    
    latest_report = max(html_files, key=lambda x: x.stat().st_mtime)
    
    if format == 'summary':
        click.echo(f"Latest report: {latest_report}")
        click.echo(f"Generated: {datetime.fromtimestamp(latest_report.stat().st_mtime)}")
    else:
        # For detailed format, we would parse the HTML or have a JSON summary
        click.echo(f"Detailed report available at: {latest_report}")
        click.echo("Open in browser to view detailed results")


if __name__ == '__main__':
    cli()
