"""TDD Reporter for progress tracking and reporting.

This module generates human-readable reports of TDD progress.
"""

import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CycleReport:
    """Report for a single TDD cycle."""
    cycle_id: str
    spec_id: str
    state: str
    start_time: datetime
    end_time: Optional[datetime] = None
    phases: List[Dict[str, Any]] = field(default_factory=list)
    test_count: int = 0
    pass_count: int = 0
    coverage: float = 0.0
    duration_minutes: float = 0.0


class TDDReporter:
    """Generates TDD progress reports."""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.reports_dir = self.project_path / ".tdd_reports"
    
    def generate_cycle_report(self, cycle_data: Dict[str, Any]) -> str:
        """Generate a report for a TDD cycle.
        
        Args:
            cycle_data: Dictionary with cycle information
            
        Returns:
            Formatted report string
        """
        return generate_cycle_report(cycle_data)
    
    def generate_summary(self, cycles: List[Dict[str, Any]]) -> str:
        """Generate summary report for multiple cycles.
        
        Args:
            cycles: List of cycle data dictionaries
            
        Returns:
            Formatted summary string
        """
        lines = [
            "=" * 60,
            "TDD SUMMARY REPORT",
            "=" * 60,
            f"Generated: {datetime.now().isoformat()}",
            f"Total Cycles: {len(cycles)}",
            ""
        ]
        
        # Calculate statistics
        total_tests = sum(c.get('test_count', 0) for c in cycles)
        total_passed = sum(c.get('pass_count', 0) for c in cycles)
        avg_coverage = sum(c.get('coverage', 0) for c in cycles) / len(cycles) if cycles else 0
        
        completed = sum(1 for c in cycles if c.get('state') == 'COMPLETE')
        
        lines.extend([
            "Statistics:",
            f"  Completed Cycles: {completed}/{len(cycles)}",
            f"  Total Tests: {total_tests}",
            f"  Tests Passed: {total_passed}",
            f"  Average Coverage: {avg_coverage:.1f}%",
            "",
            "Cycle Details:",
            "-" * 40
        ])
        
        for i, cycle in enumerate(cycles, 1):
            lines.append(f"\n{i}. {cycle.get('spec_id', 'Unknown')}")
            lines.append(f"   State: {cycle.get('state', 'UNKNOWN')}")
            lines.append(f"   Tests: {cycle.get('pass_count', 0)}/{cycle.get('test_count', 0)} passed")
            lines.append(f"   Coverage: {cycle.get('coverage', 0):.1f}%")
        
        lines.extend([
            "",
            "=" * 60
        ])
        
        return '\n'.join(lines)
    
    def save_report(self, report: str, filename: Optional[str] = None) -> str:
        """Save a report to file.
        
        Args:
            report: Report content
            filename: Optional filename (default: timestamp)
            
        Returns:
            Path to saved report
        """
        os.makedirs(self.reports_dir, exist_ok=True)
        
        if filename is None:
            filename = f"tdd_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        report_path = self.reports_dir / filename
        
        with open(report_path, 'w') as f:
            f.write(report)
        
        return str(report_path)


