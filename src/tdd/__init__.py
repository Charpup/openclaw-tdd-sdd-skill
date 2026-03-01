"""TDD Module for OpenClaw TDD-SDD Skill.

This module provides the core TDD functionality including:
- RED-GREEN-REFACTOR state machine
- Test generation from SPEC.yaml
- Test execution and result parsing
- Coverage analysis
- Progress reporting
"""

from .engine import TDDEngine, TDDState, red_phase, green_phase, refactor_phase
from .test_generator import (
    generate_tests_from_spec,
    generate_unit_test,
    generate_acceptance_test,
    TestGenerator
)
from .test_runner import run_tests, parse_pytest_output, TestRunner
from .coverage import check_coverage, CoverageAnalyzer
from .reporter import TDDReporter, generate_cycle_report, generate_status_line

__version__ = "3.0.0"

__all__ = [
    # Engine
    "TDDEngine",
    "TDDState",
    "red_phase",
    "green_phase",
    "refactor_phase",
    # Test Generator
    "generate_tests_from_spec",
    "generate_unit_test",
    "generate_acceptance_test",
    "TestGenerator",
    # Test Runner
    "run_tests",
    "parse_pytest_output",
    "TestRunner",
    # Coverage
    "check_coverage",
    "CoverageAnalyzer",
    # Reporter
    "TDDReporter",
    "generate_cycle_report",
    "generate_status_line",
]
