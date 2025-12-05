#!/usr/bin/env python3
"""Parser for audit execution logs."""

import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class ResourceSnapshot:
    """Represents a resource usage snapshot."""
    cpu_percent: float
    memory_mb: float
    context: str
    timestamp: datetime


@dataclass
class ToolExecution:
    """Represents a single tool execution."""
    step: int
    tool_name: str
    tool_type: str
    args: Dict[str, Any]
    success: bool
    elapsed_time: float
    output_path: Optional[str] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class ToolGeneration:
    """Represents a tool generation event."""
    tool_name: str
    success: bool
    elapsed_time: float
    actual_name: Optional[str] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class PlanningPhase:
    """Represents a planning phase."""
    success: bool
    steps_count: int
    elapsed_time: float
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class ExecutionPhase:
    """Represents an execution phase."""
    success: bool
    elapsed_time: float
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tools: List[ToolExecution] = field(default_factory=list)


@dataclass
class RetryAttempt:
    """Represents a retry attempt."""
    attempt: int
    max_attempts: int
    error: str
    timestamp: datetime


@dataclass
class WorkflowExecution:
    """Represents a complete workflow execution."""
    prompt: str
    file_path: Optional[str]
    success: bool
    total_elapsed_time: float
    start_time: datetime
    end_time: Optional[datetime] = None
    planning_phases: List[PlanningPhase] = field(default_factory=list)
    execution_phases: List[ExecutionPhase] = field(default_factory=list)
    tool_generations: List[ToolGeneration] = field(default_factory=list)
    retry_attempts: List[RetryAttempt] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    merge_success: Optional[bool] = None
    merge_elapsed: Optional[float] = None
    resource_snapshots: List[ResourceSnapshot] = field(default_factory=list)


