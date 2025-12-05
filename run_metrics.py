#!/usr/bin/env python3
"""
Metrics Evaluation Runner for From-Words-to-Shields Pipeline

This script runs test prompts against the pipeline and evaluates various metrics:
- Robustness: Pipeline success rate, tool-generation success %, recovery success
- Adaptability: Time to generate new pipeline, # of LLM steps, success rate on novel requirements
- Performance: End-to-end latency, resource usage, throughput
- Security: Sandbox compliance, manifest verification, generated code safety
- Auditability: Log completeness, manifest accuracy, decision traceability
- Baseline Comparison: LLM planning overhead %

Usage:
    python run_metrics.py                    # Run all test suites
    python run_metrics.py --suite robustness # Run specific suite
    python run_metrics.py --quick            # Run quick tests only
    python run_metrics.py --evaluate-only    # Only evaluate existing logs
    python run_metrics.py --list-suites      # List available test suites
"""

import os
import sys
import argparse

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars are already set


def main():
    parser = argparse.ArgumentParser(
        description="Run metrics evaluation for the pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_metrics.py                     # Run all test suites
  python run_metrics.py --suite robustness  # Run robustness tests
  python run_metrics.py --quick             # Run quick smoke tests
  python run_metrics.py --evaluate-only     # Evaluate existing logs only
  python run_metrics.py --list-suites       # Show available test suites
        """
    )
    
    parser.add_argument(
        "--suite", "-s",
        type=str,
        help="Specific test suite to run (robustness, adaptability, performance, security, edge_cases, baseline_comparison)"
    )
    
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Run quick smoke tests only"
    )
    
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Don't clear existing logs before running tests"
    )
    
    parser.add_argument(
        "--evaluate-only", "-e",
        action="store_true",
        help="Only evaluate existing logs, don't run new tests"
    )
    
    parser.add_argument(
        "--list-suites", "-l",
        action="store_true",
        help="List available test suites and exit"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="metrics/report.json",
        help="Output path for metrics report (default: metrics/report.json)"
    )
    
    parser.add_argument(
        "--test-file", "-f",
        type=str,
        help="Path to test video file"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Import metrics modules
    from metrics.runner import MetricsRunner
    from metrics.evaluator import MetricsEvaluator
    
    # List suites and exit
    if args.list_suites:
        print("\nAvailable Test Suites:")
        print("=" * 50)
        for suite_name, tests in MetricsRunner.TEST_SUITES.items():
            print(f"\n{suite_name}:")
            for test in tests:
                print(f"  {test.name}: {test.description or test.prompt[:40]}")

        return 0
    
    # Check for API key
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key and not args.evaluate_only:
        print("ERROR: GROQ_API_KEY not found in environment variables")
        print("Set it in your .env file or export it:")
        print("  export GROQ_API_KEY=your_key_here")
        return 1
    
    # Evaluate only mode
    if args.evaluate_only:
        print("\n" + "=" * 70)
        print("METRICS EVALUATION (from existing logs)")
        print("=" * 70)
        
        evaluator = MetricsEvaluator()
        metrics = evaluator.evaluate()
        
        if metrics.workflows_analyzed == 0:
            print("\nNo workflows found in audit log.")
            print("Run tests first with: python run_metrics.py --quick")
            return 1
        
        evaluator.print_report(metrics)
        report_path = evaluator.save_report(metrics, args.output)
        print(f"\nReport saved to: {report_path}")
        return 0
    
    # Initialize runner
    runner = MetricsRunner(
        test_file=args.test_file,
        backup_logs=True
    )
    
    if not runner.test_file:
        print("ERROR: No test video file found")
        print("Either place a .mp4 file in data/samples/ or use --test-file")
        return 1
    
    print(f"\nUsing test file: {runner.test_file}")
    
    # Run tests
    print("\n" + "=" * 70)
    print("RUNNING PIPELINE TESTS")
    print("=" * 70)
    
    try:
        if args.quick:
            print("\nRunning quick smoke tests...")
            runner.run_quick_test()
        elif args.suite:
            print(f"\nRunning {args.suite} test suite...")
            runner.run_suite(args.suite, clear_logs=not args.no_clear)
        else:
            print("\nRunning all test suites...")
            runner.run_all_suites(clear_logs=not args.no_clear)
        
        # Print test summary
        runner.print_summary()
        runner.save_results()
        
    except KeyboardInterrupt:
        print("\n\nTest run interrupted by user")
        runner.print_summary()
        runner.save_results()
    
    # Evaluate metrics
    print("\n" + "=" * 70)
    print("EVALUATING METRICS")
    print("=" * 70)
    
    evaluator = MetricsEvaluator()
    metrics = evaluator.evaluate()
    evaluator.print_report(metrics)
    report_path = evaluator.save_report(metrics, args.output)
    
    print(f"\n{'='*70}")
    print("EVALUATION COMPLETE")
    print(f"{'='*70}")
    print(f"Test results: metrics/test_results.json")
    print(f"Metrics report: {report_path}")
    
    # Return exit code based on test pass rate
    summary = runner.get_summary()
    if summary.get("pass_rate", 0) < 0.5:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

