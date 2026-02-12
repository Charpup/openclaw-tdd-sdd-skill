"""
Planning Integration Module for TDD+SDD Skill

Provides integration with planning-with-files workflow by managing
task_plan.md, progress.md, and findings.md files directly.

This module allows TDD+SDD workflow to:
1. Initialize planning files with TDD/SDD specific phases
2. Update phase completion status
3. Log test results and TDD phase transitions
4. Record technical decisions and findings
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


def _get_timestamp() -> str:
    """Get current timestamp in standard format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _read_file(filepath: Path) -> str:
    """Read file contents, return empty string if not exists."""
    if filepath.exists():
        return filepath.read_text(encoding='utf-8')
    return ""


def _write_file(filepath: Path, content: str) -> None:
    """Write content to file, creating parent directories if needed."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding='utf-8')


def _update_task_plan_phase(filepath: Path, phase_name: str, completed: bool = True) -> bool:
    """
    Update a phase status in task_plan.md.
    
    Looks for phase headers and updates checkbox status.
    Supports both phase sections and checklist items.
    """
    content = _read_file(filepath)
    if not content:
        return False
    
    # Pattern to match phase headers like "## Phase 1: Spec Definition (SDD)"
    # or checklist items like "- [ ] Write SPEC.yaml"
    lines = content.split('\n')
    updated = False
    
    for i, line in enumerate(lines):
        # Check if this line contains the phase name
        if phase_name in line:
            # Update checklist items: - [ ] -> - [x]
            if line.strip().startswith('- [ ]'):
                lines[i] = line.replace('- [ ]', '- [x]', 1)
                updated = True
            # Update phase status in header if marked with emoji
            elif '🔄' in line or '⏳' in line:
                lines[i] = line.replace('🔄', '✅').replace('⏳', '✅')
                updated = True
    
    if updated:
        _write_file(filepath, '\n'.join(lines))
    
    return updated


def _append_to_file(filepath: Path, content: str) -> None:
    """Append content to file, creating it if it doesn't exist."""
    existing = _read_file(filepath)
    if existing and not existing.endswith('\n'):
        existing += '\n'
    _write_file(filepath, existing + content)


def init_workflow(skill_name: str, project_dir: str = ".") -> dict:
    """
    Initialize TDD+SDD workflow planning files.
    
    Creates or updates task_plan.md with TDD/SDD specific phases,
    and initializes progress.md and findings.md with proper structure.
    
    Args:
        skill_name: Name of the skill being developed
        project_dir: Project root directory (default: current directory)
    
    Returns:
        dict: {
            "task_plan_path": str,
            "progress_path": str,
            "findings_path": str,
            "status": str
        }
    
    Example:
        >>> result = init_workflow("my-skill", "./my-skill")
        >>> print(result["task_plan_path"])
        './my-skill/task_plan.md'
    """
    project_path = Path(project_dir).resolve()
    task_plan_path = project_path / "task_plan.md"
    progress_path = project_path / "progress.md"
    findings_path = project_path / "findings.md"
    
    timestamp = _get_timestamp()
    
    # Create task_plan.md with TDD/SDD specific phases
    task_plan_content = f"""# Task Plan - {skill_name} (TDD+SDD Workflow)

**Skill**: {skill_name}
**Started**: {timestamp}
**Method**: TDD+SDD Dual Pyramid

---

## Phase 1: Spec Definition (SDD)
- [ ] Write SPEC.yaml
- [ ] Validate spec with `validate_spec()`

## Phase 2: Test Generation (TDD Setup)
- [ ] Generate test stubs with `generate_tests_from_spec()`
- [ ] Verify RED state (all tests fail)

## Phase 3: Implementation (Red-Green-Refactor)
- [ ] Implement code to pass tests (GREEN)
- [ ] Refactor while keeping tests green

## Phase 4: Final Validation
- [ ] Run full test suite
- [ ] Verify coverage >= 80%
- [ ] Validate spec compliance

---

## Progress Overview

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Spec Definition | ⏳ Pending | SDD - Behavior definition |
| Phase 2: Test Generation | ⏳ Pending | TDD Setup |
| Phase 3: Implementation | ⏳ Pending | Red-Green-Refactor |
| Phase 4: Final Validation | ⏳ Pending | Verification |

---

## Key Decisions

| Decision | Status |
|----------|--------|
| Architecture pattern | ⏳ TBD |
| Test framework | ⏳ TBD |
| Coverage threshold | ✅ 80% (default) |
"""
    
    # Create progress.md with initial structure
    progress_content = f"""# Progress Log - {skill_name}

## {timestamp} - Workflow Initialized

TDD+SDD workflow started for **{skill_name}**.

### Initial Setup
- [x] task_plan.md created
- [x] progress.md initialized
- [x] findings.md initialized

### Current Phase
⏳ Phase 1: Spec Definition (SDD)

---

## Test Results Log

| Time | Phase | Passed | Failed | Coverage | Status |
|------|-------|--------|--------|----------|--------|

---
"""
    
    # Create findings.md with initial structure
    findings_content = f"""# Findings & Decisions - {skill_name}

## Overview

This document records technical decisions, design rationale, and important
discoveries during the TDD+SDD development of **{skill_name}**.

---

## SDD Phase Findings

### Interface Design Decisions

*No decisions recorded yet.*

### Contract Definitions

*No contracts defined yet.*

---

## TDD Phase Findings

### Implementation Decisions

*No implementation decisions yet.*

### Refactoring Notes

*No refactoring performed yet.*

---

## Resources & References

*Add links to relevant documentation, APIs, etc.*

---

## Log

### {timestamp} - Workflow Started
- Initialized TDD+SDD workflow
- Created planning files

"""
    
    # Write all files
    _write_file(task_plan_path, task_plan_content)
    _write_file(progress_path, progress_content)
    _write_file(findings_path, findings_content)
    
    return {
        "task_plan_path": str(task_plan_path),
        "progress_path": str(progress_path),
        "findings_path": str(findings_path),
        "status": "initialized"
    }


