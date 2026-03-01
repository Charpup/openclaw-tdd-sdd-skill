---
name: tdd-sdd-development
description: TDD+SDD dual-pyramid workflow with OpenSpec-inspired delta specs and brownfield support. Manages SPEC.yaml creation, test generation, Red-Green-Refactor cycles, and change tracking. Use when building production-ready skills requiring test coverage, maintainability, or working with existing codebases. Triggers on "TDD", "SDD", "test driven", "spec driven", "SPEC.yaml", "delta spec", "brownfield".
metadata:
  openclaw:
    emoji: "🧪"
    requires:
      bins: ["python3", "pytest"]
      env: []
    os: ["linux", "macos", "windows"]
    install:
      - id: "pip-tdd-deps"
        kind: "shell"
        command: "pip3 install pytest pytest-cov pytest-asyncio pytest-mock pyyaml click rich"
        label: "Install Python testing dependencies"
---

# TDD+SDD Development Workflow v3.0

**Version:** 3.0.0 | **Homepage:** https://github.com/Charpup/openclaw-tdd-sdd-skill

Develop OpenClaw skills using Test-Driven Development (TDD) and Spec-Driven Development (SDD) best practices. Now with **full TDD automation**: RED-GREEN-REFACTOR state machine, automated test generation, coverage tracking, and comprehensive reporting.

## What's New in v3.0

### 🆕 RED-GREEN-REFACTOR Engine
Full TDD cycle automation with state tracking:
```python
from tdd.engine import red_phase, green_phase, refactor_phase

# RED: Generate tests and expect failure
result = red_phase("SPEC.yaml")
# Output: 🔴 RED Phase - 4 tests failing as expected

# GREEN: Implement and verify tests pass
result = green_phase("tests/")
# Output: 🟢 GREEN Phase - 4 tests passing

# REFACTOR: Improve code quality
result = refactor_phase("src/", "tests/")
# Output: 🟡 REFACTOR Phase - 92% coverage, 2 suggestions
```

### 🆕 Automated Test Generation
Generate complete pytest tests from SPEC.yaml:
```python
from tdd.test_generator import generate_tests_from_spec

result = generate_tests_from_spec("SPEC.yaml", "tests/")
# Generates: test_calc_001.py, test_calc_002.py, test_acceptance.py
```

### 🆕 Coverage Analysis
Integrated coverage checking with threshold validation:
```python
from tdd.coverage import check_coverage

result = check_coverage("src/", threshold=80.0)
# Output: Coverage 85% - Meets threshold ✅
```

### 🆕 TDD Reporting
Beautiful progress reports and status tracking:
```python
from tdd.reporter import generate_cycle_report

report = generate_cycle_report(cycle_data)
# Generates formatted markdown report
```

## When to Use This Skill

**ALWAYS use for:**
- Creating a new OpenClaw skill from scratch
- Adding features to **existing** skills (brownfield)
- Refactoring with test coverage
- Any skill requiring long-term maintenance
- Following strict TDD workflow

**Use TDD Module when:**
- You want automated RED-GREEN-REFACTOR tracking
- You need test generation from specifications
- You require coverage threshold enforcement
- You want detailed TDD progress reports

**Use DELTA SPECS when:**
- Modifying existing functionality
- Deprecating old features
- Migrating from old patterns

**Use ARTIFACT FLOW when:**
- Complex features needing design docs
- Team collaboration
- Requirements exploration needed

**SKIP for:**
- Simple bug fixes (< 5 lines)
- Documentation-only changes
- Quick prototypes

## Core Workflows

### Workflow A: TDD Cycle (RED-GREEN-REFACTOR)
Traditional TDD with full automation:

```
SPEC.yaml → Generate Tests → RED → Implement → GREEN → REFACTOR → Archive
                ↑                                              ↓
                └──────────── Coverage Check ←─────────────────┘
```

### Workflow B: Brownfield (Existing Project)
Delta specs for existing codebases:

```
Detect Code → Generate Base Specs → Delta Specs → Tests → Implement → Archive
```

