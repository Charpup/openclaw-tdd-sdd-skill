# TDD Anti-Patterns — Why RED Gets Skipped

## The Core Problem

AI coding agents (including Claude) naturally gravitate toward solving problems immediately.
TDD requires the counterintuitive discipline of writing tests FIRST, watching them FAIL,
and only THEN writing implementation. Without enforcement mechanisms, the RED phase gets skipped.

## Common Anti-Patterns

### 1. "I'll Write Tests After" (GREEN-first)

**What happens:** Claude writes implementation code, then writes tests that pass.
**Why it's bad:** Tests written after implementation tend to test what the code does,
not what it should do. They miss edge cases the implementation accidentally handles.
**Detection:** `.tdd-state.json` has no `red_evidence` but `green_evidence` exists.

### 2. "The Tests Are Obvious" (Spec-to-Code Skip)

**What happens:** Claude reads SPEC.yaml and jumps straight to implementation.
**Why it's bad:** The spec might be ambiguous. Writing tests first forces you to
make the spec concrete — what exactly is a "valid" input?
**Detection:** SPEC.yaml exists, test files don't, but src/ files do.

### 3. "Let Me Fix Just This One Thing" (Partial Implementation Before RED)

**What happens:** Claude starts RED phase but writes a "skeleton" implementation
to help think about the tests.
**Why it's bad:** The skeleton often becomes the implementation. Tests get written
to match the skeleton instead of the spec.
**Detection:** src/ files modified before `.tdd-state.json` records red_evidence.

### 4. "80% Coverage Is Close Enough" (Coverage Shortcut)

**What happens:** Coverage is at 75% and Claude declares REFACTOR complete.
**Why it's bad:** 80% is the hard threshold. Below it, critical paths may be untested.
**Detection:** `.tdd-state.json` coverage.percentage < 80.

### 5. "Batch All Requirements" (Mega-Cycle)

**What happens:** Claude writes tests for ALL requirements at once, then implements all.
**Why it's bad:** Debugging failures is harder. The RED-GREEN feedback loop loses its value.
**Detection:** Single TDD cycle covers 5+ requirements.

## Self-Check Checklist

Before writing any implementation code, ask:

1. Does `.tdd-state.json` exist with `phase: "red"`?
2. Do test files exist in `tests/`?
3. Have the tests been run and FAILED (red_evidence populated)?
4. Is the failure because of NotImplementedError or missing module (expected)?
5. NOT because of test syntax errors (fix those first)?

Only if ALL answers are YES → proceed to GREEN phase.

## Why This Matters

TDD isn't about having tests. It's about the **design feedback** from writing tests first:
- Tests reveal ambiguous requirements early
- Tests define the public API before implementation constrains it
- The RED-GREEN cycle keeps changes small and reviewable
- Coverage is a natural byproduct, not an afterthought
