# TDD+SDD Dual Pyramid Skill for OpenClaw

> A production-ready skill framework combining Test-Driven Development (TDD) for implementation layer with Spec-Driven Development (SDD) for AI Agent behavior layer.

## 🎯 Overview

This skill provides a complete development workflow for OpenClaw agents that bridges traditional software engineering practices with AI-native development patterns.

### The Dual Pyramid Model

```
SDD Pyramid (Behavior Layer - AI Agent)
    ├── End-to-End Acceptance (Agent tasks)
    ├── Module Collaboration Tests
    └── Tool Function Contracts

TDD Pyramid (Implementation Layer - Traditional)
    ├── Interface Contract Tests
    ├── Module Integration
    └── Function-Level Unit Tests
```

## 🚀 Quick Start

### Installation

```bash
# Clone the skill to your OpenClaw workspace
cd ~/.openclaw/workspace/skills
git clone https://github.com/Charpup/openclaw-tdd-sdd-skill.git

# Install dependencies
cd openclaw-tdd-sdd-skill
pip install -r requirements.txt
```

### Creating a New Skill with TDD+SDD

```bash
# Use the initialization tool
python tools/init_skill.py --name my-new-skill --path ../my-new-skill

# This creates:
# ├── SPEC.yaml              # SDD specification
# ├── pytest.ini             # Test configuration
# ├── lib/                   # Implementation
# ├── tools/                 # CLI tools
# └── tests/                 # Test suites
```

## 📁 Project Structure

```
tdd-sdd-skill/
├── README.md                # This file
├── LICENSE                  # MIT License
├── requirements.txt         # Python dependencies
├── pytest.ini              # pytest configuration
│
├── lib/                    # Core libraries
│   ├── sdd_validator.py    # SPEC.yaml validation
│   ├── test_generator.py   # Test generation from spec
│   └── coverage_reporter.py # Coverage reporting
│
├── tools/                  # CLI tools
│   ├── init_skill.py       # Initialize new skill
│   ├── validate_spec.py    # Validate SPEC.yaml
│   └── run_tests.py        # Run test suite
│
├── templates/              # Starter templates
│   ├── sdd_spec_template.yaml
│   ├── test_template.py
│   └── skill_manifest_template.json
│
├── examples/               # Example implementations
│   └── memu-skill-example/ # Reference implementation
│
└── tests/                  # Self-tests
    ├── unit/
    ├── integration/
    └── acceptance/
```

## 📝 SPEC.yaml Format

The SDD specification defines behavior through scenarios and contracts:

```yaml
spec_version: "1.0"
module_name: "example_skill"
description: "Example skill demonstrating TDD+SDD"

interfaces:
  - name: "ExampleService"
    type: "class"
    
    methods:
      - name: "process"
        signature: "(input: str) -> dict"
        description: "Process input and return result"
        
        contract:
          preconditions:
            - "input is not empty"
          postconditions:
            - "result contains 'output' key"
        
        test_cases:
          - id: "TC-001"
            name: "Valid input"
            input: {input: "hello"}
            expected: {output: "HELLO"}

scenarios:
  - id: "E2E-001"
    name: "Complete workflow"
    given:
      - condition: "Service is initialized"
    when:
      - action: "Call process()"
    then:
      - expectation: "Result is valid"

acceptance_criteria:
  functional:
    - "All unit tests pass"
    - "Code coverage >= 80%"
```

## 🧪 Testing Workflow

### 1. Write SPEC.yaml First (SDD)

Define behavior through scenarios before writing code.

### 2. Generate Test Stubs

```bash
python tools/generate_tests.py --spec SPEC.yaml --output tests/
```

### 3. Implement to Make Tests Pass (TDD)

```bash
# Red: Write failing test
# Green: Make it pass
# Refactor: Improve code

pytest tests/unit -v
```

### 4. Validate Against SPEC

```bash
python tools/validate_spec.py --spec SPEC.yaml --tests tests/
```

## 🎓 Learning Resources

- [TDD+SDD Research Report](docs/research-report.md)
- [Dual Pyramid Explained](docs/dual-pyramid.md)
- [MemU Skill Example](examples/memu-skill-example/)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenClaw community for the agent framework
- MemU team for the memory system that inspired this workflow
- Master Charpup for the TDD+SDD concept and validation

---

*Built with ❤️ for the OpenClaw ecosystem*