### Workflow C: Artifact Flow (Complex)
OpenSpec-inspired full workflow:

```
proposal.md → specs/ → design.md → tasks.md → Tests → RED → GREEN → Archive
```

## Quick Start

### TDD Cycle Example
```python
# Import TDD module
from tdd.engine import TDDEngine, red_phase, green_phase, refactor_phase
from tdd.test_generator import generate_tests_from_spec

# Initialize TDD engine
engine = TDDEngine(project_path=".")
engine.start_cycle("CALC-001")

# RED Phase: Generate tests and run (expecting failure)
red_result = red_phase("SPEC.yaml", output_dir="tests/")
print(red_result["message"])  # 🔴 RED Phase - 4 tests failing

# ... Implement minimal code to make tests pass ...

# GREEN Phase: Verify tests pass
green_result = green_phase("tests/")
print(green_result["message"])  # 🟢 GREEN Phase - 4 tests passing

# REFACTOR Phase: Improve code quality
refactor_result = refactor_phase("src/", "tests/", coverage_threshold=80.0)
print(refactor_result["message"])  # 🟡 REFACTOR Phase complete

# Complete cycle
engine.complete_cycle()
```

### Test Generation Example
```python
from tdd.test_generator import generate_tests_from_spec, generate_unit_test

# Generate all tests from SPEC.yaml
result = generate_tests_from_spec("SPEC.yaml", "tests/")
print(f"Generated {len(result['generated_files'])} test files")

# Or generate individual tests
requirement = {
    "id": "AUTH-001",
    "description": "User can login",
    "scenarios": [...]
}
test_code = generate_unit_test(requirement, module_name="auth")
```

### Test Runner Example
```python
from tdd.test_runner import run_tests, parse_pytest_output

# Run tests with coverage
results = run_tests("tests/", coverage=True)
print(f"Tests: {results['passed']}/{results['total']} passed")
print(f"Coverage: {results['coverage']:.1f}%")

# Check for failures
if results['failed'] > 0:
    for failure in results['failures']:
        print(f"❌ {failure['test']}: {failure['message']}")
```

### Coverage Checking Example
```python
from tdd.coverage import check_coverage, CoverageAnalyzer

# Simple coverage check
result = check_coverage("src/", threshold=80.0)
if result['meets_threshold']:
    print(f"✅ Coverage {result['coverage']:.1f}% meets threshold")
else:
    print(f"❌ Coverage {result['coverage']:.1f}% below threshold")

# Detailed analysis
analyzer = CoverageAnalyzer("src/")
report = analyzer.check(threshold=80.0)
for file in report.files:
    print(f"{file.path}: {file.percentage:.1f}%")
```

## SPEC.yaml Formats

### Format 1: Standard (v1.0 Compatible)
```yaml
specification:
  name: "My Skill"
  version: "1.0.0"
  
requirements:
  - id: AUTH-001
    description: "User can login"
    scenarios:
      - name: "valid login"
        given: "valid credentials"
        when: "user submits"
        then: "login succeeds"
```

### Format 2: With TDD Config (v3.0)
```yaml
specification:
  name: "My Skill"
  version: "1.0.0"
  
tdd_config:
  test_framework: pytest
  coverage_threshold: 80
  test_types: [unit, integration]
  
requirements:
  - id: AUTH-001
    description: "User can login"
    priority: high
    scenarios:
      - name: "valid login"
        given: "valid credentials"
        when: "user submits"
        then: "login succeeds"
```

### Format 3: Delta Specs
```yaml
specification:
  name: "My Skill"
  version: "2.0.0"
  
# Base specs (existing)
requirements:
  - id: AUTH-001
    description: "User can login with password"

# Changes
delta_specs:
  added:
    - id: AUTH-002
      description: "User can login with OAuth"
      scenarios:
        - name: "oauth login"
          given: "valid oauth token"
          when: "user authenticates"
          then: "login succeeds"
  
  modified:
    - id: AUTH-001
      description: "User can login with password or OAuth"
      previous: "User can login with password"
  
  removed:
    - id: AUTH-000
      reason: "Deprecated legacy login"
```

