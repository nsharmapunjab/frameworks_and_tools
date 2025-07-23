import json
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
