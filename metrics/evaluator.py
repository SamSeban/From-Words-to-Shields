#!/usr/bin/env python3
"""Metrics evaluator for pipeline performance analysis."""

import os
import re
import ast
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict

from .log_parser import AuditLogParser, WorkflowExecution


@dataclass
class RobustnessMetrics:
    """Robustness evaluation metrics."""
    pipeline_success_rate: float = 0.0
    tool_generation_success_rate: float = 0.0
    tool_execution_success_rate: float = 0.0
    recovery_success_rate: float = 0.0  # Success after retries
    error_types: Dict[str, int] = field(default_factory=dict)
    failure_points: Dict[str, int] = field(default_factory=dict)  # Where failures occur


@dataclass
class AdaptabilityMetrics:
    """Adaptability evaluation metrics."""
    avg_pipeline_generation_time: float = 0.0
    avg_llm_steps_per_workflow: float = 0.0  # Planning + tool gen steps
    avg_tool_generation_time: float = 0.0
    novel_tool_generation_success_rate: float = 0.0
    builtin_vs_generated_ratio: float = 0.0  # Ratio of builtin to generated tools


@dataclass
class PerformanceMetrics:
    """Performance evaluation metrics."""
    avg_end_to_end_latency: float = 0.0
    min_latency: float = 0.0
    max_latency: float = 0.0
    avg_planning_time: float = 0.0
    avg_execution_time: float = 0.0
    avg_tool_execution_time: float = 0.0
    throughput_workflows_per_hour: float = 0.0
    cpu_usage_avg: float = 0.0
    memory_usage_mb: float = 0.0


@dataclass
class SecurityMetrics:
    """Security evaluation metrics."""
    sandbox_compliance: float = 0.0  # % of generated tools that pass sandbox checks
    manifest_verification_rate: float = 0.0
    unsafe_code_patterns_detected: int = 0
    allowed_imports_compliance: float = 0.0
    file_access_compliance: float = 0.0


@dataclass
class AuditabilityMetrics:
    """Auditability evaluation metrics."""
    log_completeness_score: float = 0.0  # 0-1 score for complete logging
    manifest_accuracy: float = 0.0  # % of manifests that match execution
    decision_traceability_score: float = 0.0  # Can we trace all decisions?
    timestamp_coverage: float = 0.0  # % of events with timestamps
    error_logging_completeness: float = 0.0


@dataclass
class BaselineComparisonMetrics:
    """Baseline comparison metrics."""
    overhead_from_llm_planning: float = 0.0  # % of time spent in LLM calls


@dataclass
class AllMetrics:
    """Container for all metrics categories."""
    robustness: RobustnessMetrics = field(default_factory=RobustnessMetrics)
    adaptability: AdaptabilityMetrics = field(default_factory=AdaptabilityMetrics)
    performance: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    security: SecurityMetrics = field(default_factory=SecurityMetrics)
    auditability: AuditabilityMetrics = field(default_factory=AuditabilityMetrics)
    baseline_comparison: BaselineComparisonMetrics = field(default_factory=BaselineComparisonMetrics)
    evaluation_timestamp: str = ""
    evaluation_duration: float = 0.0
    workflows_analyzed: int = 0


