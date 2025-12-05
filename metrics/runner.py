#!/usr/bin/env python3
"""Test runner for metrics evaluation."""

import os
import sys
import time
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _load_env():
    """Load environment variables."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv not required if env vars are already set


@dataclass
class TestCase:
    """A single test case for metrics evaluation."""
    name: str
    prompt: str
    category: str
    expected_tools: List[str] = field(default_factory=list)
    expected_success: bool = True
    requires_tool_generation: bool = False
    is_edge_case: bool = False
    description: str = ""


@dataclass 
class TestResult:
    """Result of a single test execution."""
    test_case: TestCase
    success: bool
    execution_time: float
    error: Optional[str] = None
    manifest: Optional[Dict] = None
    planning_time: float = 0.0
    execution_phases: int = 0
    tools_generated: int = 0
    tools_executed: int = 0
    retries: int = 0


class MetricsRunner:
    """Runs test prompts and collects metrics."""
    
    # Predefined test suites
    # Test suites designed for privacy policy compliance scenarios
    # Simulating real GDPR and privacy regulation use cases
    TEST_SUITES = {
        # Core privacy operations - fundamental GDPR compliance
        "robustness": [
            TestCase(
                name="anonymize_faces",
                prompt="Anonymize all faces in the video to comply with GDPR",
                category="robustness",
                expected_tools=["blur_faces"],
                description="Basic face anonymization for privacy"
            ),
            TestCase(
                name="redact_pii_audio",
                prompt="Mute any mentions of names, addresses, or phone numbers",
                category="robustness",
                expected_tools=["mute_keywords"],
                description="Audio PII redaction"
            ),
            TestCase(
                name="strong_anonymization",
                prompt="Apply strong blur to faces - they must be completely unrecognizable",
                category="robustness",
                expected_tools=["blur_faces"],
                description="High-strength anonymization"
            ),
            TestCase(
                name="multi_pii_categories",
                prompt="Mute mentions of email addresses, social security numbers, and credit card numbers",
                category="robustness",
                expected_tools=["mute_keywords"],
                description="Multiple PII category redaction"
            ),
        ],
        
        # Adaptability - handling evolving privacy requirements
        "adaptability": [
            TestCase(
                name="license_plate_privacy",
                prompt="Blur all license plates",
                category="adaptability",
                requires_tool_generation=True,
                description="Vehicle identification anonymization"
            ),
            TestCase(
                name="text_redaction",
                prompt="Detect and blur any visible text containing personal information",
                category="adaptability",
                requires_tool_generation=True,
                description="On-screen text PII redaction"
            ),
            TestCase(
                name="background_anonymization",
                prompt="Blur the background to hide location and environment details",
                category="adaptability",
                requires_tool_generation=True,
                description="Location privacy protection"
            ),
            TestCase(
                name="body_anonymization",
                prompt="Anonymize people's bodies, not just faces, for full privacy",
                category="adaptability",
                requires_tool_generation=True,
                description="Full person anonymization"
            ),
        ],
        
        # Performance benchmarks for privacy operations
        "performance": [
            TestCase(
                name="face_detection_speed",
                prompt="Detect all faces in the video",
                category="performance",
                expected_tools=["detect_faces"],
                description="Face detection performance"
            ),
            TestCase(
                name="face_blur_speed",
                prompt="Blur faces in video",
                category="performance",
                expected_tools=["blur_faces"],
                description="Face blur performance"
            ),
            TestCase(
                name="audio_scan_speed",
                prompt="Scan audio for sensitive keywords",
                category="performance",
                expected_tools=["detect_keywords"],
                description="Audio PII scanning performance"
            ),
        ],
        
        # Security of generated privacy tools
        "security": [
            TestCase(
                name="safe_anonymizer",
                prompt="Create a tool to pixelate regions of interest for privacy",
                category="security",
                requires_tool_generation=True,
                description="Safe pixelation tool generation"
            ),
            TestCase(
                name="safe_audio_filter",
                prompt="Apply audio filtering to mask voice identity",
                category="security",
                requires_tool_generation=True,
                description="Voice anonymization tool"
            ),
        ],
        
        # Real-world GDPR compliance scenarios
        "gdpr_compliance": [
            TestCase(
                name="right_to_be_forgotten",
                prompt="Remove all identifiable information about a specific person from the video",
                category="gdpr",
                expected_tools=["blur_faces"],
                requires_tool_generation=True,
                description="GDPR Article 17 - Right to erasure"
            ),
            TestCase(
                name="consent_withdrawal",
                prompt="Anonymize faces and mute names since consent was withdrawn",
                category="gdpr",
                expected_tools=["blur_faces", "mute_keywords"],
                description="Handle consent withdrawal"
            ),
            TestCase(
                name="data_minimization",
                prompt="Remove all unnecessary personal data - keep only essential content",
                category="gdpr",
                requires_tool_generation=True,
                description="GDPR data minimization principle"
            ),
            TestCase(
                name="childrens_privacy",
                prompt="Detect and blur all children's faces with extra care",
                category="gdpr",
                expected_tools=["blur_faces"],
                description="Enhanced protection for minors"
            ),
        ],
        
        # Multi-modal privacy - combined video and audio
        "multimodal_privacy": [
            TestCase(
                name="full_anonymization",
                prompt="Blur all faces and mute all personal names mentioned",
                category="multimodal",
                expected_tools=["blur_faces", "mute_keywords"],
                description="Complete AV anonymization"
            ),
            TestCase(
                name="witness_protection",
                prompt="Anonymize the speaker's face and distort their voice",
                category="multimodal",
                expected_tools=["blur_faces"],
                requires_tool_generation=True,
                description="Witness/source protection"
            ),
            TestCase(
                name="medical_privacy",
                prompt="Blur patient faces and mute any medical record numbers or diagnosis mentions",
                category="multimodal",
                expected_tools=["blur_faces", "mute_keywords"],
                description="HIPAA-style medical privacy"
            ),
        ],
        
        # Edge cases in privacy compliance
        "edge_cases": [
            TestCase(
                name="no_faces_present",
                prompt="Anonymize faces in the video",
                category="edge_cases",
                expected_tools=["blur_faces"],
                is_edge_case=True,
                description="Handle video with no faces"
            ),
            TestCase(
                name="crowded_scene",
                prompt="Blur all faces in a crowded public event video",
                category="edge_cases",
                expected_tools=["blur_faces"],
                description="High face count scenario"
            ),
            TestCase(
                name="partial_visibility",
                prompt="Anonymize partially visible faces and people seen from behind",
                category="edge_cases",
                expected_tools=["blur_faces"],
                requires_tool_generation=True,
                description="Partial face detection"
            ),
        ],
    }
    
    def __init__(self, test_file: str = None, 
                 log_file: str = "audit/execution.log",
                 backup_logs: bool = True):
        """Initialize the metrics runner.
        
        Args:
            test_file: Optional path to test video file
            log_file: Path to audit log file
            backup_logs: Whether to backup existing logs before running
        """
        self.test_file = test_file or self._find_test_file()
        self.log_file = log_file
        self.backup_logs = backup_logs
        self.results: List[TestResult] = []
        
    def _find_test_file(self) -> Optional[str]:
        """Find a test video file."""
        samples_dir = os.path.join(PROJECT_ROOT, "data", "samples")
        if os.path.exists(samples_dir):
            for f in os.listdir(samples_dir):
                if f.endswith('.mp4'):
                    return os.path.join(samples_dir, f)
        return None
    
    def _backup_logs(self):
        """Backup existing audit logs."""
        if os.path.exists(self.log_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.log_file}.{timestamp}.bak"
            shutil.copy(self.log_file, backup_path)
            return backup_path
        return None
    
    def _clear_logs(self):
        """Clear existing audit logs for fresh test run."""
        if os.path.exists(self.log_file):
            # Truncate the file instead of deleting
            with open(self.log_file, 'w') as f:
                f.write("")
    
    def run_test(self, test_case: TestCase, planner=None) -> TestResult:
        """Run a single test case."""
        _load_env()
        from planner.executor import executor
        from planner.write_manifest import PipelinePlanner
        
        if planner is None:
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                return TestResult(
                    test_case=test_case,
                    success=False,
                    execution_time=0,
                    error="GROQ_API_KEY not found"
                )
            planner = PipelinePlanner(api_key=api_key)
        
        print(f"\n{'='*60}")
        print(f"TEST: {test_case.name}")
        print(f"Prompt: {test_case.prompt}")
        print(f"Category: {test_case.category}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Execute the workflow
            success = executor(test_case.prompt, self.test_file, planner)
            execution_time = time.time() - start_time
            
            return TestResult(
                test_case=test_case,
                success=bool(success),
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_case=test_case,
                success=False,
                execution_time=execution_time,
                error=str(e)
            )
    
    def run_suite(self, suite_name: str, clear_logs: bool = False) -> List[TestResult]:
        """Run a specific test suite."""
        if suite_name not in self.TEST_SUITES:
            print(f"Unknown test suite: {suite_name}")
            print(f"Available suites: {list(self.TEST_SUITES.keys())}")
            return []
        
        if self.backup_logs:
            backup_path = self._backup_logs()
            if backup_path:
                print(f"Backed up logs to: {backup_path}")
        
        if clear_logs:
            self._clear_logs()
        
        test_cases = self.TEST_SUITES[suite_name]
        results = []
        
        # Setup planner once
        _load_env()
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("ERROR: GROQ_API_KEY not found")
            return []
        
        from planner.write_manifest import PipelinePlanner
        planner = PipelinePlanner(api_key=api_key)
        
        print(f"\nRunning {suite_name} test suite ({len(test_cases)} tests)")
        print("=" * 70)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] Running: {test_case.name}")
            
            result = self.run_test(test_case, planner)
            results.append(result)
            
            status = "✓ PASS" if result.success else "✗ FAIL"
            print(f"{status} - {result.execution_time:.2f}s")
            if result.error:
                print(f"  Error: {result.error}")
        
        self.results.extend(results)
        return results
    
    def run_all_suites(self, clear_logs: bool = True) -> Dict[str, List[TestResult]]:
        """Run all test suites."""
        if self.backup_logs:
            backup_path = self._backup_logs()
            if backup_path:
                print(f"Backed up logs to: {backup_path}")
        
        if clear_logs:
            self._clear_logs()
        
        all_results = {}
        
        for suite_name in self.TEST_SUITES:
            print(f"\n{'#'*70}")
            print(f"# SUITE: {suite_name.upper()}")
            print(f"{'#'*70}")
            
            results = self.run_suite(suite_name, clear_logs=False)
            all_results[suite_name] = results
        
        return all_results
    
    def run_quick_test(self) -> List[TestResult]:
        """Run a quick subset of tests for rapid iteration."""
        quick_tests = [
            TestCase(
                name="quick_face_anonymization",
                prompt="Anonymize faces for GDPR compliance",
                category="quick",
                expected_tools=["blur_faces"],
                description="Quick face privacy test"
            ),
            TestCase(
                name="quick_pii_redaction",
                prompt="Mute personal information like names and addresses",
                category="quick",
                expected_tools=["mute_keywords"],
                description="Quick audio PII test"
            ),
        ]
        
        if self.backup_logs:
            self._backup_logs()
        
        results = []
        
        _load_env()
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("ERROR: GROQ_API_KEY not found")
            return []
        
        from planner.write_manifest import PipelinePlanner
        planner = PipelinePlanner(api_key=api_key)
        
        for test_case in quick_tests:
            result = self.run_test(test_case, planner)
            results.append(result)
        
        self.results.extend(results)
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of test results."""
        if not self.results:
            return {"error": "No results to summarize"}
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed
        
        by_category = {}
        for r in self.results:
            cat = r.test_case.category
            if cat not in by_category:
                by_category[cat] = {"total": 0, "passed": 0, "failed": 0}
            by_category[cat]["total"] += 1
            if r.success:
                by_category[cat]["passed"] += 1
            else:
                by_category[cat]["failed"] += 1
        
        total_time = sum(r.execution_time for r in self.results)
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0,
            "total_time": total_time,
            "avg_time_per_test": total_time / total if total > 0 else 0,
            "by_category": by_category,
            "failed_tests": [
                {"name": r.test_case.name, "error": r.error}
                for r in self.results if not r.success
            ]
        }
    
    def print_summary(self):
        """Print test results summary."""
        summary = self.get_summary()
        
        if "error" in summary:
            print(summary["error"])
            return
        
        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"Total Tests:  {summary['total_tests']}")
        print(f"Passed:       {summary['passed']} ({summary['pass_rate']:.1%})")
        print(f"Failed:       {summary['failed']}")
        print(f"Total Time:   {summary['total_time']:.2f}s")
        print(f"Avg Per Test: {summary['avg_time_per_test']:.2f}s")
        
        print("\nBy Category:")
        for cat, stats in summary["by_category"].items():
            rate = stats["passed"] / stats["total"] if stats["total"] > 0 else 0
            print(f"  {cat}: {stats['passed']}/{stats['total']} ({rate:.1%})")
        
        if summary["failed_tests"]:
            print("\nFailed Tests:")
            for ft in summary["failed_tests"]:
                print(f"  - {ft['name']}: {ft['error']}")
        
        print("=" * 70)
    
    def save_results(self, output_path: str = "metrics/test_results.json"):
        """Save test results to JSON file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "results": [
                {
                    "test_name": r.test_case.name,
                    "prompt": r.test_case.prompt,
                    "category": r.test_case.category,
                    "success": r.success,
                    "execution_time": r.execution_time,
                    "error": r.error
                }
                for r in self.results
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\nResults saved to: {output_path}")
        return output_path


def run_metrics_evaluation(suite: str = None, 
                          quick: bool = False,
                          clear_logs: bool = True) -> Dict[str, Any]:
    """Run a complete metrics evaluation.
    
    Args:
        suite: Specific suite to run (or None for all)
        quick: Run quick test only
        clear_logs: Clear existing logs before running
        
    Returns:
        Dictionary with metrics evaluation results
    """
    from .evaluator import MetricsEvaluator
    
    # Initialize runner
    runner = MetricsRunner()
    
    if not runner.test_file:
        print("ERROR: No test video file found in data/samples/")
        return {"error": "No test file"}
    
    print(f"Using test file: {runner.test_file}")
    
    # Run tests
    if quick:
        runner.run_quick_test()
    elif suite:
        runner.run_suite(suite, clear_logs=clear_logs)
    else:
        runner.run_all_suites(clear_logs=clear_logs)
    
    # Print test summary
    runner.print_summary()
    runner.save_results()
    
    # Now evaluate metrics from the logs
    print("\n" + "#" * 70)
    print("# EVALUATING METRICS FROM LOGS")
    print("#" * 70)
    
    evaluator = MetricsEvaluator()
    metrics = evaluator.evaluate()
    evaluator.print_report(metrics)
    report_path = evaluator.save_report(metrics)
    
    return {
        "test_summary": runner.get_summary(),
        "metrics": evaluator.to_dict(metrics),
        "report_path": report_path
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run metrics evaluation")
    parser.add_argument("--suite", type=str, help="Specific suite to run")
    parser.add_argument("--quick", action="store_true", help="Run quick test only")
    parser.add_argument("--no-clear", action="store_true", help="Don't clear logs")
    parser.add_argument("--evaluate-only", action="store_true", 
                       help="Only evaluate existing logs, don't run tests")
    
    args = parser.parse_args()
    
    if args.evaluate_only:
        from .evaluator import MetricsEvaluator
        evaluator = MetricsEvaluator()
        metrics = evaluator.evaluate()
        evaluator.print_report(metrics)
        evaluator.save_report(metrics)
    else:
        results = run_metrics_evaluation(
            suite=args.suite,
            quick=args.quick,
            clear_logs=not args.no_clear
        )

