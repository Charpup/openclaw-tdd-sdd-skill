---
name: tdd-sdd-development
description: >-
  TRIGGER: TDD, SDD, test driven, spec driven, SPEC.yaml, RED GREEN REFACTOR,
  test coverage, delta spec, brownfield testing, write tests first.
  TDD+SDD dual-pyramid development workflow. SDD drives WHAT to build (SPEC.yaml),
  TDD drives HOW to verify it (RED-GREEN-REFACTOR with file-based evidence gates).
  Enforces spec-first development and mandatory test-failure evidence before
  implementation. 80% coverage hard threshold.
  Use for any code that needs tests, specs, or long-term maintainability.
  NOT for trivial fixes (< 5 lines) or documentation-only changes.
---

# TDD+SDD Development v3.1

Two frameworks, one workflow:
- **SDD (Spec-Driven Development)**: Define WHAT to build in SPEC.yaml before writing code
- **TDD (Test-Driven Development)**: Verify HOW it works via RED -> GREEN -> REFACTOR with evidence

## The Two Pyramids

```
    SDD Pyramid                    TDD Pyramid
    (What to build)                (How to verify)

      /SPEC.yaml\                  /Acceptance\
     /  scenarios  \              / Integration \
    / requirements  \            /  Unit Tests   \
   ──────────────────           ──────────────────
   Defines behavior             Proves behavior
```

SDD answers "what does this do?" -- TDD answers "does it actually work?"

## When to Use

**Always use for:**
- New features or modules
- Refactoring with behavior preservation
- Any code needing long-term maintenance
- Brownfield modifications (delta specs)

**Skip for:**
- Simple bug fixes (< 5 lines, root cause known)
- Documentation-only changes
- Quick prototypes explicitly marked as throwaway

## The TDD Enforcement Problem

AI agents naturally skip the RED phase -- they want to solve the problem immediately.
This skill uses **file-based evidence gates** to enforce the full TDD cycle.

See [references/tdd-anti-patterns.md](references/tdd-anti-patterns.md) for why this matters.

---

## Core Workflow

### Phase 0: Spec Creation (SDD)

**Before any code exists**, create `SPEC.yaml`:

1. Define the specification name, version, description
2. List requirements with unique IDs (FEAT-001, AUTH-001, etc.)
3. Write scenarios in Given-When-Then format for each requirement
4. Set tdd_config: test framework, coverage threshold (minimum 80%)

See [references/spec-format.md](references/spec-format.md) for format details.
Use [templates/SPEC.yaml](templates/SPEC.yaml) as a starting point.

**Gate: No SPEC.yaml -> no code allowed.**

### Phase 1: RED -- Write Failing Tests

For each requirement in SPEC.yaml:

1. Create test file(s) in `tests/` based on the scenarios
2. Write test functions that call the not-yet-implemented code
3. Run the tests: `pytest tests/ -v`
4. **They MUST fail** (NotImplementedError, ImportError, or assertion failures)
5. Record the evidence in `.tdd-state.json`:

```json
{
  "spec_id": "FEAT-001",
  "phase": "red",
  "red_evidence": {
    "timestamp": "2026-04-09T10:00:00",
    "test_command": "pytest tests/ -v",
    "tests_total": 4,
    "tests_failed": 4,
    "output_snapshot": "FAILED tests/test_auth.py::test_login - NotImplementedError"
  }
}
```

**Gate: No red_evidence in .tdd-state.json -> cannot write implementation code.**

The `red_evidence.output_snapshot` must be actual test runner output, not fabricated.

### Phase 2: GREEN -- Minimal Implementation

Now (and ONLY now) write implementation code:

1. Write the **minimum code** to make all failing tests pass
2. Do not add features beyond what the tests require
3. Run tests again: `pytest tests/ -v`
4. **All tests must pass**
5. Record evidence:

```json
{
  "phase": "green",
  "green_evidence": {
    "timestamp": "2026-04-09T10:30:00",
    "tests_total": 4,
    "tests_passed": 4
  }
}
```

**Gate: Any test still failing -> stay in GREEN, keep fixing.**

### Phase 3: REFACTOR -- Quality + Coverage

With all tests green, improve code quality:

1. Refactor implementation (extract functions, improve naming, remove duplication)
2. Run tests after each refactor step -- they must stay green
3. Check coverage: `python scripts/check_coverage.py --threshold 80`
4. Record coverage:

```json
{
  "phase": "refactor",
  "coverage": {
    "percentage": 85.0,
    "meets_threshold": true
  }
}
```

**Gate: Coverage < 80% -> add more tests, do not proceed.**

### Phase 4: Complete -- Archive the Cycle

