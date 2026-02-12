---
name: tdd-sdd-development
version: "1.1.0"
description: Implements TDD+SDD dual-pyramid workflow for OpenClaw skill development. Manages SPEC.yaml creation, test generation, and Red-Green-Refactor cycles. Use when building production-ready skills that require test coverage and maintainability.
homepage: https://github.com/Charpup/openclaw-tdd-sdd-skill
user-invocable: true
metadata:
  openclaw:
    os: ["darwin", "linux", "win32"]
    requires:
      skills:
        - planning-with-files >= 2.10.0
    extends:
      - planning-with-files
---

# TDD+SDD Development Workflow

Develop OpenClaw skills using Test-Driven Development (TDD) and Spec-Driven Development (SDD) best practices. This skill provides a structured workflow that enforces test coverage, interface contracts, and behavior-driven scenarios.

## When to Use This Skill

**ALWAYS use for:**
- Creating a new OpenClaw skill from scratch
- Adding a new feature to an existing skill
- Refactoring skill implementation with test coverage
- Any skill that will be shared or maintained long-term

**SKIP for:**
- Simple bug fixes (< 5 lines of code)
- Documentation-only changes
- Quick prototypes or proof-of-concepts
- One-time scripts

## Core Workflow

The TDD+SDD workflow follows a **dual-pyramid model**:

```
SDD Pyramid (Behavior Layer - AI Agent)
  └── End-to-End Acceptance Tests
  └── Module Collaboration Tests
  └── Tool Function Contracts

TDD Pyramid (Implementation Layer - Traditional)
  └── Interface Contract Tests
  └── Module Integration Tests
  └── Function-Level Unit Tests
```

### Phase 1: Spec Definition (SDD)

Define behavior through SPEC.yaml before writing any code.

1. **Call `create_spec(skill_name, requirements)`**
   - Generates SPEC.yaml from user requirements
   - Defines interfaces, contracts, preconditions, and postconditions
   - Creates BDD-style scenarios (Given-When-Then)
   - Returns: `{"spec_path": "...", "interfaces_count": N, "scenarios_count": N}`

2. **Call `validate_spec(spec_path)`**
   - Validates SPEC.yaml against SDD schema
   - Checks for missing contracts or scenarios
   - Returns: `{"is_valid": true/false, "errors": [...], "warnings": [...]}`

**Output:** Complete SPEC.yaml ready for test generation

### Phase 2: Test Generation (TDD Setup)

Generate test stubs from the specification.

3. **Call `generate_tests_from_spec(spec_path, output_dir)`**
   - Creates test files organized by pyramid level:
     - `tests/unit/` - Function-level unit tests
     - `tests/integration/` - Module collaboration tests
     - `tests/acceptance/` - End-to-end BDD scenarios
   - Generates fixtures and mocks based on contracts
   - Returns: `{"test_files": [...], "total_tests": N, "status": "generated"}`

**Output:** Complete test suite ready for Red-Green-Refactor cycle

### Phase 3: Implementation (Red-Green-Refactor)

Iterative development following TDD principles.

4. **For each test file, repeat the cycle:**
   
   **RED Phase:**
   - Call `run_tests(test_path)`
   - Tests should FAIL (expected, as no implementation yet)
   - Record failures in progress tracking
   
   **GREEN Phase:**
   - Write minimal implementation to pass tests
   - Call `run_tests(test_path)` again
   - Tests should PASS
   - Update progress tracking
   
   **REFACTOR Phase:**
   - Improve code quality while keeping tests green
   - Call `suggest_refactoring(project_dir)` for recommendations
   - Run tests to verify no regressions

5. **Call `check_coverage(project_dir)`**
   - Runs full test suite with coverage analysis
   - Returns: `{"coverage": 85.5, "status": "acceptable"}`
   - Acceptance threshold: >= 80% coverage

### Phase 4: Final Validation

Ensure implementation meets all specifications.

6. **Call `validate_implementation(spec_path, project_dir)`**
   - Verifies all SPEC.yaml requirements are implemented
   - Checks test coverage meets threshold
   - Validates no missing interfaces or scenarios
   - Returns: `{"passed": true/false, "failures": [...], "coverage_met": true/false}`

