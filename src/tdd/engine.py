"""RED-GREEN-REFACTOR Engine for TDD workflow.

This module implements the TDD state machine and phase management.
"""

import os
import re
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path


class TDDState(Enum):
    """TDD cycle states."""
    IDLE = "idle"
    RED = "red"
    GREEN = "green"
    REFACTOR = "refactor"
    COMPLETE = "complete"


@dataclass
class PhaseRecord:
    """Record of a TDD phase transition."""
    phase: TDDState
    start_time: datetime
    end_time: Optional[datetime] = None
    notes: str = ""
    test_count: int = 0
    pass_count: int = 0
    fail_count: int = 0
    coverage: float = 0.0


@dataclass
class TDDCycle:
    """Represents a complete TDD cycle."""
    id: str
    spec_id: str
    state: TDDState = TDDState.IDLE
    phases: List[PhaseRecord] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()


class TDDEngine:
    """RED-GREEN-REFACTOR state machine for TDD workflow."""
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        TDDState.IDLE: [TDDState.RED],
        TDDState.RED: [TDDState.GREEN, TDDState.IDLE],
        TDDState.GREEN: [TDDState.REFACTOR, TDDState.IDLE],
        TDDState.REFACTOR: [TDDState.RED, TDDState.COMPLETE, TDDState.IDLE],
        TDDState.COMPLETE: [TDDState.IDLE]
    }
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.current_cycle: Optional[TDDCycle] = None
        self.cycle_history: List[TDDCycle] = []
        self._state = TDDState.IDLE
    
    @property
    def state(self) -> TDDState:
        """Get current TDD state."""
        return self._state
    
    def can_transition_to(self, new_state: TDDState) -> bool:
        """Check if transition to new_state is valid."""
        return new_state in self.VALID_TRANSITIONS.get(self._state, [])
    
    def transition_to(self, new_state: TDDState, notes: str = "") -> bool:
        """Transition to a new TDD state.
        
        Args:
            new_state: The target state
            notes: Optional notes about the transition
            
        Returns:
            True if transition was successful, False otherwise
        """
        if not self.can_transition_to(new_state):
            return False
        
        # Close current phase if exists
        if self.current_cycle and self.current_cycle.phases:
            current_phase = self.current_cycle.phases[-1]
            if current_phase.end_time is None:
                current_phase.end_time = datetime.now()
        
        # Create new phase record
        phase_record = PhaseRecord(
            phase=new_state,
            start_time=datetime.now(),
            notes=notes
        )
        
        if self.current_cycle:
            self.current_cycle.phases.append(phase_record)
            self.current_cycle.state = new_state
        
        self._state = new_state
        return True
    
    def start_cycle(self, spec_id: str) -> TDDCycle:
        """Start a new TDD cycle.
        
        Args:
            spec_id: Identifier for the specification
            
        Returns:
            The new TDDCycle instance
        """
        import uuid
        
        # Archive current cycle if exists
        if self.current_cycle:
            self.cycle_history.append(self.current_cycle)
        
        self.current_cycle = TDDCycle(
            id=str(uuid.uuid4())[:8],
            spec_id=spec_id,
            state=TDDState.IDLE
        )
        self._state = TDDState.IDLE
        return self.current_cycle
    
    def complete_cycle(self) -> Optional[TDDCycle]:
        """Complete the current TDD cycle.
        
        Returns:
            The completed cycle, or None if no cycle active
        """
        if not self.current_cycle:
            return None
        
        self.current_cycle.end_time = datetime.now()
        self.current_cycle.state = TDDState.COMPLETE
        self._state = TDDState.COMPLETE
        
        completed = self.current_cycle
        self.cycle_history.append(completed)
        self.current_cycle = None
        
        return completed
    
    def get_current_phase(self) -> Optional[PhaseRecord]:
        """Get the current phase record."""
        if not self.current_cycle or not self.current_cycle.phases:
            return None
        return self.current_cycle.phases[-1]
    
    def update_phase_results(self, test_results: Dict[str, Any]):
        """Update current phase with test results.
        
        Args:
            test_results: Dictionary with test results
        """
        phase = self.get_current_phase()
        if phase:
            phase.test_count = test_results.get('total', 0)
            phase.pass_count = test_results.get('passed', 0)
            phase.fail_count = test_results.get('failed', 0)
            phase.coverage = test_results.get('coverage', 0.0)


def red_phase(spec_path: str, output_dir: str = "tests") -> Dict[str, Any]:
    """Run RED phase - generate tests and expect failure.
    
    This function:
    1. Generates tests from SPEC.yaml
    2. Runs the tests
    3. Verifies they fail (RED state)
    
    Args:
        spec_path: Path to SPEC.yaml
        output_dir: Directory to output generated tests
        
    Returns:
        Dictionary with RED phase results
    """
    from .test_generator import generate_tests_from_spec
    from .test_runner import run_tests
    
    result = {
        "status": "RED",
        "phase": "red",
        "spec_path": spec_path,
        "tests_generated": [],
        "tests_run": False,
        "test_results": {},
        "message": ""
    }
    
    try:
        # Generate tests from spec
        gen_result = generate_tests_from_spec(spec_path, output_dir)
        result["tests_generated"] = gen_result.get("generated_files", [])
        
        if not result["tests_generated"]:
            result["status"] = "ERROR"
            result["message"] = "No tests generated from spec"
            return result
        
        # Run tests expecting failure
        test_results = run_tests(output_dir, coverage=False)
        result["tests_run"] = True
        result["test_results"] = test_results
        
        # Determine if we're truly in RED state
        if test_results.get("failed", 0) > 0 or test_results.get("passed", 0) == 0:
            result["status"] = "RED"
            result["message"] = f"RED phase confirmed: {test_results.get('failed', 0)} tests failing as expected"
        else:
            result["status"] = "GREEN"
            result["message"] = "WARNING: Tests already passing - may need to check test validity"
            
    except Exception as e:
        result["status"] = "ERROR"
        result["message"] = f"Error in RED phase: {str(e)}"
    
    return result


