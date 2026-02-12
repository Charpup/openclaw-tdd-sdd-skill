"""
TDD/SDD Workflow State Machine
Enforces proper workflow sequence to prevent skipping steps
"""

import os
import json
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime


class TDDState(Enum):
    """TDD/SDD workflow states"""
    NEED_SPEC = "need_spec"          # Need to create SPEC first
    NEED_TESTS = "need_tests"        # Need to generate tests
    RED = "red"                      # Tests generated but failing (expected)
    GREEN = "green"                  # Tests passing
    REFACTOR = "refactor"            # Currently refactoring
    VALIDATED = "validated"          # Final validation complete


class StateMachine:
    """
    State machine for TDD/SDD workflow enforcement.
    
    Ensures workflow steps are executed in correct order:
    NEED_SPEC -> NEED_TESTS -> RED -> GREEN -> (REFACTOR -> GREEN)* -> VALIDATED
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        TDDState.NEED_SPEC: [TDDState.NEED_TESTS],
        TDDState.NEED_TESTS: [TDDState.RED],
        TDDState.RED: [TDDState.GREEN],
        TDDState.GREEN: [TDDState.REFACTOR, TDDState.VALIDATED],
        TDDState.REFACTOR: [TDDState.GREEN],
        TDDState.VALIDATED: []  # Terminal state
    }
    
    # Action to required state mapping
    ACTION_REQUIREMENTS = {
        "create_spec": TDDState.NEED_SPEC,
        "generate_tests": TDDState.NEED_TESTS,
        "run_tests": None,  # Can run in RED, GREEN, or REFACTOR
        "write_code": None,  # Can write code in RED or REFACTOR
        "refactor": TDDState.GREEN,
        "validate": TDDState.GREEN
    }
    
    # Action to state transition mapping (action -> new state if successful)
    ACTION_TRANSITIONS = {
        "create_spec": TDDState.NEED_TESTS,
        "generate_tests": TDDState.RED,
    }
    
    def __init__(self, project_dir: str = "."):
        """
        Initialize state machine.
        
        Args:
            project_dir: Project directory where state file will be stored
        """
        self.state_file = os.path.join(project_dir, ".tdd-sdd-state.json")
        self.current_state = self._load_state()
    
    def _load_state(self) -> TDDState:
        """
        Load state from .tdd-sdd-state.json file.
        
        Returns:
            TDDState: Current state from file, or NEED_SPEC if file doesn't exist
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    state_str = data.get("state", TDDState.NEED_SPEC.value)
                    return TDDState(state_str)
            except (json.JSONDecodeError, ValueError) as e:
                # If file is corrupted, reset to initial state
                return TDDState.NEED_SPEC
        return TDDState.NEED_SPEC
    
    def _save_state(self):
        """Save current state to .tdd-sdd-state.json file."""
        data = {
            "state": self.current_state.value,
            "last_updated": datetime.now().isoformat()
        }
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.state_file) or ".", exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_state(self) -> str:
        """
        Get current state as string.
        
        Returns:
            str: Current state value
        """
        return self.current_state.value
    
    def get_state_enum(self) -> TDDState:
        """
        Get current state as TDDState enum.
        
        Returns:
            TDDState: Current state enum
        """
        return self.current_state
    
    def can_transition(self, new_state: str) -> bool:
        """
        Check if transition to new_state is valid.
        
        Valid transitions:
        - NEED_SPEC -> NEED_TESTS (spec created)
        - NEED_TESTS -> RED (tests generated)
        - RED -> GREEN (tests pass)
        - GREEN -> REFACTOR (start refactoring)
        - REFACTOR -> GREEN (refactoring complete, tests still pass)
        - GREEN -> VALIDATED (final validation passed)
        
        Args:
            new_state: Target state to transition to
            
        Returns:
            bool: True if transition is valid, False otherwise
        """
        try:
            target_state = TDDState(new_state)
        except ValueError:
            return False
        
        return target_state in self.VALID_TRANSITIONS.get(self.current_state, [])
    
    def transition(self, new_state: str, force: bool = False) -> Dict[str, Any]:
        """
        Attempt to transition to a new state.
        
        Args:
            new_state: Target state to transition to
            force: If True, bypass validation and force transition
            
        Returns:
            dict: {
                "success": bool,        # Whether transition succeeded
                "previous_state": str,  # State before transition
                "new_state": str,       # Current state after transition
                "error": str            # Error message if failed
            }
        """
        previous_state = self.current_state.value
        
        try:
            target_state = TDDState(new_state)
        except ValueError:
            return {
                "success": False,
                "previous_state": previous_state,
                "new_state": previous_state,
                "error": f"Invalid state: {new_state}. Valid states: {[s.value for s in TDDState]}"
            }
        
        # Check if transition is valid
        if not force and not self.can_transition(new_state):
            valid_next = [s.value for s in self.VALID_TRANSITIONS.get(self.current_state, [])]
            return {
                "success": False,
                "previous_state": previous_state,
                "new_state": previous_state,
                "error": (
                    f"Invalid state transition from '{previous_state}' to '{new_state}'. "
                    f"Valid next states: {valid_next if valid_next else 'none (terminal state)'}. "
                    f"Use force=True to bypass this check."
                )
            }
        
        # Perform transition
        self.current_state = target_state
        self._save_state()
        
        return {
            "success": True,
            "previous_state": previous_state,
            "new_state": self.current_state.value,
            "error": ""
        }
    
    def validate_action(self, action: str) -> Dict[str, Any]:
        """
        Validate if an action can be performed in current state.
        
        Args:
            action: Action to validate. One of:
                - "create_spec": Create SPEC.yaml
                - "generate_tests": Generate tests from spec
                - "run_tests": Run test suite
                - "write_code": Write implementation code
                - "refactor": Perform refactoring
                - "validate": Final validation
                
        Returns:
            dict: {
                "allowed": bool,    # Whether action is allowed
                "reason": str       # Explanation if not allowed
            }
        """
        required_state = self.ACTION_REQUIREMENTS.get(action)
        
        # Actions with no state requirement are always allowed
        if required_state is None:
            # But some actions have restrictions
            if action == "run_tests":
                if self.current_state in [TDDState.NEED_SPEC, TDDState.NEED_TESTS]:
                    return {
                        "allowed": False,
                        "reason": (
                            f"Cannot run tests in '{self.current_state.value}' state. "
                            f"Tests must be generated first (state: need_tests -> red)."
                        )
                    }
                return {"allowed": True, "reason": ""}
            
            if action == "write_code":
                if self.current_state == TDDState.NEED_SPEC:
                    return {
                        "allowed": False,
                        "reason": (
                            f"Cannot write code in '{self.current_state.value}' state. "
                            f"SPEC must be created first (state: need_spec)."
                        )
                    }
                if self.current_state == TDDState.NEED_TESTS:
                    return {
                        "allowed": False,
                        "reason": (
                            f"Cannot write code in '{self.current_state.value}' state. "
                            f"Tests must be generated first (state: need_tests -> red). "
                            f"Follow TDD: write tests before implementation."
                        )
                    }
                return {"allowed": True, "reason": ""}
            
            return {"allowed": True, "reason": ""}
        
        # Check if current state matches required state
        if self.current_state != required_state:
            return {
                "allowed": False,
                "reason": (
                    f"Action '{action}' requires state '{required_state.value}' "
                    f"but current state is '{self.current_state.value}'. "
                    f"Please complete previous steps first."
                )
            }
        
        return {"allowed": True, "reason": ""}
    
    def update_after_test_run(self, tests_passed: bool, all_tests_passed: bool = None) -> Dict[str, Any]:
        """
        Update state based on test run results.
        
        This is a helper method to transition state after running tests.
        - RED -> GREEN: When tests go from failing to passing
        - GREEN -> RED: When tests start failing again (regression)
        - REFACTOR -> GREEN: When refactoring is complete (tests pass)
        - REFACTOR -> RED: When refactoring broke tests (needs fix)
        
        Args:
            tests_passed: Whether the specific test(s) just run passed
            all_tests_passed: Whether ALL tests in the suite pass (default: same as tests_passed)
            
        Returns:
            dict: Transition result (same format as transition())
        """
        if all_tests_passed is None:
            all_tests_passed = tests_passed
            
        if self.current_state == TDDState.RED and all_tests_passed:
            # Tests were failing, now they pass -> GREEN
            return self.transition(TDDState.GREEN.value)
        
        elif self.current_state == TDDState.GREEN and not all_tests_passed:
            # Tests were passing, now failing -> back to RED
            return self.transition(TDDState.RED.value)
        
        elif self.current_state == TDDState.REFACTOR:
            if all_tests_passed:
                # Refactoring complete, tests pass -> GREEN
                return self.transition(TDDState.GREEN.value)
            else:
                # Refactoring broke tests -> stay in REFACTOR (or go to RED)
                # Actually we stay in REFACTOR until fixed
                return {
                    "success": True,
                    "previous_state": TDDState.REFACTOR.value,
                    "new_state": TDDState.REFACTOR.value,
                    "error": "Tests failed during refactoring. Fix before completing refactor."
                }
        
        # No state change needed
        return {
            "success": True,
            "previous_state": self.current_state.value,
            "new_state": self.current_state.value,
            "error": ""
        }


def get_state_machine(project_dir: str = ".") -> StateMachine:
    """
    Factory function to get a StateMachine instance.
    
    Args:
        project_dir: Project directory where state file is stored
        
    Returns:
        StateMachine: Configured state machine instance
    """
    return StateMachine(project_dir)


def reset_state(project_dir: str = ".") -> Dict[str, Any]:
    """
    Reset state to NEED_SPEC.
    
    Args:
        project_dir: Project directory where state file is stored
        
    Returns:
        dict: {
            "reset": bool,      # Whether reset was successful
            "status": str       # Status message
        }
    """
    state_file = os.path.join(project_dir, ".tdd-sdd-state.json")
    
    try:
        # Remove existing state file if present
        if os.path.exists(state_file):
            os.remove(state_file)
        
        # Create new state machine (will initialize to NEED_SPEC)
        sm = StateMachine(project_dir)
        
        return {
            "reset": True,
            "status": f"State reset to '{TDDState.NEED_SPEC.value}'. Ready to start new workflow."
        }
    except Exception as e:
        return {
            "reset": False,
            "status": f"Failed to reset state: {str(e)}"
        }
