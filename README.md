# TDD+SDD Development v3.1

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
planning-with-files (plan) → task-workflow (schedule) → tdd-sdd (implement)
```

## Project Structure

```
openclaw-tdd-sdd-skill/
├── SKILL.md                    # Core TDD+SDD workflow instructions
├── references/
│   ├── spec-format.md          # SPEC.yaml format reference
│   ├── delta-spec-guide.md     # Brownfield delta spec guide
│   └── tdd-anti-patterns.md    # Why RED gets skipped + how to prevent
├── templates/
│   ├── SPEC.yaml               # Specification template
│   └── .tdd-state.json         # TDD state file template
├── scripts/
│   ├── run_tests.py            # pytest runner wrapper
│   └── check_coverage.py       # Coverage threshold checker
├── examples/
│   ├── tdd-demo/               # Calculator TDD example
│   └── pdf-ocr-skill/          # Brownfield example
├── contracts/
│   └── stack-handshake.json    # TriaDev integration contract
├── evals/
│   └── evals.json              # Evaluation test cases
└── tests/                      # Skill's own tests
```

## Changelog

### v3.1.0 (2026-04-09)
- **Breaking**: Removed Python runtime modules (src/tdd/, lib/)
- **New**: File-based TDD evidence gates (.tdd-state.json)
- **New**: Prompt-centric SKILL.md with mandatory RED phase enforcement
- **New**: TDD anti-patterns reference document
- **New**: Delta spec guide for brownfield development
- **Changed**: tools/ moved to scripts/ (standalone executables)
- **Changed**: Coverage check as standalone script

### v3.0.0
- Added TDD engine module, test generator, coverage analyzer, reporter

## License

MIT