def update_phase_complete(phase_name: str, project_dir: str = ".") -> dict:
    """
    Mark a phase as complete in task_plan.md and log to progress.md.
    
    Args:
        phase_name: Name of the phase to mark complete
                   (e.g., "Phase 1", "Spec Definition", "Write SPEC.yaml")
        project_dir: Project root directory (default: current directory)
    
    Returns:
        dict: {
            "updated": bool,
            "status": str
        }
    
    Example:
        >>> result = update_phase_complete("Phase 1")
        >>> print(result["updated"])  # True if phase was found and updated
    """
    project_path = Path(project_dir).resolve()
    task_plan_path = project_path / "task_plan.md"
    progress_path = project_path / "progress.md"
    
    timestamp = _get_timestamp()
    
    # Update task_plan.md
    task_updated = False
    if task_plan_path.exists():
        task_updated = _update_task_plan_phase(task_plan_path, phase_name)
        
        # Also try to update the phase name with common variations
        if not task_updated:
            # Try common phase name patterns
            variations = [
                phase_name,
                phase_name.replace("Phase ", "Phase"),
                phase_name.replace("Phase", "Phase "),
            ]
            for variant in variations:
                if _update_task_plan_phase(task_plan_path, variant):
                    task_updated = True
                    break
    
    # Log to progress.md
    progress_entry = f"""
## {timestamp} - Phase Completed: {phase_name}

✅ **{phase_name}** marked as complete.

### Next Steps
- Review task_plan.md for remaining items
- Proceed to next phase

---
"""
    _append_to_file(progress_path, progress_entry)
    
    return {
        "updated": task_updated,
        "status": "updated" if task_updated else "logged_only"
    }