## TDD Module API Reference

### Engine Module (`tdd.engine`)

#### `TDDEngine(project_path: str)`
RED-GREEN-REFACTOR state machine.

**Methods:**
- `start_cycle(spec_id: str) -> TDDCycle` - Start new TDD cycle
- `transition_to(state: TDDState, notes: str) -> bool` - Transition state
- `can_transition_to(state: TDDState) -> bool` - Check valid transition
- `complete_cycle() -> TDDCycle` - Complete current cycle
- `get_current_phase() -> PhaseRecord` - Get current phase info

#### `red_phase(spec_path: str, output_dir: str) -> dict`
Run RED phase - generate tests and expect failure.

**Returns:**
```python
{
    "status": "RED",
    "tests_generated": ["tests/test_req_001.py", ...],
    "test_results": {"passed": 0, "failed": 4, ...},
    "message": "RED phase confirmed: 4 tests failing as expected"
}
```

#### `green_phase(test_path: str, impl_path: str) -> dict`
Run GREEN phase - verify tests pass.

**Returns:**
```python
{
    "status": "GREEN",
    "tests_green": True,
    "test_results": {"passed": 4, "failed": 0, ...},
    "message": "GREEN phase achieved: 4 tests passing"
}
```

#### `refactor_phase(impl_path: str, test_path: str, coverage_threshold: float) -> dict`
Run REFACTOR phase - improve code quality.

**Returns:**
```python
{
    "status": "REFACTOR",
    "tests_green": True,
    "coverage_met": True,
    "coverage_result": {"coverage": 85.0, "meets_threshold": True},
    "suggestions": ["Consider breaking down long function..."],
    "message": "REFACTOR phase: 1 suggestion(s) available"
}
```

### Test Generator Module (`tdd.test_generator`)

#### `generate_tests_from_spec(spec_path: str, output_dir: str) -> dict`
Generate pytest tests from SPEC.yaml.

**Returns:**
```python
{
    "status": "success",
    "generated_files": ["tests/test_req_001.py", ...],
    "requirements_count": 4,
    "scenarios_count": 8,
    "message": "Generated 5 test files"
}
```

#### `generate_unit_test(requirement: dict, module_name: str) -> str`
Generate single unit test from requirement.

#### `generate_acceptance_test(requirement: dict, scenario: dict, module_name: str) -> str`
Generate acceptance test from GIVEN-WHEN-THEN scenario.

### Test Runner Module (`tdd.test_runner`)

#### `run_tests(test_path: str, coverage: bool) -> dict`
Run pytest and return results.

**Returns:**
```python
{
    "status": "passed",
    "total": 10,
    "passed": 10,
    "failed": 0,
    "skipped": 0,
    "coverage": 85.5,
    "failures": [],
    "output": "..."
}
```

#### `parse_pytest_output(output: str) -> dict`
Parse pytest output for status and metrics.

### Coverage Module (`tdd.coverage`)

#### `check_coverage(source_path: str, threshold: float) -> dict`
Check if coverage meets threshold.

**Returns:**
```python
{
    "status": "pass",
    "coverage": 85.0,
    "threshold": 80.0,
    "meets_threshold": True,
    "files": [
        {"path": "src/module.py", "percentage": 90.0, ...}
    ]
}
```

#### `CoverageAnalyzer(source_path: str)`
Coverage analysis class with detailed reporting.

### Reporter Module (`tdd.reporter`)

#### `generate_cycle_report(cycle_data: dict) -> str`
Generate formatted TDD cycle report.

#### `generate_status_line(state: str, tests_passed: int, tests_total: int, coverage: float) -> str`
Generate single-line status summary.

**Example:**
```
🟢 GREEN    | Tests: 4/4 | Coverage: 85.0%
```

## Available Functions (Legacy API)

### Core Functions

#### `init_workflow(skill_name: str) -> dict`
Initialize standard TDD+SDD workflow.