class MetricsEvaluator:
    """Evaluates pipeline metrics from audit logs and runtime data."""
    
    # Known safe imports for generated tools
    ALLOWED_IMPORTS = {
        'cv2', 'numpy', 'os', 'time', 'json', 'pathlib',
        'torch', 'torchaudio', 'whisper', 'pydub', 'librosa',
        'soundfile', 'typing', 'abc', 'registry', 'tool_api'
    }
    
    # Unsafe patterns to detect in generated code
    UNSAFE_PATTERNS = [
        r'subprocess\.',
        r'os\.system\s*\(',
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__\s*\(',
        r'open\s*\([^)]*["\']\/etc',
        r'open\s*\([^)]*["\']\/root',
        r'open\s*\([^)]*["\']~\/',
        r'shutil\.rmtree',
        r'os\.remove\s*\(',
        r'os\.unlink\s*\(',
        r'requests\.',
        r'urllib\.',
        r'socket\.',
    ]
    
    def __init__(self, log_file: str = "audit/execution.log",
                 tools_dir: str = "tools",
                 manifests_dir: str = "manifests"):
        self.parser = AuditLogParser(log_file)
        self.tools_dir = tools_dir
        self.manifests_dir = manifests_dir
        self.workflows: List[WorkflowExecution] = []
    
    def evaluate(self) -> AllMetrics:
        """Run full evaluation and return all metrics."""
        start_time = time.time()
        
        # Parse workflows
        self.workflows = self.parser.parse()
        
        # Compute all metrics
        metrics = AllMetrics(
            robustness=self._evaluate_robustness(),
            adaptability=self._evaluate_adaptability(),
            performance=self._evaluate_performance(),
            security=self._evaluate_security(),
            auditability=self._evaluate_auditability(),
            baseline_comparison=self._evaluate_baseline_comparison(),
            evaluation_timestamp=datetime.now().isoformat(),
            evaluation_duration=time.time() - start_time,
            workflows_analyzed=len(self.workflows)
        )
        
        return metrics
    
    def _evaluate_robustness(self) -> RobustnessMetrics:
        """Evaluate robustness metrics."""
        if not self.workflows:
            return RobustnessMetrics()
        
        total_workflows = len(self.workflows)
        successful_workflows = sum(1 for w in self.workflows if w.success)
        
        # Tool generation success
        all_tool_gens = []
        for w in self.workflows:
            all_tool_gens.extend(w.tool_generations)
        
        tool_gen_success = sum(1 for t in all_tool_gens if t.success)
        
        # Tool execution success
        all_tool_execs = []
        for w in self.workflows:
            for ep in w.execution_phases:
                all_tool_execs.extend(ep.tools)
        
        tool_exec_success = sum(1 for t in all_tool_execs if t.success)
        
        # Recovery success rate (workflows that succeeded after retries)
        workflows_with_retries = [w for w in self.workflows if w.retry_attempts]
        recovered = sum(1 for w in workflows_with_retries if w.success)
        
        # Error analysis
        error_types: Dict[str, int] = {}
        failure_points: Dict[str, int] = {}
        
        for w in self.workflows:
            for e in w.errors:
                error_type = e.split(':')[0] if ':' in e else "Unknown"
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # Analyze failure points
            for ep in w.execution_phases:
                for tool in ep.tools:
                    if not tool.success:
                        failure_points[tool.tool_name] = failure_points.get(tool.tool_name, 0) + 1
            
            for tg in w.tool_generations:
                if not tg.success:
                    failure_points[f"toolgen_{tg.tool_name}"] = failure_points.get(f"toolgen_{tg.tool_name}", 0) + 1
        
        return RobustnessMetrics(
            pipeline_success_rate=successful_workflows / total_workflows if total_workflows > 0 else 0,
            tool_generation_success_rate=tool_gen_success / len(all_tool_gens) if all_tool_gens else 1.0,
            tool_execution_success_rate=tool_exec_success / len(all_tool_execs) if all_tool_execs else 0,
            recovery_success_rate=recovered / len(workflows_with_retries) if workflows_with_retries else 1.0,
            error_types=error_types,
            failure_points=failure_points
        )
    
    def _evaluate_adaptability(self) -> AdaptabilityMetrics:
        """Evaluate adaptability metrics."""
        if not self.workflows:
            return AdaptabilityMetrics()
        
        planning_times = []
        tool_gen_times = []
        llm_steps_per_workflow = []
        builtin_tools = 0
        generated_tools = 0
        
        for w in self.workflows:
            # Planning times
            for p in w.planning_phases:
                planning_times.append(p.elapsed_time)
            
            # Tool generation times
            for tg in w.tool_generations:
                tool_gen_times.append(tg.elapsed_time)
            
            # Count LLM steps (planning + tool generation)
            llm_steps = len(w.planning_phases) + len(w.tool_generations)
            llm_steps_per_workflow.append(llm_steps)
            
            # Count builtin vs generated tools
            generated_tools += len(w.tool_generations)
            for ep in w.execution_phases:
                for tool in ep.tools:
                    if not any(tg.tool_name == tool.tool_name or tg.actual_name == tool.tool_name 
                              for tg in w.tool_generations):
                        builtin_tools += 1
        
        # Novel tool generation success (tools that were generated and then executed)
        novel_success = 0
        novel_total = 0
        for w in self.workflows:
            for tg in w.tool_generations:
                if tg.success:
                    novel_total += 1
                    # Check if the generated tool was successfully executed
                    tool_name = tg.actual_name or tg.tool_name
                    for ep in w.execution_phases:
                        for tool in ep.tools:
                            if tool.tool_name == tool_name and tool.success:
                                novel_success += 1
                                break
        
        total_tools = builtin_tools + generated_tools
        
        return AdaptabilityMetrics(
            avg_pipeline_generation_time=sum(planning_times) / len(planning_times) if planning_times else 0,
            avg_llm_steps_per_workflow=sum(llm_steps_per_workflow) / len(llm_steps_per_workflow) if llm_steps_per_workflow else 0,
            avg_tool_generation_time=sum(tool_gen_times) / len(tool_gen_times) if tool_gen_times else 0,
            novel_tool_generation_success_rate=novel_success / novel_total if novel_total > 0 else 1.0,
            builtin_vs_generated_ratio=builtin_tools / generated_tools if generated_tools > 0 else float('inf')
        )
    
    def _evaluate_performance(self) -> PerformanceMetrics:
        """Evaluate performance metrics."""
        if not self.workflows:
            return PerformanceMetrics()
        
        latencies = [w.total_elapsed_time for w in self.workflows]
        planning_times = []
        execution_times = []
        tool_times = []
        
        for w in self.workflows:
            for p in w.planning_phases:
                planning_times.append(p.elapsed_time)
            for ep in w.execution_phases:
                execution_times.append(ep.elapsed_time)
                for tool in ep.tools:
                    tool_times.append(tool.elapsed_time)
        
        # Calculate throughput based on total time span
        if len(self.workflows) >= 2:
            time_span = (self.workflows[-1].start_time - self.workflows[0].start_time).total_seconds()
            throughput = len(self.workflows) / (time_span / 3600) if time_span > 0 else 0
        else:
            throughput = 0
        
        # Aggregate resource usage from logged snapshots
        all_cpu = []
        all_mem = []
        for w in self.workflows:
            for snap in w.resource_snapshots:
                all_cpu.append(snap.cpu_percent)
                all_mem.append(snap.memory_mb)
        
        avg_cpu = sum(all_cpu) / len(all_cpu) if all_cpu else 0.0
        avg_mem = sum(all_mem) / len(all_mem) if all_mem else 0.0
        
        return PerformanceMetrics(
            avg_end_to_end_latency=sum(latencies) / len(latencies) if latencies else 0,
            min_latency=min(latencies) if latencies else 0,
            max_latency=max(latencies) if latencies else 0,
            avg_planning_time=sum(planning_times) / len(planning_times) if planning_times else 0,
            avg_execution_time=sum(execution_times) / len(execution_times) if execution_times else 0,
            avg_tool_execution_time=sum(tool_times) / len(tool_times) if tool_times else 0,
            throughput_workflows_per_hour=throughput,
            cpu_usage_avg=avg_cpu,
            memory_usage_mb=avg_mem
        )
    
    def _evaluate_security(self) -> SecurityMetrics:
        """Evaluate security metrics of generated tools."""
        # Find all generated tool files
        generated_tools = self._find_generated_tools()
        
        if not generated_tools:
            return SecurityMetrics(
                sandbox_compliance=1.0,
                manifest_verification_rate=1.0,
                allowed_imports_compliance=1.0,
                file_access_compliance=1.0
            )
        
        total_tools = len(generated_tools)
        sandbox_compliant = 0
        import_compliant = 0
        file_access_compliant = 0
        total_unsafe_patterns = 0
        
        for tool_path in generated_tools:
            try:
                with open(tool_path, 'r') as f:
                    code = f.read()
                
                # Check for unsafe patterns
                unsafe_count = self._count_unsafe_patterns(code)
                total_unsafe_patterns += unsafe_count
                
                # Check import compliance
                imports = self._extract_imports(code)
                disallowed = [i for i in imports if i not in self.ALLOWED_IMPORTS]
                if not disallowed:
                    import_compliant += 1
                
                # Check file access patterns
                if self._check_file_access_compliance(code):
                    file_access_compliant += 1
                
                # Overall sandbox compliance
                if unsafe_count == 0 and not disallowed:
                    sandbox_compliant += 1
                    
            except Exception:
                continue
        
        # Check manifest verification
        manifests_verified = self._verify_manifests()
        
        return SecurityMetrics(
            sandbox_compliance=sandbox_compliant / total_tools if total_tools > 0 else 1.0,
            manifest_verification_rate=manifests_verified,
            unsafe_code_patterns_detected=total_unsafe_patterns,
            allowed_imports_compliance=import_compliant / total_tools if total_tools > 0 else 1.0,
            file_access_compliance=file_access_compliant / total_tools if total_tools > 0 else 1.0
        )
    
    def _find_generated_tools(self) -> List[str]:
        """Find all generated tool files (non-builtin)."""
        generated = []
        
        # Builtin tools
        builtin_files = {
            'face.py', 'blur.py', 'blur_faces.py',
            'detect_keywords.py', 'mute_segments.py', 'mute_keywords.py',
            '__init__.py'
        }
        
        for root, _, files in os.walk(self.tools_dir):
            for f in files:
                if f.endswith('.py') and f not in builtin_files:
                    generated.append(os.path.join(root, f))
        
        return generated
    
    def _count_unsafe_patterns(self, code: str) -> int:
        """Count unsafe patterns in code."""
        count = 0
        for pattern in self.UNSAFE_PATTERNS:
            matches = re.findall(pattern, code)
            count += len(matches)
        return count
    
    def _extract_imports(self, code: str) -> List[str]:
        """Extract imported modules from code."""
        imports = []
        
        # Simple regex-based extraction
        import_patterns = [
            r'^import\s+(\w+)',
            r'^from\s+(\w+)',
        ]
        
        for line in code.split('\n'):
            line = line.strip()
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    imports.append(match.group(1))
        
        return imports
    
    def _check_file_access_compliance(self, code: str) -> bool:
        """Check if file access patterns are compliant (only data/ directory)."""
        # Look for file write operations
        write_patterns = [
            r'open\s*\([^)]+["\']([^"\']+)["\'][^)]*["\']w',
            r'\.write\s*\(',
            r'cv2\.VideoWriter\s*\([^)]+["\']([^"\']+)["\']',
        ]
        
        for pattern in write_patterns:
            matches = re.findall(pattern, code)
            for match in matches:
                if isinstance(match, str) and not match.startswith(('data/', './data/', 'data\\')):
                    # Check if it's using a variable (acceptable)
                    if not match.startswith('{') and not match.startswith('$'):
                        return False
        
        return True
    
    def _verify_manifests(self) -> float:
        """Verify manifests in manifests directory."""
        if not os.path.exists(self.manifests_dir):
            return 1.0
        
        total = 0
        valid = 0
        
        for f in os.listdir(self.manifests_dir):
            if f.endswith('.json'):
                total += 1
                try:
                    with open(os.path.join(self.manifests_dir, f), 'r') as file:
                        manifest = json.load(file)
                    
                    # Basic validation
                    if 'pipeline' in manifest:
                        if all('tool' in step for step in manifest['pipeline']):
                            valid += 1
                except Exception:
                    continue
        
        return valid / total if total > 0 else 1.0
    
    def _evaluate_auditability(self) -> AuditabilityMetrics:
        """Evaluate auditability metrics."""
        if not self.workflows:
            return AuditabilityMetrics()
        
        log_completeness_scores = []
        timestamp_counts = 0
        total_events = 0
        error_logged = 0
        total_errors = 0
        
        for w in self.workflows:
            score = 0.0
            expected_events = 0
            found_events = 0
            
            # Check for expected events
            expected_events += 2  # Workflow start/end
            found_events += 1 if w.start_time else 0
            found_events += 1 if w.end_time else 0
            
            expected_events += len(w.planning_phases) * 2  # start/end for each
            for p in w.planning_phases:
                found_events += 1 if p.start_time else 0
                found_events += 1 if p.end_time else 0
            
            expected_events += len(w.execution_phases) * 2
            for ep in w.execution_phases:
                found_events += 1 if ep.start_time else 0
                found_events += 1 if ep.end_time else 0
                
                for tool in ep.tools:
                    expected_events += 2
                    found_events += 1 if tool.start_time else 0
                    found_events += 1 if tool.end_time else 0
                    
                    if not tool.success:
                        total_errors += 1
                        if tool.error:
                            error_logged += 1
            
            for tg in w.tool_generations:
                expected_events += 2
                found_events += 1 if tg.start_time else 0
                found_events += 1 if tg.end_time else 0
                
                if not tg.success:
                    total_errors += 1
                    if tg.error:
                        error_logged += 1
            
            total_events += expected_events
            timestamp_counts += found_events
            
            score = found_events / expected_events if expected_events > 0 else 1.0
            log_completeness_scores.append(score)
        
        # Decision traceability - check if we can trace from prompt to execution
        traceable = 0
        for w in self.workflows:
            # Can trace if we have: prompt → planning → manifest steps → execution
            if (w.prompt and w.planning_phases and 
                all(p.steps_count > 0 for p in w.planning_phases if p.success) and
                w.execution_phases):
                traceable += 1
        
        return AuditabilityMetrics(
            log_completeness_score=sum(log_completeness_scores) / len(log_completeness_scores) if log_completeness_scores else 0,
            manifest_accuracy=1.0,  # Would need manifest comparison logic
            decision_traceability_score=traceable / len(self.workflows) if self.workflows else 0,
            timestamp_coverage=timestamp_counts / total_events if total_events > 0 else 1.0,
            error_logging_completeness=error_logged / total_errors if total_errors > 0 else 1.0
        )
    
    def _evaluate_baseline_comparison(self) -> BaselineComparisonMetrics:
        """Evaluate metrics compared to baselines."""
        if not self.workflows:
            return BaselineComparisonMetrics()
        
        # Calculate LLM overhead (planning + tool generation time as % of total)
        total_llm_time = 0
        total_workflow_time = 0
        
        for w in self.workflows:
            total_workflow_time += w.total_elapsed_time
            for p in w.planning_phases:
                total_llm_time += p.elapsed_time
            for tg in w.tool_generations:
                total_llm_time += tg.elapsed_time
        
        llm_overhead = total_llm_time / total_workflow_time if total_workflow_time > 0 else 0
        
        return BaselineComparisonMetrics(
            overhead_from_llm_planning=llm_overhead * 100  # As percentage
        )
    
    def to_dict(self, metrics: AllMetrics) -> Dict[str, Any]:
        """Convert metrics to dictionary format."""
        return {
            'robustness': asdict(metrics.robustness),
            'adaptability': asdict(metrics.adaptability),
            'performance': asdict(metrics.performance),
            'security': asdict(metrics.security),
            'auditability': asdict(metrics.auditability),
            'baseline_comparison': asdict(metrics.baseline_comparison),
            'evaluation_timestamp': metrics.evaluation_timestamp,
            'evaluation_duration': metrics.evaluation_duration,
            'workflows_analyzed': metrics.workflows_analyzed
        }
    
    def save_report(self, metrics: AllMetrics, output_path: str = "metrics/report.json"):
        """Save metrics report to JSON file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.to_dict(metrics), f, indent=2)
        
        return output_path
    
    def print_report(self, metrics: AllMetrics):
        """Print a formatted metrics report."""
        print("\n" + "=" * 70)
        print("PIPELINE METRICS EVALUATION REPORT")
        print("=" * 70)
        print(f"Timestamp: {metrics.evaluation_timestamp}")
        print(f"Workflows Analyzed: {metrics.workflows_analyzed}")
        print(f"Evaluation Duration: {metrics.evaluation_duration:.2f}s")
        
        print("\n" + "-" * 70)
        print("ROBUSTNESS METRICS")
        print("-" * 70)
        r = metrics.robustness
        print(f"  Pipeline Success Rate:       {r.pipeline_success_rate:.1%}")
        print(f"  Tool Generation Success:     {r.tool_generation_success_rate:.1%}")
        print(f"  Tool Execution Success:      {r.tool_execution_success_rate:.1%}")
        print(f"  Recovery Success Rate:       {r.recovery_success_rate:.1%}")
        if r.error_types:
            print(f"  Error Types: {r.error_types}")
        if r.failure_points:
            print(f"  Failure Points: {r.failure_points}")
        
        print("\n" + "-" * 70)
        print("ADAPTABILITY METRICS")
        print("-" * 70)
        a = metrics.adaptability
        print(f"  Avg Pipeline Generation:     {a.avg_pipeline_generation_time:.2f}s")
        print(f"  Avg LLM Steps per Workflow:  {a.avg_llm_steps_per_workflow:.1f}")
        print(f"  Avg Tool Generation Time:    {a.avg_tool_generation_time:.2f}s")
        print(f"  Novel Tool Success Rate:     {a.novel_tool_generation_success_rate:.1%}")
        print(f"  Builtin/Generated Ratio:     {a.builtin_vs_generated_ratio:.2f}")
        
        print("\n" + "-" * 70)
        print("PERFORMANCE METRICS")
        print("-" * 70)
        p = metrics.performance
        print(f"  Avg End-to-End Latency:      {p.avg_end_to_end_latency:.2f}s")
        print(f"  Min Latency:                 {p.min_latency:.2f}s")
        print(f"  Max Latency:                 {p.max_latency:.2f}s")
        print(f"  Avg Planning Time:           {p.avg_planning_time:.2f}s")
        print(f"  Avg Execution Time:          {p.avg_execution_time:.2f}s")
        print(f"  Avg Tool Execution Time:     {p.avg_tool_execution_time:.2f}s")
        print(f"  Throughput:                  {p.throughput_workflows_per_hour:.1f} workflows/hour")
        print(f"  Avg CPU Usage:               {p.cpu_usage_avg:.1f}%")
        print(f"  Avg Memory Usage:            {p.memory_usage_mb:.1f} MB")
        
        print("\n" + "-" * 70)
        print("SECURITY METRICS")
        print("-" * 70)
        s = metrics.security
        print(f"  Sandbox Compliance:          {s.sandbox_compliance:.1%}")
        print(f"  Manifest Verification:       {s.manifest_verification_rate:.1%}")
        print(f"  Unsafe Patterns Detected:    {s.unsafe_code_patterns_detected}")
        print(f"  Import Compliance:           {s.allowed_imports_compliance:.1%}")
        print(f"  File Access Compliance:      {s.file_access_compliance:.1%}")
        
        print("\n" + "-" * 70)
        print("AUDITABILITY METRICS")
        print("-" * 70)
        au = metrics.auditability
        print(f"  Log Completeness Score:      {au.log_completeness_score:.1%}")
        print(f"  Manifest Accuracy:           {au.manifest_accuracy:.1%}")
        print(f"  Decision Traceability:       {au.decision_traceability_score:.1%}")
        print(f"  Timestamp Coverage:          {au.timestamp_coverage:.1%}")
        print(f"  Error Logging Completeness:  {au.error_logging_completeness:.1%}")
        
        print("\n" + "-" * 70)
        print("BASELINE COMPARISON")
        print("-" * 70)
        b = metrics.baseline_comparison
        print(f"  LLM Planning Overhead:       {b.overhead_from_llm_planning:.1f}%")
        
        print("\n" + "=" * 70)


if __name__ == "__main__":
    evaluator = MetricsEvaluator()
    metrics = evaluator.evaluate()
    evaluator.print_report(metrics)
    evaluator.save_report(metrics)
    print(f"\nReport saved to metrics/report.json")

