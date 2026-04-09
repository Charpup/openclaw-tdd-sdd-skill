#!/usr/bin/env python3
"""
Run TDD+SDD test suite with proper categorization
Usage: python run_tests.py [unit|integration|acceptance|all]
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run_tests(test_type: str = "all", verbose: bool = True, coverage: bool = False):
    """Run test suite"""
    
    # Base command
    cmd = ["pytest"]
    
    # Add test path
    if test_type == "all":
        cmd.append("tests/")
    else:
        cmd.append(f"tests/{test_type}/")
    
    # Add options
    if verbose:
        cmd.append("-v")
    
    cmd.extend(["--tb=short", "--strict-markers"])
    
    if coverage:
        cmd.extend(["--cov=lib", "--cov-report=term-missing"])
    
    # Color output
    cmd.append("--color=yes")
    
    print(f"\n{'='*60}")
    print(f"Running {test_type.upper()} Tests")
    print(f"{'='*60}\n")
    
    print(f"Command: {' '.join(cmd)}\n")
    
    # Run tests
    result = subprocess.run(cmd, cwd=Path.cwd())
    
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Run TDD+SDD test suite"
    )
    parser.add_argument(
        "type",
        nargs="?",
        default="all",
        choices=["unit", "integration", "acceptance", "all"],
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=True,
        help="Verbose output"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet output"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage report"
    )
    
    args = parser.parse_args()
    
    verbose = not args.quiet
    
    exit_code = run_tests(
        test_type=args.type,
        verbose=verbose,
        coverage=args.coverage
    )
    
    return exit_code


if __name__ == "__main__":
    exit(main())
