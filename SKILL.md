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

# TDD+SDD Development Workflow v2.0

**Version:** 2.0.0 | **Homepage:** https://github.com/Charpup/openclaw-tdd-sdd-skill

Develop OpenClaw skills using Test-Driven Development (TDD) and Spec-Driven Development (SDD) best practices. Now with **OpenSpec-inspired** features: delta specs for brownfield development, artifact-based workflow, and change tracking.

## What's New in v2.0

### 🆕 Delta Specs (OpenSpec-Inspired)
Describe changes to existing systems:
```yaml
delta_specs:
  added:
    - requirement_id: NEW-001
      description: "New authentication method"
  modified:
    - requirement_id: AUTH-001  
      description: "Updated from 30min to 15min timeout"
  removed:
    - requirement_id: OLD-001
      reason: "Replaced by NEW-001"
```

### 🆕 Brownfield Mode
Work with existing codebases:
```bash
# Detect and spec existing code
tdd_sdd.init_brownfield(project_dir="./existing-project")
```

### 🆕 Artifact Flow (Optional)
Enhanced workflow with separated artifacts:
```
proposal.md → specs/ → design.md → tasks.md → implement
   (why)      (what)    (how)     (steps)    (code)
```

### 🆕 Archive & Completion
Track spec evolution:
```bash
tdd_sdd.archive_change(change_name="add-oauth")
# Merges deltas into main specs, moves to archive/
```

## When to Use This Skill

**ALWAYS use for:**
- Creating a new OpenClaw skill from scratch
- Adding features to **existing** skills (brownfield)
- Refactoring with test coverage
- Any skill requiring long-term maintenance

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

### Workflow A: Greenfield (New Project) - Default
Traditional TDD+SDD for new skills:

```
SPEC.yaml → Tests → RED → GREEN → REFACTOR → Validate
```

### Workflow B: Brownfield (Existing Project) - NEW
Delta specs for existing codebases:

```
Detect Code → Generate Base Specs → Delta Specs → Tests → Implement → Archive
```

### Workflow C: Artifact Flow (Complex) - NEW
OpenSpec-inspired full workflow:

```
proposal.md → specs/ → design.md → tasks.md → Tests → RED → GREEN → Archive
```

## Quick Start

### Greenfield (Default)
```python
tdd_sdd.init_workflow(skill_name="my-skill")
tdd_sdd.create_spec(requirements="Extract text from PDFs")
tdd_sdd.generate_tests()
tdd_sdd.run_tests()  # RED
tdd_sdd.run_tests()  # GREEN (after implementation)
```

### Brownfield (NEW)
```python
tdd_sdd.init_brownfield(project_dir="./existing-skill")
tdd_sdd.create_delta_spec(
    change_name="add-dark-mode",
    added=["support for dark theme"],
    modified=["color variables"]
)
tdd_sdd.generate_tests()
# ... implement ...
tdd_sdd.archive_change("add-dark-mode")
```

### Artifact Flow (NEW)
```python
tdd_sdd.init_artifact_flow(skill_name="complex-feature")
tdd_sdd.create_proposal(intent="Add real-time collaboration")
tdd_sdd.create_specs_from_proposal()
tdd_sdd.create_design_doc()
tdd_sdd.create_task_list()
# ... implement ...
tdd_sdd.archive_change()
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

### Format 2: Delta Specs (NEW)
```yaml
specification:
  name: "My Skill"
  version: "2.0.0"
  
# Base specs (existing)
requirements:
  - id: AUTH-001
    description: "User can login with password"

# Changes (NEW)
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

## Available Functions

### Core Functions

#### `init_workflow(skill_name: str) -> dict`
Initialize standard TDD+SDD workflow.

#### `init_brownfield(project_dir: str) -> dict` ⭐ NEW
Initialize for existing codebase. Detects current code and generates base specs.

#### `init_artifact_flow(skill_name: str) -> dict` ⭐ NEW
Initialize with full artifact structure (proposal/specs/design/tasks).

### Spec Functions

#### `create_spec(skill_name: str, requirements: str) -> dict`
Create SPEC.yaml from requirements.

#### `create_delta_spec(change_name: str, added: list, modified: list, removed: list) -> dict` ⭐ NEW
Create delta specs for brownfield changes.

#### `validate_spec(spec_path: str) -> dict`
Validate SPEC.yaml format.

### Artifact Functions (NEW)

#### `create_proposal(intent: str, scope: dict) -> dict`
Create proposal.md with intent and scope.

#### `create_specs_from_proposal() -> dict`
Generate specs from proposal.

#### `create_design_doc() -> dict`
Create design.md with technical approach.

#### `create_task_list() -> dict`
Create tasks.md with implementation checklist.

### Test Functions

#### `generate_tests_from_spec(spec_path: str) -> dict`
Generate test files from spec.

#### `run_tests(test_path: str = None) -> dict`
Run tests, returns RED/GREEN status.

#### `check_coverage(threshold: float = 80.0) -> dict`
Check coverage meets threshold.

### Archive Functions (NEW)

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
└── tests/
    ├── unit/
    ├── integration/
    └── acceptance/
```

### With Artifacts (NEW)
```
my-skill/
├── SPEC.yaml              # Current specs (source of truth)
├── artifacts/             # Active change artifacts
│   ├── proposal.md
│   ├── design.md
│   └── tasks.md
├── changes/               # Change tracking (NEW)
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
tdd_sdd.init_workflow(skill_name="my-skill")
tdd_sdd.create_spec(requirements="...")

# TriadDev schedules implementation batches
triadev analyze
triadev implement --all

# Archive on completion
tdd_sdd.archive_change()
triadev run --complete
```

## Critical Rules

### 1. Spec-First (Always)
Never write implementation before spec is complete.

### 2. Delta Specs for Changes (NEW)
Use delta_specs when modifying existing code:
```yaml
delta_specs:
  modified:
    - id: EXISTING-001
      description: "Updated behavior"
```

### 3. Test Coverage Threshold
Minimum 80% coverage required.

### 4. Archive on Completion (NEW)
Always archive changes to maintain spec history:
```python
tdd_sdd.archive_change("feature-name")
```

### 5. Brownfield Detection (NEW)
For existing projects, always start with:
```python
tdd_sdd.init_brownfield(project_dir=".")
```

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Skip specs and code directly | Always define spec first |
| Modify code without delta specs | Use delta_specs for changes |
| Leave changes unarchived | Archive after completion |
| Skip brownfield detection | Use init_brownfield for existing code |
| Mix artifact and standard flow | Choose one approach per project |

## Migration from v1.x

v1.x SPEC.yaml files are **fully compatible** with v2.0. To use new features:

1. Add `delta_specs` section for changes
2. Use `init_brownfield` for existing projects
3. Try `init_artifact_flow` for complex features

No breaking changes - all v1.x workflows continue to work.

## References

| Resource | Purpose |
|----------|---------|
| OpenSpec | https://github.com/Fission-AI/OpenSpec - Inspiration for delta specs |
| TriadDev | Golden Triangle workflow integration |
| Examples | `examples/` directory for sample projects |

---

**Start building with TDD+SDD v2.0 today!** 🚀