#### `init_brownfield(project_dir: str) -> dict`
Initialize for existing codebase.

#### `init_artifact_flow(skill_name: str) -> dict`
Initialize with full artifact structure.

### Spec Functions

#### `create_spec(skill_name: str, requirements: str) -> dict`
Create SPEC.yaml from requirements.

#### `create_delta_spec(change_name: str, added: list, modified: list, removed: list) -> dict`
Create delta specs for brownfield changes.

#### `validate_spec(spec_path: str) -> dict`
Validate SPEC.yaml format.

### Artifact Functions

#### `create_proposal(intent: str, scope: dict) -> dict`
Create proposal.md with intent and scope.

#### `create_specs_from_proposal() -> dict`
Generate specs from proposal.

#### `create_design_doc() -> dict`
Create design.md with technical approach.

#### `create_task_list() -> dict`
Create tasks.md with implementation checklist.

### Test Functions (Legacy)

#### `generate_tests_from_spec(spec_path: str) -> dict`
Generate test files from spec.

#### `run_tests(test_path: str = None) -> dict`
Run tests, returns RED/GREEN status.

#### `check_coverage(threshold: float = 80.0) -> dict`
Check coverage meets threshold.

### Archive Functions

#### `archive_change(change_name: str = None) -> dict`
Complete change, merge deltas, move to archive.

#### `list_active_changes() -> list`
List all active (non-archived) changes.

#### `sync_specs_to_main() -> dict`
Merge delta specs into main specs without archiving.

## Project Structure

### Standard Structure
```
my-skill/
├── SPEC.yaml
├── src/
│   └── __init__.py
└── tests/
    ├── __init__.py
    ├── unit/
    ├── integration/
    └── acceptance/
```

### With TDD Module
```
my-skill/
├── SPEC.yaml              # Current specs (source of truth)
├── src/                   # Implementation code
│   ├── __init__.py
│   └── module.py
├── tests/                 # Generated and custom tests
│   ├── __init__.py
│   ├── test_req_001.py    # Auto-generated from SPEC
│   └── test_acceptance.py # Auto-generated scenarios
├── .tdd_reports/          # TDD cycle reports
│   └── tdd_report_20260301_120000.md
└── .coverage/             # Coverage data
```

### With Artifacts
```
my-skill/
├── SPEC.yaml              # Current specs (source of truth)
├── artifacts/             # Active change artifacts
│   ├── proposal.md
│   ├── design.md
│   └── tasks.md
├── changes/               # Change tracking
│   ├── add-feature-1/     # Active change
│   │   ├── proposal.md
│   │   ├── specs/
│   │   ├── design.md
│   │   └── tasks.md
│   └── archive/           # Completed changes
│       └── 2026-02-25-add-feature-1/
├── src/
└── tests/
```

## Integration with TriadDev

This skill is a core component of the **TriadDev Golden Triangle**:

```
📋 PLANNING → 📊 WORKFLOW → 🧪 TDD/SDD (this skill)
     ↓            ↓              ↓
task_plan.md   batches     SPEC.yaml + Tests
```

### TriadDev Integration Points

1. **Planning Phase:** Creates task_plan.md with TDD/SDD phases
2. **Workflow Phase:** task-workflow schedules spec→test→impl batches
3. **TDD Phase:** This skill executes Red-Green-Refactor cycles

### Example TriadDev Flow

```bash
# Initialize with TriadDev
triadev init "My Skill" --template lib
triadev plan --objectives "Design API,Write tests,Implement,Validate"

# TDD+SDD workflow starts
python -c "
from tdd.engine import TDDEngine, red_phase, green_phase
from tdd.test_generator import generate_tests_from_spec

# RED Phase
red_phase('SPEC.yaml', 'tests/')

# ... implement ...

# GREEN Phase
green_phase('tests/')
"

# TriadDev schedules implementation batches
triadev analyze
triadev implement --all

# Archive on completion
tdd_sdd.archive_change("feature-name")
triadev run --complete
```

