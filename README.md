# TDD+SDD Development v3.2

Dual-pyramid development skill for AI coding agents. Combines Spec-Driven Development
(define WHAT) with Test-Driven Development (verify HOW) using file-based evidence gates.

## Key Feature: TDD Enforcement

AI agents tend to skip the RED phase (writing failing tests first). This skill uses
`.tdd-state.json` as an evidence ledger with mandatory gates:

```
SPEC.yaml exists? → Tests exist? → Tests FAILED (red_evidence)? → NOW write implementation
```

No shortcuts. No fabricated evidence. Real test output required.

## Installation

```bash
# Claude Code
claude skill add Charpup/openclaw-tdd-sdd-skill

# Manual
git clone https://github.com/Charpup/openclaw-tdd-sdd-skill.git ~/.claude/skills/tdd-sdd-development
```

## Part of the Golden Triangle

Integrates with [TriaDev](https://github.com/Charpup/triadev):

```
planning-with-files (plan) → task-workflow (schedule) → value-first-gate (assess) → tdd-sdd (implement)
```

Coordinates via `triadev-handoff.json` — reads `scheduling.batches` and `implementation.current`, writes `implementation.completed`, `.spec_path`, `.tdd_state_path`.

## What's New in v3.2

| Addition | Purpose |
|----------|---------|
| `evals/evals.json` (4 → 8 cases) | New coverage: brownfield initialization (generate base SPEC from existing code), coverage gate enforcement (refuse complete below 80%), state-machine illegal transitions (refuse skip-RED, refuse advance with null red_evidence), delta spec completeness. ~75% deterministic assertions (file_exists, json_path_*, yaml_path_*). |

## Project Structure

```
openclaw-tdd-sdd-skill/
├── SKILL.md                    # Core TDD+SDD workflow instructions
├── LICENSE
├── references/
│   ├── spec-format.md          # SPEC.yaml format reference
│   ├── delta-spec-guide.md     # Brownfield delta spec guide
│   └── tdd-anti-patterns.md    # Why RED gets skipped + how to prevent
├── templates/
│   └── SPEC.yaml               # Specification template
├── scripts/
│   ├── run_tests.py            # pytest runner wrapper
│   └── check_coverage.py       # Coverage threshold checker
├── examples/
│   ├── tdd-demo/               # Calculator TDD example (minimal)
│   └── pdf-ocr-skill/          # GOLD — full brownfield walkthrough
│                               #  (SPEC.yaml + lib/ + tests/ + findings + progress + task_plan)
├── contracts/
│   └── stack-handshake.json    # TriaDev integration contract
├── evals/
│   └── evals.json              # 8 cases (spec creation, RED phase, delta spec,
│                               #  brownfield init, coverage gate, state machine, negative)
└── tests/                      # Skill's own tests
```

## The 6 Critical Rules (Non-Negotiable)

1. **Spec-first**: SPEC.yaml before any code
2. **RED before GREEN**: Tests must fail before implementation begins
3. **Evidence-based**: `.tdd-state.json` must have real test output
4. **80% coverage**: Hard floor, no exceptions
5. **One cycle per requirement**: Don't batch TDD cycles
6. **Archive on complete**: Move finished changes to `archive/`

## Working Examples

- [`examples/pdf-ocr-skill/`](examples/pdf-ocr-skill/) — **GOLD** full walkthrough. Brownfield development of a PDF+OCR module. 10+ files including SPEC.yaml (2 interface contracts, 5 requirements), lib/ implementation, tests/ (unit + integration + acceptance), findings.md (PyMuPDF vs pdfplumber, Tesseract vs PaddleOCR decisions), progress.md, task_plan.md.
- [`examples/tdd-demo/`](examples/tdd-demo/) — minimal calculator TDD skeleton (SPEC + failing tests + conftest).

## Changelog

### v3.2.0 (2026-04-18)
Round-2 evals hardening. Additive; no breaking changes.

- **Hardened**: `evals/evals.json` — 4 → 8 cases. New coverage:
  - `brownfield-init-01`: reading existing src/user_service.py, generating base SPEC.yaml from signatures
  - `coverage-gate-01`: refusing to mark cycle complete when coverage is 65% (< 80% threshold)
  - `state-machine-skip-red-01`: refusing to skip RED phase; enforces "write tests first, see them fail, record evidence"
  - `green-without-red-evidence-01`: refusing to advance to REFACTOR when `red_evidence` is null
- **Assertion mix**: ~75% deterministic (`file_exists`, `json_path_equals`, `yaml_path_equals`, `yaml_path_exists`) vs `llm_judge`, reducing judge-leniency regressions.

### v3.1.0 (2026-04-09)
- **Breaking**: Removed Python runtime modules (src/tdd/, lib/)
- **New**: File-based TDD evidence gates (`.tdd-state.json`)
- **New**: Prompt-centric SKILL.md with mandatory RED phase enforcement
- **New**: TDD anti-patterns reference document
- **New**: Delta spec guide for brownfield development
- **Changed**: tools/ moved to scripts/ (standalone executables)
- **Changed**: Coverage check as standalone script

### v3.0.0
- Added TDD engine module, test generator, coverage analyzer, reporter

## License

MIT