class AuditLogParser:
    """Parser for audit execution logs."""
    
    # Regex patterns for log parsing
    TIMESTAMP_PATTERN = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})'
    EVENT_PATTERN = rf'{TIMESTAMP_PATTERN} \| (\w+)\s+\| (.+)'
    
    def __init__(self, log_file: str = "audit/execution.log"):
        self.log_file = log_file
        self.workflows: List[WorkflowExecution] = []
    
    def parse(self) -> List[WorkflowExecution]:
        """Parse the audit log file and return workflow executions."""
        if not os.path.exists(self.log_file):
            return []
        
        with open(self.log_file, 'r') as f:
            lines = f.readlines()
        
        self.workflows = []
        current_workflow = None
        current_execution = None
        pending_tools = {}  # Track tools waiting for end events
        pending_toolgen = {}  # Track tool generations waiting for end events
        
        for line in lines:
            match = re.match(self.EVENT_PATTERN, line.strip())
            if not match:
                continue
            
            timestamp_str, event_type, message = match.groups()
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
            
            # Parse based on event type
            if event_type == "WORKFLOW":
                if "START" in message:
                    # Extract prompt and file path
                    prompt_match = re.search(r'prompt="([^"]*)"', message)
                    file_match = re.search(r'file=(.+)$', message)
                    
                    prompt = prompt_match.group(1) if prompt_match else ""
                    file_path = file_match.group(1) if file_match else None
                    
                    current_workflow = WorkflowExecution(
                        prompt=prompt,
                        file_path=file_path,
                        success=False,
                        total_elapsed_time=0.0,
                        start_time=timestamp
                    )
                    current_execution = None
                    pending_tools = {}
                    pending_toolgen = {}
                    
                elif "END" in message and current_workflow:
                    success_match = re.search(r'success=(True|False)', message)
                    elapsed_match = re.search(r'elapsed=(\d+\.?\d*)s', message)
                    
                    current_workflow.success = success_match.group(1) == "True" if success_match else False
                    current_workflow.total_elapsed_time = float(elapsed_match.group(1)) if elapsed_match else 0.0
                    current_workflow.end_time = timestamp
                    
                    self.workflows.append(current_workflow)
                    current_workflow = None
            
            elif event_type == "PLANNING" and current_workflow:
                if "START" in message:
                    planning = PlanningPhase(
                        success=False,
                        steps_count=0,
                        elapsed_time=0.0,
                        start_time=timestamp
                    )
                    current_workflow.planning_phases.append(planning)
                    
                elif "OK" in message or "FAIL" in message:
                    if current_workflow.planning_phases:
                        planning = current_workflow.planning_phases[-1]
                        planning.success = "OK" in message
                        planning.end_time = timestamp
                        
                        steps_match = re.search(r'steps=(\d+)', message)
                        elapsed_match = re.search(r'elapsed=(\d+\.?\d*)s', message)
                        error_match = re.search(r'error="([^"]*)"', message)
                        
                        planning.steps_count = int(steps_match.group(1)) if steps_match else 0
                        planning.elapsed_time = float(elapsed_match.group(1)) if elapsed_match else 0.0
                        planning.error = error_match.group(1) if error_match else None
            
            elif event_type == "EXECUTION" and current_workflow:
                if "START" in message:
                    current_execution = ExecutionPhase(
                        success=False,
                        elapsed_time=0.0,
                        start_time=timestamp
                    )
                    current_workflow.execution_phases.append(current_execution)
                    
                elif ("OK" in message or "FAIL" in message) and current_execution:
                    current_execution.success = "OK" in message
                    current_execution.end_time = timestamp
                    
                    elapsed_match = re.search(r'elapsed=(\d+\.?\d*)s', message)
                    error_match = re.search(r'error="([^"]*)"', message)
                    
                    current_execution.elapsed_time = float(elapsed_match.group(1)) if elapsed_match else 0.0
                    current_execution.error = error_match.group(1) if error_match else None
            
            elif event_type == "TOOL" and current_workflow and current_execution:
                if "START" in message:
                    step_match = re.search(r'step=(\d+)', message)
                    tool_match = re.search(r'tool=(\w+)', message)
                    type_match = re.search(r'type=(\w+)', message)
                    args_match = re.search(r'args=\[([^\]]*)\]', message)
                    
                    step = int(step_match.group(1)) if step_match else 0
                    tool_name = tool_match.group(1) if tool_match else "unknown"
                    tool_type = type_match.group(1) if type_match else "unknown"
                    
                    # Parse args
                    args = {}
                    if args_match and args_match.group(1):
                        for arg in args_match.group(1).split(','):
                            if '=' in arg:
                                k, v = arg.split('=', 1)
                                args[k.strip()] = v.strip()
                    
                    tool_exec = ToolExecution(
                        step=step,
                        tool_name=tool_name,
                        tool_type=tool_type,
                        args=args,
                        success=False,
                        elapsed_time=0.0,
                        start_time=timestamp
                    )
                    pending_tools[step] = tool_exec
                    
                elif "OK" in message or "FAIL" in message:
                    step_match = re.search(r'step=(\d+)', message)
                    step = int(step_match.group(1)) if step_match else 0
                    
                    if step in pending_tools:
                        tool_exec = pending_tools.pop(step)
                        tool_exec.success = "OK" in message
                        tool_exec.end_time = timestamp
                        
                        elapsed_match = re.search(r'elapsed=(\d+\.?\d*)s', message)
                        output_match = re.search(r'output=(\S+)', message)
                        error_match = re.search(r'error="([^"]*)"', message)
                        
                        tool_exec.elapsed_time = float(elapsed_match.group(1)) if elapsed_match else 0.0
                        tool_exec.output_path = output_match.group(1) if output_match else None
                        tool_exec.error = error_match.group(1) if error_match else None
                        
                        current_execution.tools.append(tool_exec)
            
            elif event_type == "TOOLGEN" and current_workflow:
                if "START" in message:
                    tool_match = re.search(r'tool=(\w+)', message)
                    tool_name = tool_match.group(1) if tool_match else "unknown"
                    
                    toolgen = ToolGeneration(
                        tool_name=tool_name,
                        success=False,
                        elapsed_time=0.0,
                        start_time=timestamp
                    )
                    pending_toolgen[tool_name] = toolgen
                    
                elif "OK" in message or "FAIL" in message:
                    tool_match = re.search(r'tool=(\w+)', message)
                    tool_name = tool_match.group(1) if tool_match else "unknown"
                    
                    if tool_name in pending_toolgen:
                        toolgen = pending_toolgen.pop(tool_name)
                        toolgen.success = "OK" in message
                        toolgen.end_time = timestamp
                        
                        elapsed_match = re.search(r'elapsed=(\d+\.?\d*)s', message)
                        actual_match = re.search(r'as=(\w+)', message)
                        error_match = re.search(r'error="([^"]*)"', message)
                        
                        toolgen.elapsed_time = float(elapsed_match.group(1)) if elapsed_match else 0.0
                        toolgen.actual_name = actual_match.group(1) if actual_match else None
                        toolgen.error = error_match.group(1) if error_match else None
                        
                        current_workflow.tool_generations.append(toolgen)
            
            elif event_type == "RETRY" and current_workflow:
                attempt_match = re.search(r'attempt=(\d+)/(\d+)', message)
                error_match = re.search(r'error="([^"]*)"', message)
                
                if attempt_match:
                    retry = RetryAttempt(
                        attempt=int(attempt_match.group(1)),
                        max_attempts=int(attempt_match.group(2)),
                        error=error_match.group(1) if error_match else "",
                        timestamp=timestamp
                    )
                    current_workflow.retry_attempts.append(retry)
            
            elif event_type == "MERGE" and current_workflow:
                if "OK" in message:
                    current_workflow.merge_success = True
                    elapsed_match = re.search(r'elapsed=(\d+\.?\d*)s', message)
                    current_workflow.merge_elapsed = float(elapsed_match.group(1)) if elapsed_match else 0.0
                elif "FAIL" in message:
                    current_workflow.merge_success = False
            
            elif event_type == "ERROR" and current_workflow:
                current_workflow.errors.append(message)
            
            elif event_type == "RESOURCE" and current_workflow:
                cpu_match = re.search(r'cpu=(\d+\.?\d*)%', message)
                mem_match = re.search(r'mem=(\d+\.?\d*)MB', message)
                ctx_match = re.search(r'context=(\S+)', message)
                
                if cpu_match and mem_match:
                    snapshot = ResourceSnapshot(
                        cpu_percent=float(cpu_match.group(1)),
                        memory_mb=float(mem_match.group(1)),
                        context=ctx_match.group(1) if ctx_match else "",
                        timestamp=timestamp
                    )
                    current_workflow.resource_snapshots.append(snapshot)
        
        return self.workflows
    
    def get_workflows_in_range(self, start_time: datetime = None, 
                               end_time: datetime = None) -> List[WorkflowExecution]:
        """Filter workflows by time range."""
        if not self.workflows:
            self.parse()
        
        filtered = self.workflows
        
        if start_time:
            filtered = [w for w in filtered if w.start_time >= start_time]
        if end_time:
            filtered = [w for w in filtered if w.start_time <= end_time]
        
        return filtered
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all parsed workflows."""
        if not self.workflows:
            self.parse()
        
        if not self.workflows:
            return {"error": "No workflows found in log"}
        
        total = len(self.workflows)
        successful = sum(1 for w in self.workflows if w.success)
        
        # Calculate aggregate metrics
        all_tool_execs = []
        all_tool_gens = []
        total_retries = 0
        
        for w in self.workflows:
            for ep in w.execution_phases:
                all_tool_execs.extend(ep.tools)
            all_tool_gens.extend(w.tool_generations)
            total_retries += len(w.retry_attempts)
        
        return {
            "total_workflows": total,
            "successful_workflows": successful,
            "failed_workflows": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "total_tool_executions": len(all_tool_execs),
            "successful_tool_executions": sum(1 for t in all_tool_execs if t.success),
            "total_tool_generations": len(all_tool_gens),
            "successful_tool_generations": sum(1 for t in all_tool_gens if t.success),
            "total_retries": total_retries,
            "avg_workflow_time": sum(w.total_elapsed_time for w in self.workflows) / total if total > 0 else 0,
            "avg_tool_execution_time": sum(t.elapsed_time for t in all_tool_execs) / len(all_tool_execs) if all_tool_execs else 0,
            "avg_tool_generation_time": sum(t.elapsed_time for t in all_tool_gens) / len(all_tool_gens) if all_tool_gens else 0,
        }


if __name__ == "__main__":
    # Test the parser
    parser = AuditLogParser()
    workflows = parser.parse()
    
    print(f"\nParsed {len(workflows)} workflows")
    print("\nSummary:")
    summary = parser.get_summary()
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print("\nWorkflow Details:")
    for i, w in enumerate(workflows, 1):
        print(f"\n{i}. {w.prompt[:50]}...")
        print(f"   Success: {w.success}, Time: {w.total_elapsed_time:.2f}s")
        print(f"   Planning phases: {len(w.planning_phases)}")
        print(f"   Execution phases: {len(w.execution_phases)}")
        print(f"   Tool generations: {len(w.tool_generations)}")
        print(f"   Retries: {len(w.retry_attempts)}")

