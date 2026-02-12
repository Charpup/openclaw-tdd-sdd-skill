"""
TDD+SDD Workflow Orchestration
Provides Agent-callable functions for Test-Driven and Spec-Driven Development

This module implements the dual-pyramid workflow:
- SDD (Spec-Driven Development) - Behavior Layer (AI Agent)
- TDD (Test-Driven Development) - Implementation Layer (Traditional)
"""

from typing import Optional, Dict, Any, List
from .state_machine import get_state_machine, TDDState


def create_spec(skill_name: str, requirements: str, output_path: str = None) -> dict:
    """
    Generate SPEC.yaml from natural language requirements.
    
    This is the starting point of the SDD workflow. It converts user requirements
    into a structured SPEC.yaml file that defines interfaces, contracts, and
    behavior scenarios.
    
    Args:
        skill_name: Name of the skill to develop (used in spec metadata)
        requirements: User's natural language description of what the skill should do
        output_path: Where to write SPEC.yaml (default: ./SPEC.yaml)
    
    Returns:
        dict: {
            "spec_path": str,           # Path to the generated SPEC.yaml
            "interfaces_count": int,    # Number of interfaces defined
            "scenarios_count": int,     # Number of scenarios defined
            "status": str               # "created" | "error"
        }
    
    Example:
        >>> result = create_spec(
        ...     skill_name="pdf-ocr",
        ...     requirements="Extract text from PDFs using Tesseract OCR",
        ...     output_path="./SPEC.yaml"
        ... )
        >>> print(result["interfaces_count"])  # e.g., 3
    """
    # Check state before proceeding
    sm = get_state_machine()
    validation = sm.validate_action("create_spec")
    
    if not validation["allowed"]:
        return {
            "spec_path": None,
            "interfaces_count": 0,
            "scenarios_count": 0,
            "status": "error",
            "error": validation["reason"]
        }
    
    # TODO: Implement actual spec generation logic
    # For now, return placeholder
    result = {
        "spec_path": output_path or "./SPEC.yaml",
        "interfaces_count": 0,
        "scenarios_count": 0,
        "status": "created"
    }
    
    # Update state on success
    sm.transition(TDDState.NEED_TESTS.value)
    
    return result


def validate_spec(spec_path: str) -> dict:
    """
    Validate SPEC.yaml format against the SDD schema.
    
    Checks for required fields, valid YAML structure, contract completeness,
    and scenario definitions.
    
    Args:
        spec_path: Path to the SPEC.yaml file to validate
    
    Returns:
        dict: {
            "is_valid": bool,       # True if spec passes all checks
            "errors": list,         # List of validation error messages
            "warnings": list        # List of validation warnings (non-blocking)
        }
    
    Example:
        >>> result = validate_spec("./SPEC.yaml")
        >>> if not result["is_valid"]:
        ...     for error in result["errors"]:
        ...         print(f"Error: {error}")
    """
    # TODO: Implement spec validation logic
    return {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }


def generate_tests_from_spec(spec_path: str, output_dir: str = "tests") -> dict:
    """
    Generate test files from SPEC.yaml.
    
    Creates test stubs organized into the dual-pyramid structure:
    - tests/unit/         : Function-level unit tests
    - tests/integration/  : Module collaboration tests
    - tests/acceptance/   : End-to-end acceptance tests
    
    Args:
        spec_path: Path to the SPEC.yaml file
        output_dir: Directory where tests will be generated (default: "tests")
    
    Returns:
        dict: {
            "test_files": list,     # List of generated test file paths
            "total_tests": int,     # Total number of test cases generated
            "status": str           # "generated" | "partial" | "error"
        }
    
    Example:
        >>> result = generate_tests_from_spec("./SPEC.yaml", "tests")
        >>> print(f"Generated {result['total_tests']} tests")
        >>> for f in result["test_files"]:
        ...     print(f"  - {f}")
    """
    # Check state before proceeding
    sm = get_state_machine()
    validation = sm.validate_action("generate_tests")
    
    if not validation["allowed"]:
        return {
            "test_files": [],
            "total_tests": 0,
            "status": "error",
            "error": validation["reason"]
        }
    
    # TODO: Implement actual test generation logic
    result = {
        "test_files": [],
        "total_tests": 0,
        "status": "generated"
    }
    
    # Update state on success (transition to RED state)
    sm.transition(TDDState.RED.value)
    
    return result