7. **Call `finalize_workflow()`**
   - Updates planning files with final status
   - Generates summary report
   - Archives development artifacts

## Integration with planning-with-files

This skill **requires** and **extends** `planning-with-files`. It automatically integrates with the planning system:

### Automatic Planning Integration

When you start a TDD+SDD workflow, this skill automatically:

1. **Creates specialized phases in `task_plan.md`:**
   - Phase 1: Spec Definition (SDD) - Write SPEC.yaml
   - Phase 2: Test Generation (TDD Setup) - Generate test stubs
   - Phase 3: Implementation (Red-Green-Refactor) - Write code iteratively
   - Phase 4: Final Validation - Verify coverage and compliance

2. **Updates `progress.md` after each step:**
   - Test execution results with pass/fail counts
   - Coverage percentage tracking
   - Errors encountered and resolutions
   - Current TDD state (RED/GREEN/REFACTOR)

3. **Records decisions in `findings.md`:**
   - Interface design rationale
   - Contract definition reasoning
   - Trade-offs in implementation
   - Performance considerations

### Dependency Declaration

```yaml
# This skill requires planning-with-files
metadata:
  openclaw:
    requires:
      skills:
        - planning-with-files >= 2.10.0
    extends:
      - planning-with-files
```

### Example Integration Flow

```
User: "Create a PDF OCR extraction skill"

Agent workflow:
1. planning-with-files.init_planning()
   → Creates task_plan.md with generic phases

2. tdd_sdd.init_workflow(skill_name="pdf-ocr")
   → Enhances task_plan.md with TDD/SDD phases
   → Creates SPEC.yaml template
   → Updates progress.md: "Workflow initialized"

3. tdd_sdd.create_spec(requirements="...")
   → Writes SPEC.yaml
   → Updates task_plan.md: Phase 1 complete
   → Logs to findings.md: "Defined 3 interfaces"

4. tdd_sdd.generate_tests()
   → Creates tests/ directory structure
   → Updates progress.md: "Generated 12 test cases"
   → Updates task_plan.md: Phase 2 complete

5. tdd_sdd.run_tests()
   → Executes pytest (expect RED phase)
   → Updates progress.md with results

6. [Agent writes implementation code]

7. tdd_sdd.run_tests()
   → Executes pytest (expect GREEN phase)
   → Updates progress.md: "All tests passing"

8. tdd_sdd.validate_final()
   → Final compliance check
   → Updates task_plan.md: All phases complete
   → Writes summary to findings.md
```

## Available Functions

### Spec Definition (SDD)

#### `create_spec(skill_name: str, requirements: str, output_path: str = None) -> dict`
Generate SPEC.yaml from natural language requirements.

**Parameters:**
- `skill_name`: Name of the skill to develop
- `requirements`: User's description of skill functionality
- `output_path`: Where to write SPEC.yaml (default: `./SPEC.yaml`)

**Returns:**
```json
{
  "spec_path": "./SPEC.yaml",
  "interfaces_count": 3,
  "scenarios_count": 5,
  "status": "created"
}
```

#### `validate_spec(spec_path: str) -> dict`
Validate SPEC.yaml against SDD schema.

**Parameters:**
- `spec_path`: Path to SPEC.yaml file