def green_phase(test_path: str, impl_path: str = None) -> Dict[str, Any]:
    """Run GREEN phase - verify tests pass.
    
    This function:
    1. Runs the tests
    2. Verifies they pass (GREEN state)
    3. Optionally checks coverage
    
    Args:
        test_path: Path to test files or directory
        impl_path: Optional path to implementation for coverage
        
    Returns:
        Dictionary with GREEN phase results
    """
    from .test_runner import run_tests
    
    result = {
        "status": "UNKNOWN",
        "phase": "green",
        "test_path": test_path,
        "tests_run": False,
        "test_results": {},
        "message": ""
    }
    
    try:
        # Run tests
        test_results = run_tests(test_path, coverage=True)
        result["tests_run"] = True
        result["test_results"] = test_results
        
        # Determine if we're in GREEN state
        if test_results.get("failed", 0) == 0 and test_results.get("passed", 0) > 0:
            result["status"] = "GREEN"
            result["message"] = f"GREEN phase achieved: {test_results.get('passed', 0)} tests passing"
        elif test_results.get("failed", 0) > 0:
            result["status"] = "RED"
            result["message"] = f"Still in RED: {test_results.get('failed', 0)} tests failing"
        else:
            result["status"] = "UNKNOWN"
            result["message"] = "No tests found or run"
            
    except Exception as e:
        result["status"] = "ERROR"
        result["message"] = f"Error in GREEN phase: {str(e)}"
    
    return result


def refactor_phase(impl_path: str, test_path: str, 
                   coverage_threshold: float = 80.0) -> Dict[str, Any]:
    """Run REFACTOR phase - improve code while keeping tests green.
    
    This function:
    1. Verifies tests are green
    2. Checks coverage meets threshold
    3. Provides refactoring suggestions
    
    Args:
        impl_path: Path to implementation code
        test_path: Path to test files
        coverage_threshold: Minimum coverage percentage required
        
    Returns:
        Dictionary with REFACTOR phase results
    """
    from .test_runner import run_tests
    from .coverage import check_coverage
    
    result = {
        "status": "UNKNOWN",
        "phase": "refactor",
        "impl_path": impl_path,
        "test_path": test_path,
        "tests_green": False,
        "coverage_met": False,
        "coverage_result": {},
        "suggestions": [],
        "message": ""
    }
    
    try:
        # First verify tests are green
        test_results = run_tests(test_path, coverage=True)
        
        if test_results.get("failed", 0) > 0:
            result["status"] = "RED"
            result["message"] = "Cannot refactor: tests are failing. Return to GREEN phase first."
            return result
        
        if test_results.get("passed", 0) == 0:
            result["status"] = "UNKNOWN"
            result["message"] = "No tests passing. Check test setup."
            return result
        
        result["tests_green"] = True
        
        # Check coverage
        coverage_result = check_coverage(impl_path, test_path, coverage_threshold)
        result["coverage_result"] = coverage_result
        result["coverage_met"] = coverage_result.get("meets_threshold", False)
        
        # Generate refactoring suggestions
        suggestions = []
        
        if not result["coverage_met"]:
            suggestions.append(f"Increase test coverage to {coverage_threshold}% (currently {coverage_result.get('coverage', 0):.1f}%)")
        
        # Check for common refactoring opportunities
        suggestions.extend(_analyze_code_for_refactoring(impl_path))
        
        result["suggestions"] = suggestions
        
        if result["coverage_met"] and not suggestions:
            result["status"] = "COMPLETE"
            result["message"] = "REFACTOR phase complete: code is clean and well-covered"
        else:
            result["status"] = "REFACTOR"
            result["message"] = f"REFACTOR phase: {len(suggestions)} suggestion(s) available"
            
    except Exception as e:
        result["status"] = "ERROR"
        result["message"] = f"Error in REFACTOR phase: {str(e)}"
    
    return result


def _analyze_code_for_refactoring(impl_path: str) -> List[str]:
    """Analyze code for refactoring opportunities.
    
    Args:
        impl_path: Path to implementation code
        
    Returns:
        List of refactoring suggestions
    """
    suggestions = []
    
    if not os.path.exists(impl_path):
        return suggestions
    
    # Simple static analysis for common issues
    files_to_check = []
    if os.path.isfile(impl_path):
        files_to_check = [impl_path]
    elif os.path.isdir(impl_path):
        for root, _, files in os.walk(impl_path):
            for file in files:
                if file.endswith('.py'):
                    files_to_check.append(os.path.join(root, file))
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Check for long functions (simplistic check)
                for i, line in enumerate(lines):
                    if line.strip().startswith('def '):
                        func_start = i
                        func_lines = 0
                        for j in range(i + 1, len(lines)):
                            if lines[j] and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                                break
                            func_lines += 1
                        if func_lines > 30:
                            suggestions.append(f"Consider breaking down long function in {file_path}:{func_start+1}")
                
                # Check for TODO comments
                if 'TODO' in content or 'FIXME' in content:
                    suggestions.append(f"Address TODO/FIXME comments in {file_path}")
                    
        except Exception:
            pass
    
    return suggestions