1. **Before** marking the cycle complete, invoke [`verification-before-completion`](../verification-before-completion/SKILL.md) skill to verify: (a) `.tdd-state.json` has non-null `red_evidence` + `green_evidence` + `coverage.percentage >= 80`, (b) re-read `.tdd-state.json` after any write
2. Update `.tdd-state.json` phase to "complete"
3. Move cycle data to `cycle_history` array
4. If more requirements remain in SPEC.yaml, start a new RED phase for the next one
5. When all requirements are done, archive changes

---

## TDD State Machine

```
red --> green --> refactor --> complete
 ^                                |
 '-------- next requirement ------'
```

**Rules:**
- Transitions are one-way: red -> green -> refactor -> complete
- Cannot skip phases (no red -> refactor)
- Cannot go backward (no green -> red) except starting a new cycle
- Each SPEC requirement gets its own cycle

## The .tdd-state.json File

This file is the TDD evidence ledger. It lives in the project root.

```json
{
  "spec_id": "FEAT-001",
  "phase": "red",
  "red_evidence": {
    "timestamp": "ISO-8601",
    "test_command": "the exact command run",
    "tests_total": 4,
    "tests_failed": 4,
    "output_snapshot": "first 200 chars of failure output"
  },
  "green_evidence": {
    "timestamp": "ISO-8601",
    "tests_total": 4,
    "tests_passed": 4
  },
  "coverage": {
    "percentage": 85.0,
    "meets_threshold": true
  },
  "cycle_history": [
    {
      "spec_id": "FEAT-000",
      "completed_at": "ISO-8601",
      "coverage": 92.0
    }
  ]
}
```

**Ownership:** Only tdd-sdd reads and writes this file. Other skills do not access it.

---

## Brownfield Development (Delta Specs)

For existing codebases:

1. Assess existing code -> generate base SPEC.yaml with current requirements
2. Add `delta_specs` section for changes (added/modified/removed)
3. Run TDD cycle only for delta items
4. Existing tests must remain green throughout
5. Archive deltas when complete

See [references/delta-spec-guide.md](references/delta-spec-guide.md) for details.

## Integration with TriaDev

When used as part of the Golden Triangle:

**What tdd-sdd reads:**
- `triadev-handoff.json` -> `scheduling.batches` (which task to implement next)
- `triadev-handoff.json` -> `implementation.current` (current task ID)

**What tdd-sdd writes:**
- `triadev-handoff.json` -> `implementation.completed` (append task ID on completion)
- `triadev-handoff.json` -> `implementation.spec_path` (path to SPEC.yaml)
- `triadev-handoff.json` -> `implementation.tdd_state_path` (path to .tdd-state.json)

**What tdd-sdd does NOT do:**
- Does not create or modify `task_plan.md` (that's planning-with-files)
- Does not schedule tasks (that's task-workflow)
- Does not make routing decisions (that's triadev)

## Helper Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/run_tests.py` | Run pytest with categorization | `python scripts/run_tests.py [unit\|integration\|all]` |
| `scripts/check_coverage.py` | Check coverage vs threshold | `python scripts/check_coverage.py --threshold 80` |

Scripts are **optional** -- Claude can run pytest directly. Use scripts for
formatted output or when integrating with CI.

## Project Structure

```
project/
├── SPEC.yaml              # Specification (source of truth)
├── .tdd-state.json        # TDD cycle evidence
├── src/                   # Implementation code
├── tests/
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── acceptance/        # Acceptance tests
└── changes/               # Brownfield change tracking
    ├── active/
    └── archive/
```

## Self-Check Before Writing Implementation

Before writing ANY code in `src/`:

- [ ] SPEC.yaml exists with requirements defined?
- [ ] Test files exist in `tests/` for the current requirement?
- [ ] Tests have been run and FAILED (red_evidence in .tdd-state.json)?
- [ ] Failures are because code doesn't exist yet (NOT test syntax errors)?

If any answer is NO -> go back to the appropriate phase.

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Write implementation before tests | Write tests first, see them fail (RED) |
| Write tests that pass immediately | Tests must fail first -- that's the point |
| Skip RED phase because "tests are obvious" | Write them anyway; obvious tests catch non-obvious bugs |
| Test implementation details | Test behavior (Given-When-Then from SPEC) |
| Write all tests for all requirements at once | One requirement per TDD cycle |
| Accept coverage below 80% | Add tests until threshold is met |
| Fabricate red_evidence output | Run actual tests; paste actual output |
| Skip SPEC.yaml for "simple" features | If it needs tests, it needs a spec |

## Critical Rules (Non-Negotiable)

1. **Spec-first**: SPEC.yaml before any code
2. **RED before GREEN**: Tests must fail before implementation begins
3. **Evidence-based**: .tdd-state.json must have real test output
4. **80% coverage**: Hard floor, no exceptions
5. **One cycle per requirement**: Don't batch TDD cycles
6. **Archive on complete**: Move finished changes to archive/