**Returns:**
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": ["Missing performance criteria"]
}
```

### Test Generation (TDD)

#### `generate_tests_from_spec(spec_path: str, output_dir: str = "tests") -> dict`
Generate test files from SPEC.yaml.

**Parameters:**
- `spec_path`: Path to validated SPEC.yaml
- `output_dir`: Directory for test files (default: `tests/`)

**Returns:**
```json
{
  "test_files": [
    "tests/unit/test_service.py",
    "tests/integration/test_collaboration.py",
    "tests/acceptance/test_scenarios.py"
  ],
  "total_tests": 15,
  "status": "generated"
}
```

#### `run_tests(test_path: str = None, coverage: bool = True) -> dict`
Run pytest with optional coverage reporting.

**Parameters:**
- `test_path`: Specific test file to run (default: all tests)
- `coverage`: Enable coverage analysis (default: true)

**Returns:**
```json
{
  "passed": 12,
  "failed": 3,
  "coverage": 75.5,
  "status": "completed",
  "tdd_phase": "RED"
}
```

#### `check_coverage(project_dir: str, threshold: float = 80.0) -> dict`
Check if test coverage meets threshold.

**Parameters:**
- `project_dir`: Project root directory
- `threshold`: Minimum acceptable coverage percentage (default: 80.0)

**Returns:**
```json
{
  "coverage": 85.5,
  "threshold": 80.0,
  "met": true,
  "status": "acceptable"
}
```

### Validation & Workflow

#### `validate_implementation(spec_path: str, project_dir: str) -> dict`
Validate that implementation meets SPEC requirements.

**Parameters:**
- `spec_path`: Path to SPEC.yaml
- `project_dir`: Project root with implementation

**Returns:**
```json
{
  "spec_compliant": true,
  "coverage_met": true,
  "missing_implementations": [],
  "status": "validated"
}
```

#### `init_workflow(skill_name: str) -> dict`
Initialize TDD+SDD workflow with planning integration.

**Parameters:**
- `skill_name`: Name of the skill being developed

**Returns:**
```json
{
  "task_plan_updated": true,
  "spec_template_created": true,
  "progress_initialized": true,
  "status": "initialized"
}
```

#### `suggest_refactoring(project_dir: str) -> list`
Analyze code and suggest refactorings.

**Parameters:**
- `project_dir`: Project root directory

**Returns:**
```json
[
  {
    "file": "lib/service.py",
    "line": 42,
    "issue": "Function too long (50 lines)",
    "suggestion": "Extract into smaller methods"
  }
]
```

#### `finalize_workflow() -> dict`
Complete workflow and generate final report.

**Returns:**
```json
{
  "all_phases_complete": true,
  "final_coverage": 87.2,
  "spec_compliance": "100%",
  "status": "completed"
}
```

## Critical Rules

### 1. Spec-First Development
Never write implementation code before SPEC.yaml is complete and validated.

### 2. Test-First Implementation
Never write implementation before tests exist. The workflow enforces:
- RED phase: Tests exist but fail
- GREEN phase: Implementation makes tests pass
- REFACTOR phase: Improve quality while tests pass

### 3. Coverage Threshold
Minimum 80% code coverage required for workflow completion.

### 4. Planning Integration
Always update planning files after each phase:
- `task_plan.md` - Phase completion status
- `progress.md` - Test results and coverage
- `findings.md` - Design decisions and trade-offs

### 5. State Tracking
The workflow maintains internal state:
- Current phase (SPEC/TEST/IMPL/VALIDATE)
- TDD state (RED/GREEN/REFACTOR)
- Coverage status
- Validation results

## Templates and References

| Resource | Location | Purpose |
|----------|----------|---------|
| SPEC Template | `templates/sdd_spec_template.yaml` | Starting point for new specs |
| Test Templates | `templates/test_*.py` | Test file templates |
| Example Project | `examples/pdf-ocr-skill/` | Complete working example |
| API Documentation | `references/api.md` | Detailed function reference |

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Skip SPEC.yaml and start coding | Always define spec first |
| Write all tests at once | Iterate through Red-Green-Refactor |
| Ignore failing tests in RED phase | Document expected failures in progress.md |
| Skip refactoring phase | Allocate time for code quality improvements |
| Work without planning files | Let the skill create and update them |
| Accept <80% coverage | Add tests until threshold is met |

## Quick Start

```bash
# Initialize workflow for a new skill
tdd_sdd.init_workflow(skill_name="my-skill")

# Create specification
tdd_sdd.create_spec(
    skill_name="my-skill",
    requirements="Extract text from PDFs using OCR"
)

# Validate spec
tdd_sdd.validate_spec(spec_path="./SPEC.yaml")

# Generate tests
tdd_sdd.generate_tests_from_spec(spec_path="./SPEC.yaml")

# Run tests (RED phase)
tdd_sdd.run_tests()

# [Write implementation code]

# Run tests (GREEN phase)
tdd_sdd.run_tests()

# Validate final implementation
tdd_sdd.validate_implementation(
    spec_path="./SPEC.yaml",
    project_dir="."
)
```