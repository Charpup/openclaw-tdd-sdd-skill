#!/usr/bin/env python3
"""
Validate SPEC.yaml files
Usage: python validate_spec.py <path/to/SPEC.yaml>
"""
import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.sdd_validator import validate_spec


def main():
    parser = argparse.ArgumentParser(
        description="Validate SDD specification files"
    )
    parser.add_argument(
        "spec",
        help="Path to SPEC.yaml file"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"TDD+SDD Specification Validator")
    print(f"{'='*60}\n")
    
    print(f"Validating: {args.spec}\n")
    
    is_valid, errors, warnings = validate_spec(args.spec)
    
    # Display results
    if errors:
        print(f"❌ Errors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
        print()
    
    if warnings:
        print(f"⚠️  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    # Final status
    if is_valid and not (args.strict and warnings):
        print("✅ Specification is valid!")
        if warnings and not args.strict:
            print("   (Warnings present but not treated as errors)")
        return 0
    else:
        print("❌ Specification validation failed!")
        return 1


if __name__ == "__main__":
    exit(main())