def log_test_results(results: dict, project_dir: str = ".") -> dict:
    """
    Log test results to progress.md.
    
    Args:
        results: Dictionary containing test results with keys:
                - passed: int - Number of tests passed
                - failed: int - Number of tests failed
                - coverage: float - Code coverage percentage
                - tdd_phase: str - Current TDD phase ("RED"/"GREEN"/"REFACTOR")
                - (optional) details: str - Additional details
        project_dir: Project root directory (default: current directory)
    
    Returns:
        dict: {
            "logged": bool,
            "status": str
        }
    
    Example:
        >>> results = {
        ...     "passed": 12,
        ...     "failed": 3,
        ...     "coverage": 75.5,
        ...     "tdd_phase": "RED"
        ... }
        >>> log_test_results(results, "./my-project")
    """
    project_path = Path(project_dir).resolve()
    progress_path = project_path / "progress.md"
    
    timestamp = _get_timestamp()
    
    # Extract values with defaults
    passed = results.get("passed", 0)
    failed = results.get("failed", 0)
    coverage = results.get("coverage", 0.0)
    tdd_phase = results.get("tdd_phase", "UNKNOWN")
    details = results.get("details", "")
    
    # Determine status indicator
    total = passed + failed
    if failed == 0 and total > 0:
        test_status = "✅ PASS"
    elif failed > 0:
        test_status = "❌ FAIL"
    else:
        test_status = "⚠️ NO TESTS"
    
    # Phase indicator
    phase_emoji = {
        "RED": "🔴",
        "GREEN": "🟢",
        "REFACTOR": "♻️"
    }.get(tdd_phase.upper(), "⚪")
    
    # Create log entry
    log_entry = f"""
## {timestamp} - Test Run ({phase_emoji} {tdd_phase})

### Results
- **Passed**: {passed}
- **Failed**: {failed}
- **Coverage**: {coverage:.1f}%
- **Status**: {test_status}

"""
    
    if details:
        log_entry += f"""### Details
{details}

"""
    
    # Add to results table
    log_entry += f"""### Summary Table
| Time | Phase | Passed | Failed | Coverage | Status |
|------|-------|--------|--------|----------|--------|
| {timestamp} | {tdd_phase} | {passed} | {failed} | {coverage:.1f}% | {test_status} |

---
"""
    
    _append_to_file(progress_path, log_entry)
    
    return {
        "logged": True,
        "status": "logged"
    }


def log_finding(decision: str, rationale: str, project_dir: str = ".") -> dict:
    """
    Record a technical decision or finding to findings.md.
    
    Args:
        decision: Brief description of the decision made
        rationale: Explanation of why this decision was made
        project_dir: Project root directory (default: current directory)
    
    Returns:
        dict: {
            "logged": bool,
            "status": str
        }
    
    Example:
        >>> log_finding(
        ...     decision="Use stdio mode for MCP",
        ...     rationale="More stable than HTTP, no authentication needed",
        ...     project_dir="./my-project"
        ... )
    """
    project_path = Path(project_dir).resolve()
    findings_path = project_path / "findings.md"
    
    timestamp = _get_timestamp()
    
    # Create finding entry
    finding_entry = f"""
### {timestamp} - {decision}

**Decision**: {decision}

**Rationale**:
{rationale}

---
"""
    
    _append_to_file(findings_path, finding_entry)
    
    return {
        "logged": True,
        "status": "logged"
    }


# Convenience functions for specific use cases

def mark_spec_complete(project_dir: str = ".") -> dict:
    """Mark Phase 1 (Spec Definition) as complete."""
    return update_phase_complete("Phase 1: Spec Definition", project_dir)


def mark_tests_generated(project_dir: str = ".") -> dict:
    """Mark Phase 2 (Test Generation) as complete."""
    return update_phase_complete("Phase 2: Test Generation", project_dir)


def mark_implementation_complete(project_dir: str = ".") -> dict:
    """Mark Phase 3 (Implementation) as complete."""
    return update_phase_complete("Phase 3: Implementation", project_dir)


def mark_validation_complete(project_dir: str = ".") -> dict:
    """Mark Phase 4 (Final Validation) as complete."""
    return update_phase_complete("Phase 4: Final Validation", project_dir)


def log_red_phase(passed: int, failed: int, coverage: float, project_dir: str = ".") -> dict:
    """Log test results for RED phase (tests exist but fail)."""
    return log_test_results({
        "passed": passed,
        "failed": failed,
        "coverage": coverage,
        "tdd_phase": "RED"
    }, project_dir)


def log_green_phase(passed: int, failed: int, coverage: float, project_dir: str = ".") -> dict:
    """Log test results for GREEN phase (tests pass)."""
    return log_test_results({
        "passed": passed,
        "failed": failed,
        "coverage": coverage,
        "tdd_phase": "GREEN"
    }, project_dir)


def log_refactor_phase(passed: int, failed: int, coverage: float, project_dir: str = ".") -> dict:
    """Log test results for REFACTOR phase."""
    return log_test_results({
        "passed": passed,
        "failed": failed,
        "coverage": coverage,
        "tdd_phase": "REFACTOR"
    }, project_dir)