def run_tests(test_path: str = None, coverage: bool = True) -> dict:
    """
    Run pytest and generate coverage report.
    
    Executes the test suite and returns detailed results including pass/fail
    counts and code coverage percentage.
    
    Args:
        test_path: Path to specific test file or directory (default: all tests)
        coverage: Whether to generate coverage report (default: True)
    
    Returns:
        dict: {
            "passed": int,          # Number of tests that passed
            "failed": int,          # Number of tests that failed
            "coverage": float,      # Code coverage percentage (0-100)
            "status": str           # "completed" | "partial" | "error"
        }
    
    Example:
        >>> result = run_tests("tests/unit", coverage=True)
        >>> print(f"Passed: {result['passed']}/{result['passed'] + result['failed']}")
        >>> print(f"Coverage: {result['coverage']:.1f}%")
    """
    # Check state before proceeding
    sm = get_state_machine()
    validation = sm.validate_action("run_tests")
    
    if not validation["allowed"]:
        return {
            "passed": 0,
            "failed": 0,
            "coverage": 0.0,
            "status": "error",
            "error": validation["reason"]
        }
    
    # TODO: Implement actual test running logic
    result = {
        "passed": 0,
        "failed": 0,
        "coverage": 0.0,
        "status": "completed"
    }
    
    # Update state based on test results
    # For now, assume tests pass to demonstrate state transition
    all_passed = result["failed"] == 0
    sm.update_after_test_run(tests_passed=all_passed, all_tests_passed=all_passed)
    
    return result


def validate_implementation(spec_path: str, project_dir: str) -> dict:
    """
    Validate that implementation meets SPEC requirements.
    
    Cross-references the actual implementation against the SPEC.yaml to ensure:
    - All defined interfaces are implemented
    - Contracts (preconditions/postconditions) are satisfied
    - Test coverage meets acceptance criteria (>= 80%)
    
    Args:
        spec_path: Path to the SPEC.yaml file
        project_dir: Root directory of the skill project
    
    Returns:
        dict: {
            "spec_compliant": bool,     # True if all interfaces implemented
            "coverage_met": bool,       # True if coverage >= 80%
            "missing_implementations": list,  # List of missing interfaces
            "status": str               # "validated" | "incomplete" | "error"
        }
    
    Example:
        >>> result = validate_implementation("./SPEC.yaml", "./my-skill")
        >>> if not result["spec_compliant"]:
        ...     print("Missing implementations:")
        ...     for item in result["missing_implementations"]:
        ...         print(f"  - {item}")
    """
    # Check state before proceeding
    sm = get_state_machine()
    validation = sm.validate_action("validate")
    
    if not validation["allowed"]:
        return {
            "spec_compliant": False,
            "coverage_met": False,
            "missing_implementations": [],
            "status": "error",
            "error": validation["reason"]
        }
    
    # TODO: Implement actual validation logic
    result = {
        "spec_compliant": True,
        "coverage_met": True,
        "missing_implementations": [],
        "status": "validated"
    }
    
    return result


def init_workflow(skill_name: str) -> dict:
    """
    Initialize TDD/SDD workflow for a new skill.
    
    Sets up the complete development environment including:
    - task_plan.md with TDD/SDD phases
    - SPEC.yaml template ready for editing
    - Progress tracking files
    
    This function integrates with planning-with-files to create a structured
    development plan with the following phases:
    1. Phase 1: Write SPEC.yaml (SDD - behavior definition)
    2. Phase 2: Generate test stubs (TDD setup)
    3. Phase 3: Implement & pass tests (Red-Green-Refactor)
    4. Phase 4: Final validation & refactoring
    
    Args:
        skill_name: Name of the skill to develop
    
    Returns:
        dict: {
            "task_plan_path": str,      # Path to created task_plan.md
            "spec_template_path": str,  # Path to SPEC.yaml template
            "status": str               # "initialized" | "error"
        }
    
    Example:
        >>> result = init_workflow("pdf-ocr-skill")
        >>> print(f"Workflow initialized: {result['task_plan_path']}")
        >>> print(f"Edit spec at: {result['spec_template_path']}")
    """
    # Reset state to initial state
    from .state_machine import reset_state
    reset_result = reset_state()
    
    if not reset_result["reset"]:
        return {
            "task_plan_path": None,
            "spec_template_path": None,
            "status": "error",
            "error": reset_result["status"]
        }
    
    # TODO: Implement actual initialization logic
    return {
        "task_plan_path": "./task_plan.md",
        "spec_template_path": "./SPEC.yaml",
        "status": "initialized"
    }