def generate_cycle_report(cycle_data: Dict[str, Any]) -> str:
    """Generate a formatted report for a TDD cycle.
    
    Args:
        cycle_data: Dictionary with cycle information
        
    Returns:
        Formatted report string
    """
    lines = [
        "=" * 60,
        "TDD CYCLE REPORT",
        "=" * 60,
        ""
    ]
    
    # Basic info
    lines.extend([
        f"Cycle ID: {cycle_data.get('id', 'N/A')}",
        f"Specification: {cycle_data.get('spec_id', 'N/A')}",
        f"Current State: {cycle_data.get('state', 'UNKNOWN')}",
        ""
    ])
    
    # Timing
    start_time = cycle_data.get('start_time')
    if start_time:
        lines.append(f"Started: {start_time}")
    
    end_time = cycle_data.get('end_time')
    if end_time:
        lines.append(f"Completed: {end_time}")
    
    lines.append("")
    
    # Phase history
    phases = cycle_data.get('phases', [])
    if phases:
        lines.extend([
            "Phase History:",
            "-" * 40
        ])
        
        for phase in phases:
            phase_name = phase.get('phase', 'UNKNOWN')
            start = phase.get('start_time', 'N/A')
            end = phase.get('end_time')
            tests = phase.get('test_count', 0)
            passed = phase.get('pass_count', 0)
            coverage = phase.get('coverage', 0)
            
            lines.append(f"\n  {phase_name}:")
            lines.append(f"    Started: {start}")
            if end:
                lines.append(f"    Completed: {end}")
            if tests > 0:
                lines.append(f"    Tests: {passed}/{tests} passed")
            if coverage > 0:
                lines.append(f"    Coverage: {coverage:.1f}%")
            
            notes = phase.get('notes', '')
            if notes:
                lines.append(f"    Notes: {notes}")
        
        lines.append("")
    
    # Current status
    lines.extend([
        "Current Status:",
        "-" * 40
    ])
    
    test_count = cycle_data.get('test_count', 0)
    pass_count = cycle_data.get('pass_count', 0)
    coverage = cycle_data.get('coverage', 0)
    
    lines.append(f"  Tests: {pass_count}/{test_count} passing")
    lines.append(f"  Coverage: {coverage:.1f}%")
    
    # State-specific messages
    state = cycle_data.get('state', 'UNKNOWN')
    lines.append(f"  State: {state}")
    
    if state == 'RED':
        lines.append("\n  🔴 RED Phase: Tests are failing as expected.")
        lines.append("     Next: Implement minimal code to make tests pass.")
    elif state == 'GREEN':
        lines.append("\n  🟢 GREEN Phase: All tests passing.")
        lines.append("     Next: Refactor code while keeping tests green.")
    elif state == 'REFACTOR':
        lines.append("\n  🟡 REFACTOR Phase: Improving code quality.")
        lines.append("     Next: Complete refactoring and verify tests still pass.")
    elif state == 'COMPLETE':
        lines.append("\n  ✅ COMPLETE: TDD cycle finished successfully.")
    
    lines.extend([
        "",
        "=" * 60
    ])
    
    return '\n'.join(lines)


def generate_status_line(state: str, tests_passed: int, tests_total: int, 
                         coverage: float) -> str:
    """Generate a single-line status summary.
    
    Args:
        state: Current TDD state
        tests_passed: Number of passing tests
        tests_total: Total number of tests
        coverage: Coverage percentage
        
    Returns:
        Status line string
    """
    state_emoji = {
        'IDLE': '⚪',
        'RED': '🔴',
        'GREEN': '🟢',
        'REFACTOR': '🟡',
        'COMPLETE': '✅'
    }.get(state, '⚪')
    
    return f"{state_emoji} {state:8} | Tests: {tests_passed}/{tests_total} | Coverage: {coverage:.1f}%"


def format_test_failures(failures: List[Dict[str, Any]], max_failures: int = 5) -> str:
    """Format test failures for display.
    
    Args:
        failures: List of failure dictionaries
        max_failures: Maximum failures to show
        
    Returns:
        Formatted failure report
    """
    if not failures:
        return "No failures to report."
    
    lines = [
        f"Test Failures ({min(len(failures), max_failures)} of {len(failures)} shown):",
        "-" * 40
    ]
    
    for i, failure in enumerate(failures[:max_failures], 1):
        lines.append(f"\n{i}. {failure.get('test', 'Unknown test')}")
        lines.append(f"   File: {failure.get('file', 'Unknown file')}")
        
        error_type = failure.get('error_type', '')
        if error_type:
            lines.append(f"   Error: {error_type}")
        
        message = failure.get('message', '')
        if message:
            lines.append(f"   Message: {message[:200]}")
    
    return '\n'.join(lines)


def generate_progress_bar(percentage: float, width: int = 30) -> str:
    """Generate a text progress bar.
    
    Args:
        percentage: Percentage (0-100)
        width: Width of the bar in characters
        
    Returns:
        Progress bar string
    """
    filled = int(width * percentage / 100)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {percentage:.1f}%"