## Critical Rules

### 1. Spec-First (Always)
Never write implementation before spec is complete.

### 2. RED Phase Validation
Always verify tests fail before implementing:
```python
result = red_phase("SPEC.yaml")
assert result["status"] == "RED"  # Tests should fail first
```

### 3. GREEN Phase Validation
Always verify tests pass after implementing:
```python
result = green_phase("tests/")
assert result["status"] == "GREEN"  # Tests should pass
```

### 4. Coverage Threshold
Minimum 80% coverage required:
```python
result = check_coverage("src/", threshold=80.0)
assert result["meets_threshold"]  # Must meet threshold
```

### 5. Delta Specs for Changes
Use delta_specs when modifying existing code:
```yaml
delta_specs:
  modified:
    - id: EXISTING-001
      description: "Updated behavior"
```

### 6. Archive on Completion
Always archive changes to maintain spec history:
```python
tdd_sdd.archive_change("feature-name")
```

### 7. Brownfield Detection
For existing projects, always start with:
```python
tdd_sdd.init_brownfield(project_dir=".")
```

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Skip specs and code directly | Always define spec first |
| Skip RED phase (tests must fail first) | Always run red_phase() before implementing |
| Ignore failing tests in GREEN | Fix all tests before REFACTOR |
| Modify code without delta specs | Use delta_specs for changes |
| Leave changes unarchived | Archive after completion |
| Skip brownfield detection | Use init_brownfield for existing code |
| Mix artifact and standard flow | Choose one approach per project |
| Ignore coverage warnings | Address coverage gaps in REFACTOR |

## Example Project

See `examples/tdd-demo/` for a complete working example:

```
examples/tdd-demo/
├── SPEC.yaml           # Calculator specification
├── src/
│   └── calculator.py   # Implementation
└── tests/
    └── test_calculator.py  # Generated + custom tests
```

Run the example:
```bash
cd examples/tdd-demo
python -m pytest tests/ -v --cov=src
```

## Migration from v2.x

v2.x SPEC.yaml files are **fully compatible** with v3.0. To use new TDD features:

1. Import the TDD module:
```python
from tdd.engine import red_phase, green_phase, refactor_phase
from tdd.test_generator import generate_tests_from_spec
from tdd.test_runner import run_tests
from tdd.coverage import check_coverage
```

2. Use the new TDD workflow:
```python
# Old way (still works)
tdd_sdd.generate_tests_from_spec("SPEC.yaml")

# New way with full TDD
def run_tdd_cycle(spec_path):
    # RED
    red_result = red_phase(spec_path)
    if red_result["status"] != "RED":
        raise Exception("Expected RED phase")
    
    # ... implement ...
    
    # GREEN
    green_result = green_phase("tests/")
    if green_result["status"] != "GREEN":
        raise Exception("Expected GREEN phase")
    
    # REFACTOR
    refactor_result = refactor_phase("src/", "tests/")
    return refactor_result
```

No breaking changes - all v2.x workflows continue to work.

## References

| Resource | Purpose |
|----------|---------|
| OpenSpec | https://github.com/Fission-AI/OpenSpec - Inspiration for delta specs |
| TriadDev | Golden Triangle workflow integration |
| Examples | `examples/` directory for sample projects |
| pytest | https://docs.pytest.org/ - Testing framework |
| pytest-cov | https://pytest-cov.readthedocs.io/ - Coverage plugin |

## TDD Module Structure

```
tdd-sdd-skill/
├── src/
│   └── tdd/
│       ├── __init__.py          # Module exports
│       ├── engine.py            # RED-GREEN-REFACTOR state machine
│       ├── test_generator.py    # Test generation from SPEC.yaml
│       ├── test_runner.py       # pytest execution
│       ├── coverage.py          # Coverage analysis
│       └── reporter.py          # Progress reports
├── examples/
│   └── tdd-demo/                # Working example
└── SKILL.md                     # This documentation
```

---

**Start building with TDD+SDD v3.0 today!** 🚀
