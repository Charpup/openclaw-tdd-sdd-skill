#!/usr/bin/env python3
"""
Check test coverage against threshold.
Usage: python check_coverage.py [--threshold 80] [--source src/]

Outputs JSON result to stdout for machine consumption.
"""
import argparse
import subprocess
import sys
import json
import re


def check_coverage(source_path: str = "src/", threshold: float = 80.0) -> dict:
    """Run pytest with coverage and check against threshold."""
    cmd = [
        "pytest", "tests/",
        f"--cov={source_path}",
        "--cov-report=term-missing",
        "--tb=short",
        "-q"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Parse total coverage from output
    coverage_pct = 0.0
    for line in result.stdout.split('\n'):
        # Match "TOTAL ... XX%" pattern
        match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', line)
        if match:
            coverage_pct = float(match.group(1))
            break

    meets_threshold = coverage_pct >= threshold

    return {
        "status": "pass" if meets_threshold else "fail",
        "coverage": coverage_pct,
        "threshold": threshold,
        "meets_threshold": meets_threshold,
        "test_output": result.stdout[-500:] if result.stdout else "",
        "test_returncode": result.returncode
    }


def main():
    parser = argparse.ArgumentParser(description="Check test coverage")
    parser.add_argument("--threshold", type=float, default=80.0, help="Coverage threshold (default: 80%%)")
    parser.add_argument("--source", default="src/", help="Source directory (default: src/)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = check_coverage(args.source, args.threshold)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        icon = "+" if result["meets_threshold"] else "X"
        print(f"[{icon}] Coverage: {result['coverage']:.1f}% (threshold: {result['threshold']:.1f}%)")
        if not result["meets_threshold"]:
            print(f"    BELOW THRESHOLD - need {result['threshold'] - result['coverage']:.1f}% more")

    return 0 if result["meets_threshold"] else 1


if __name__ == "__main__":
    sys.exit(main())
