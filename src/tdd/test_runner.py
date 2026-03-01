"""Test Runner for TDD workflow.

This module runs pytest and parses results for TDD state tracking.
"""

import os
import re
import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


def _get_python_cmd() -> str:
    """Get the Python command to use."""
    return sys.executable


@dataclass
class TestResult:
    """Represents test execution results."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration: float = 0.0
    coverage: float = 0.0
    failures: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.failures is None:
            self.failures = []


class TestRunner:
    """Runs pytest and captures results."""
    
    def __init__(self, runner_type: str = "pytest"):
        self.runner_type = runner_type
    
    def run(self, test_path: str, coverage: bool = True) -> TestResult:
        """Run tests and return results.
        
        Args:
            test_path: Path to test files or directory
            coverage: Whether to collect coverage
            
        Returns:
            TestResult with execution details
        """
        result = run_tests(test_path, coverage)
        return TestResult(
            total=result.get('total', 0),
            passed=result.get('passed', 0),
            failed=result.get('failed', 0),
            skipped=result.get('skipped', 0),
            errors=result.get('errors', 0),
            duration=result.get('duration', 0.0),
            coverage=result.get('coverage', 0.0),
            failures=result.get('failures', [])
        )
    
    def run_tests(self, test_path: str, coverage: bool = True) -> dict:
        """Run pytest and return structured results.
        
        Args:
            test_path: Path to test files or directory
            coverage: Whether to collect coverage
            
        Returns:
            Dictionary with test results
        """
        return run_tests(test_path, coverage)
    
    def parse_pytest_output(self, output: str) -> dict:
        """Parse pytest output for RED/GREEN status.
        
        Extracts:
        - passed, failed, errors counts
        - coverage percentage
        - failure messages
        
        Args:
            output: Raw pytest output
            
        Returns:
            Structured dictionary with parsed results
        """
        return parse_pytest_output(output)
    
    def is_red(self, results: dict) -> bool:
        """Check if tests are in RED state (failures expected).
        
        RED state means tests are failing, which is expected
        during the initial TDD phase before implementation.
        
        Args:
            results: Test results dictionary
            
        Returns:
            True if tests are failing (RED state)
        """
        failed = results.get('failed', 0)
        errors = results.get('errors', 0)
        return failed > 0 or errors > 0
    
    def is_green(self, results: dict) -> bool:
        """Check if tests are in GREEN state (all pass).
        
        GREEN state means all tests are passing, indicating
        the implementation phase is complete.
        
        Args:
            results: Test results dictionary
            
        Returns:
            True if all tests pass (GREEN state)
        """
        failed = results.get('failed', 0)
        errors = results.get('errors', 0)
        passed = results.get('passed', 0)
        return passed > 0 and failed == 0 and errors == 0


def run_tests(test_path: str, coverage: bool = True) -> Dict[str, Any]:
    """Run pytest and return results.
    
    This function:
    1. Runs pytest with optional coverage
    2. Captures output
    3. Parses results for status
    
    Args:
        test_path: Path to test files or directory
        coverage: Whether to run with coverage
        
    Returns:
        Dictionary with test results
    """
    result = {
        "status": "unknown",
        "test_path": test_path,
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "duration": 0.0,
        "coverage": 0.0,
        "failures": [],
        "output": "",
        "error": None
    }
    
    python_cmd = _get_python_cmd()
    
    # Build pytest command
    cmd = [python_cmd, "-m", "pytest", test_path, "-v"]
    
    if coverage:
        cmd.extend(["--cov", ".", "--cov-report=term-missing"])
    
    # Add JSON output for parsing
    cmd.extend(["--tb=short"])
    
    try:
        # Run pytest with inherited environment
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd() + ':' + env.get('PYTHONPATH', '')
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            env=env
        )
        
        output = process.stdout + process.stderr
        result["output"] = output
        
        # Parse the output
        parsed = parse_pytest_output(output)
        result.update(parsed)
        
        # Determine status
        if result["failed"] > 0 or result["errors"] > 0:
            result["status"] = "failed"
        elif result["passed"] > 0:
            result["status"] = "passed"
        elif result["skipped"] > 0:
            result["status"] = "skipped"
        else:
            result["status"] = "no_tests"
            
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = "Test execution timed out"
    except FileNotFoundError:
        result["status"] = "error"
        result["error"] = "pytest not found. Install with: pip install pytest pytest-cov"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result


def parse_pytest_output(output: str) -> Dict[str, Any]:
    """Parse pytest output for status.
    
    This function extracts:
    - Pass/fail counts
    - Coverage percentage
    - Error messages
    
    Args:
        output: Raw pytest output
        
    Returns:
        Dictionary with parsed results
    """
    result = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "duration": 0.0,
        "coverage": 0.0,
        "failures": []
    }
    
    # Parse test counts from summary line
    # Example: "5 passed, 2 failed, 1 skipped in 0.05s"
    summary_pattern = r'(\d+) passed(?:, (\d+) failed)?(?:, (\d+) skipped)?(?:, (\d+) error)? in ([\d.]+)s'
    
    for line in output.split('\n'):
        # Match summary line
        match = re.search(summary_pattern, line)
        if match:
            result["passed"] = int(match.group(1) or 0)
            result["failed"] = int(match.group(2) or 0)
            result["skipped"] = int(match.group(3) or 0)
            result["errors"] = int(match.group(4) or 0)
            result["duration"] = float(match.group(5) or 0)
            result["total"] = result["passed"] + result["failed"] + result["skipped"] + result["errors"]
        
        # Parse coverage percentage
        # Example: "TOTAL 85%"
        coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)%', line)
        if coverage_match:
            result["coverage"] = float(coverage_match.group(1))
        
        # Alternative coverage format
        # Example: "Coverage.py warning:... 85%"
        alt_coverage = re.search(r'coverage.*?(\d+)%', line, re.IGNORECASE)
        if alt_coverage and result["coverage"] == 0:
            result["coverage"] = float(alt_coverage.group(1))
    
    # Parse failure details
    result["failures"] = _parse_failures(output)
    
    return result


def _parse_failures(output: str) -> List[Dict[str, Any]]:
    """Parse failure details from pytest output.
    
    Args:
        output: Raw pytest output
        
    Returns:
        List of failure dictionaries
    """
    failures = []
    
    # Split output by failure sections
    # Look for patterns like "FAILED test_file.py::TestClass::test_method"
    failure_pattern = r'FAILED\s+(\S+)::(\S+)'
    
    lines = output.split('\n')
    current_failure = None
    
    for i, line in enumerate(lines):
        # Check for failure header
        match = re.search(failure_pattern, line)
        if match:
            if current_failure:
                failures.append(current_failure)
            
            file_path = match.group(1)
            test_name = match.group(2)
            
            current_failure = {
                "file": file_path,
                "test": test_name,
                "error_type": "",
                "message": "",
                "details": []
            }
        
        # Capture error details after failure header
        elif current_failure and line.strip():
            # Look for assertion errors
            if 'AssertionError' in line or 'Error' in line or 'Exception' in line:
                current_failure["error_type"] = line.strip()
            # Capture the next few lines as details
            elif len(current_failure["details"]) < 10:
                current_failure["details"].append(line)
    
    # Don't forget the last failure
    if current_failure:
        failures.append(current_failure)
    
    # Extract error messages from details
    for failure in failures:
        if failure["details"]:
            # Find the assertion line
            for detail in failure["details"]:
                if 'assert' in detail.lower():
                    failure["message"] = detail.strip()
                    break
            if not failure["message"]:
                failure["message"] = '\n'.join(failure["details"][:3])
    
    return failures


def run_specific_tests(test_names: List[str], test_path: str = ".") -> Dict[str, Any]:
    """Run specific test methods or classes.
    
    Args:
        test_names: List of test names to run
        test_path: Base path for tests
        
    Returns:
        Dictionary with test results
    """
    if not test_names:
        return run_tests(test_path)
    
    python_cmd = _get_python_cmd()
    
    # Build command with specific test selection
    cmd = [python_cmd, "-m", "pytest", "-v"]
    
    for test_name in test_names:
        cmd.append(f"{test_path}::{test_name}")
    
    result = {
        "status": "unknown",
        "tests": test_names,
        "total": 0,
        "passed": 0,
        "failed": 0,
        "output": "",
        "error": None
    }
    
    try:
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        output = process.stdout + process.stderr
        result["output"] = output
        
        parsed = parse_pytest_output(output)
        result.update(parsed)
        
        if result["failed"] > 0:
            result["status"] = "failed"
        elif result["passed"] > 0:
            result["status"] = "passed"
            
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result
