#!/usr/bin/env python3
"""Compact audit logging for pipeline execution."""

import os
from datetime import datetime

_LOG_FILE = "audit/execution.log"
_start_times = {}


def _ts():
    """Return compact timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def _write(event, msg=""):
    """Write a single log line."""
    os.makedirs(os.path.dirname(_LOG_FILE), exist_ok=True)
    line = f"{_ts()} | {event:<12} | {msg}\n"
    with open(_LOG_FILE, "a") as f:
        f.write(line)


def workflow_start(prompt, file_path=None):
    """Log workflow start."""
    _start_times["workflow"] = datetime.now()
    _write("WORKFLOW", f"START prompt=\"{prompt}\" file={file_path}")


def workflow_end(success):
    """Log workflow end with total time."""
    elapsed = ""
    if "workflow" in _start_times:
        elapsed = f" elapsed={(datetime.now()-_start_times['workflow']).total_seconds():.2f}s"
    _write("WORKFLOW", f"END success={success}{elapsed}")


def planning_start():
    """Log manifest planning start."""
    _start_times["planning"] = datetime.now()
    _write("PLANNING", "START")


def planning_end(manifest):
    """Log manifest planning end."""
    elapsed = ""
    if "planning" in _start_times:
        elapsed = f" elapsed={(datetime.now()-_start_times['planning']).total_seconds():.2f}s"
    if "error" in manifest:
        _write("PLANNING", f"FAIL error=\"{manifest['error']}\"{elapsed}")
    else:
        steps = len(manifest.get("pipeline", []))
        _write("PLANNING", f"OK steps={steps}{elapsed}")


def execution_start():
    """Log pipeline execution start."""
    _start_times["execution"] = datetime.now()
    _write("EXECUTION", "START")


def execution_end(results):
    """Log pipeline execution end."""
    elapsed = ""
    if "execution" in _start_times:
        elapsed = f" elapsed={(datetime.now()-_start_times['execution']).total_seconds():.2f}s"
    if "error" in results:
        _write("EXECUTION", f"FAIL error=\"{results['error']}\"{elapsed}")
    else:
        _write("EXECUTION", f"OK{elapsed}")


def tool_start(step, tool_name, tool_type, args):
    """Log tool execution start."""
    _start_times[f"step_{step}"] = datetime.now()
    args_str = ",".join(f"{k}={v}" for k,v in args.items() if not str(v).startswith("/"))[:60]
    _write("TOOL", f"START step={step} tool={tool_name} type={tool_type} args=[{args_str}]")


def tool_end(step, tool_name, success, output_path=None, error=None):
    """Log tool execution end."""
    elapsed = ""
    if f"step_{step}" in _start_times:
        elapsed = f" elapsed={(datetime.now()-_start_times[f'step_{step}']).total_seconds():.2f}s"
    if success:
        out = f" output={os.path.basename(output_path)}" if output_path else ""
        _write("TOOL", f"OK step={step} tool={tool_name}{out}{elapsed}")
    else:
        _write("TOOL", f"FAIL step={step} tool={tool_name} error=\"{error}\"{elapsed}")


def tool_gen_start(tool_name):
    """Log tool generation start."""
    _start_times[f"gen_{tool_name}"] = datetime.now()
    _write("TOOLGEN", f"START tool={tool_name}")


def tool_gen_end(tool_name, success, actual_name=None, error=None):
    """Log tool generation end."""
    elapsed = ""
    if f"gen_{tool_name}" in _start_times:
        elapsed = f" elapsed={(datetime.now()-_start_times[f'gen_{tool_name}']).total_seconds():.2f}s"
    if success:
        name_info = f" as={actual_name}" if actual_name and actual_name != tool_name else ""
        _write("TOOLGEN", f"OK tool={tool_name}{name_info}{elapsed}")
    else:
        _write("TOOLGEN", f"FAIL tool={tool_name} error=\"{error}\"{elapsed}")


def merge_start(video, audio):
    """Log merge operation start."""
    _start_times["merge"] = datetime.now()
    _write("MERGE", f"START video={os.path.basename(video)} audio={os.path.basename(audio)}")


def merge_end(success, output_path=None, error=None):
    """Log merge operation end."""
    elapsed = ""
    if "merge" in _start_times:
        elapsed = f" elapsed={(datetime.now()-_start_times['merge']).total_seconds():.2f}s"
    if success:
        _write("MERGE", f"OK output={os.path.basename(output_path)}{elapsed}")
    else:
        _write("MERGE", f"FAIL error=\"{error}\"{elapsed}")


def error(msg):
    """Log an error."""
    _write("ERROR", msg)


def retry(attempt, max_attempts, error_msg):
    """Log a retry attempt."""
    _write("RETRY", f"attempt={attempt}/{max_attempts} error=\"{error_msg}\"")


class AuditLog:
    """Context manager for workflow auditing."""
    
    def __init__(self, prompt, file_path=None):
        self.prompt = prompt
        self.file_path = file_path
        self.success = False
    
    def __enter__(self):
        workflow_start(self.prompt, self.file_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            error(f"{exc_type.__name__}: {exc_val}")
            self.success = False
        workflow_end(self.success)
        return False

