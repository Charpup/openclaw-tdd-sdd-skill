# TDD+SDD Development Skill for OpenClaw

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/Charpup/openclaw-tdd-sdd-skill/releases/tag/v2.1.0)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-4CAF50.svg)](https://openclaw.ai)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![evals](https://img.shields.io/badge/evals-3%20cases-blueviolet.svg)](evals/evals.json)

> TDD+SDD dual-pyramid workflow with OpenSpec-inspired **delta specs** and **brownfield** support. Manages SPEC.yaml creation, test generation, Red-Green-Refactor cycles, and change tracking — for both new and existing OpenClaw skills.

---

## AI Agent Quick Reference

```yaml
# Skill identity (SKILL.md frontmatter)
name: tdd-sdd-development
version: "3.0.0"
triggers:
  - "TDD"
  - "SDD"
  - "test driven"
  - "spec driven"
  - "SPEC.yaml"
  - "delta spec"
  - "brownfield"
  - "Red-Green-Refactor"

# Runtime requirements
requires:
  bins: [python3, pytest]
  env: []

# Install
run: pip3 install pytest pytest-cov pytest-asyncio pytest-mock pyyaml click rich
```

**When to invoke:**
- Creating a new OpenClaw skill from scratch (greenfield)
- Adding features to an existing skill with change tracking (brownfield + delta specs)
- Any work requiring test coverage, SPEC.yaml, or Red-Green-Refactor cycles
- Refactoring with guaranteed test coverage ≥ 80%

**When NOT to invoke:**
- Simple bug fixes < 5 lines
- Documentation-only changes
- Quick prototypes with no maintenance requirement

---

## What's in v2.0+

### Delta Specs (OpenSpec-inspired)

Track changes to existing systems without touching the base spec:

```yaml
delta_specs:
  added:
    - requirement_id: AUTH-002
      description: "OAuth 2.0 login support"
      scenarios:
        - name: "oauth login"
          given: "valid OAuth token"
          when: "user authenticates"
          then: "session created, JWT returned"
  modified:
    - requirement_id: AUTH-001
      description: "Password login now also accepts OAuth"
      previous: "Password-only login"
  removed:
    - requirement_id: AUTH-000
      reason: "Legacy token system replaced by JWT"
```

### Brownfield Mode

Start from existing code — auto-detect and generate base specs:

```python
tdd_sdd.init_brownfield(project_dir="./existing-skill")
# → scans src/, generates base SPEC.yaml from code signatures
# → ready for delta spec additions
```

### Artifact Flow

OpenSpec-inspired full design pipeline for complex features:

```
proposal.md → specs/ → design.md → tasks.md → implement → archive
   (why)       (what)    (how)      (steps)
```

### Archive & Spec Evolution

Complete a change, merge deltas into main SPEC, move artifacts to `archive/`:

```python
tdd_sdd.archive_change("add-oauth")
# → merges delta_specs into requirements
# → moves changes/add-oauth/ to changes/archive/2026-02-25-add-oauth/
# → SPEC.yaml is now the single source of truth
```

---

## Core Workflows

### Workflow A: Greenfield (new skill)

```
SPEC.yaml → test stubs (RED) → implementation (GREEN) → coverage check → REFACTOR
```

```python
tdd_sdd.init_workflow(skill_name="rate-limiter")
tdd_sdd.create_spec(requirements="Limit API calls to 100/min per user, 429 on overflow")
tdd_sdd.generate_tests_from_spec(spec_path="./SPEC.yaml")
tdd_sdd.run_tests()         # RED: tests fail (not implemented)
# ... implement ...
tdd_sdd.run_tests()         # GREEN: tests pass
tdd_sdd.check_coverage()    # must be ≥ 80%
```

### Workflow B: Brownfield (existing skill)

```
detect code → base SPEC → delta specs → tests → implement → archive
```

```python
tdd_sdd.init_brownfield(project_dir="./auth-service")
tdd_sdd.create_delta_spec(
    change_name="add-oauth",
    added=["OAuth 2.0 support"],
    modified=["session handling"],
    removed=["legacy token auth"],
)
tdd_sdd.generate_tests()
# ... implement ...
tdd_sdd.archive_change("add-oauth")
```

### Workflow C: Artifact Flow (complex feature)

```python
tdd_sdd.init_artifact_flow(skill_name="payment-gateway")
tdd_sdd.create_proposal(intent="Add Stripe integration",
                         scope={"in": "payment processing", "out": "tax calculation"})
tdd_sdd.create_specs_from_proposal()
tdd_sdd.create_design_doc()
tdd_sdd.create_task_list()
# ... implement ...
tdd_sdd.archive_change()
```

---

## SPEC.yaml Format

### Standard (v1.x compatible)

```yaml
specification:
  name: "rate-limiter"
  version: "1.0.0"

requirements:
  - id: RATE-001
    description: "Limit API calls to 100 per minute per user"
    scenarios:
      - name: "within limit"
        given: "user has made 99 calls this minute"
        when: "user makes one more call"
        then: "call succeeds, counter = 100"
      - name: "over limit"
        given: "user has made 100 calls this minute"
        when: "user makes another call"
        then: "HTTP 429 Too Many Requests returned"
```

### With Delta Specs (v2.x)

```yaml
specification:
  name: "auth-service"
  version: "2.0.0"

requirements:        # existing, unchanged
  - id: AUTH-001
    description: "Password login"

delta_specs:         # new in v2.0
  added:
    - id: AUTH-002
      description: "OAuth login"
  modified:
    - id: AUTH-001
      description: "Password or OAuth login"
      previous: "Password login"
  removed:
    - id: AUTH-000
      reason: "Legacy tokens deprecated"
```

---

## Project Structure

```
my-skill/
├── SKILL.md              # OpenClaw skill manifest
├── SPEC.yaml             # Requirements (source of truth)
├── requirements.txt
├── pytest.ini
│
├── lib/                  # Implementation
│   ├── workflow.py       # Agent-callable functions
│   ├── state_machine.py  # TDD state enforcement
│   └── ...
│
├── tools/                # CLI tools
│   ├── validate_spec.py
│   └── run_tests.py
│
├── templates/
│   ├── sdd_spec_template.yaml
│   └── test_template.py
│
├── changes/              # Active change tracking (brownfield)
│   ├── add-oauth/        # Active change
│   └── archive/          # Completed changes
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── acceptance/
│
└── evals/
    └── evals.json        # Skill-creator standard test cases
```

---

## Critical Rules

1. **Spec-first always** — never write implementation before SPEC.yaml is complete
2. **Delta specs for changes** — use `delta_specs` when modifying existing functionality
3. **80% coverage minimum** — `check_coverage(threshold=80.0)` must pass before done
4. **Archive on completion** — always `archive_change()` to maintain spec history
5. **Brownfield detection** — for existing projects, always start with `init_brownfield()`

---

## Evals

Test cases in [`evals/evals.json`](evals/evals.json):

| ID | Scenario | Expected Trigger |
|----|----------|-----------------|
| 1 | Create SPEC.yaml for a rate-limiter skill (greenfield) | ✅ Yes |
| 2 | Create delta spec for adding OAuth to existing auth service | ✅ Yes |
| 3 | Fix a typo in a variable name | ❌ No |

---

## Version History

| Version | Changes |
|---------|---------|
| **v2.1.0** | Add `metadata.openclaw` compliance; add `evals/evals.json` (3 cases) |
| **v2.0.0** | Delta specs, brownfield mode, artifact flow, archive & spec evolution |
| **v1.1.0** | planning-with-files integration, state machine |
| **v1.0.0** | Initial TDD+SDD dual-pyramid workflow |

---

## Integration: TriadDev Golden Triangle

```
📋 planning-with-files   →   📊 task-workflow   →   🧪 tdd-sdd-development  ← (this skill)
  (task_plan.md)              (batch schedule)         (SPEC.yaml + tests)
```

Use [triadev](https://github.com/Charpup/triadev) to orchestrate all three automatically.

---

## Related Projects

- [planning-with-files](https://github.com/OthmanAdi/planning-with-files) — File-based planning (Manus pattern)
- [task-workflow](https://github.com/Charpup/openclaw-task-workflow) — DAG task scheduling
- [triadev](https://github.com/Charpup/triadev) — Golden Triangle orchestrator
- [OpenSpec](https://github.com/Fission-AI/OpenSpec) — Inspiration for delta specs

## Testing

```bash
pip install -r requirements.txt
pytest tests/ -v --cov=lib --cov-report=term-missing
```

## License

MIT — [Charpup](https://github.com/Charpup)
