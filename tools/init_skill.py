#!/usr/bin/env python3
"""
Initialize a new skill with TDD+SDD structure
Usage: python init_skill.py --name my-skill --path ../my-skill
"""
import argparse
import os
import shutil
from pathlib import Path
from datetime import datetime


def create_directory_structure(base_path: Path):
    """Create the standard skill directory structure"""
    dirs = [
        "lib",
        "tools",
        "tests/unit",
        "tests/integration",
        "tests/acceptance",
        "examples"
    ]
    
    for dir_path in dirs:
        (base_path / dir_path).mkdir(parents=True, exist_ok=True)
        # Add __init__.py to Python packages
        if dir_path.startswith(("lib", "tests")):
            init_file = base_path / dir_path / "__init__.py"
            init_file.touch()
    
    print(f"✅ Created directory structure in {base_path}")


def create_spec_yaml(base_path: Path, skill_name: str):
    """Create SPEC.yaml from template"""
    template_path = Path(__file__).parent.parent / "templates" / "sdd_spec_template.yaml"
    
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Customize template
        content = content.replace("your_skill_name", skill_name)
        content = content.replace("Your Name", os.getenv("USER", "Developer"))
        content = content.replace("YYYY-MM-DD", datetime.now().strftime("%Y-%m-%d"))
        
        spec_path = base_path / "SPEC.yaml"
        with open(spec_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Created SPEC.yaml")
    else:
        print(f"⚠️  Template not found: {template_path}")


def create_test_files(base_path: Path):
    """Create initial test files from templates"""
    template_path = Path(__file__).parent.parent / "templates" / "test_template.py"
    
    if template_path.exists():
        # Copy to unit tests
        shutil.copy(template_path, base_path / "tests" / "unit" / "test_skill.py")
        print(f"✅ Created test_template.py")
    else:
        print(f"⚠️  Test template not found")


def create_pytest_ini(base_path: Path):
    """Create pytest.ini configuration"""
    config = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    acceptance: Acceptance tests
    slow: Slow tests
"""
    
    with open(base_path / "pytest.ini", 'w') as f:
        f.write(config)
    
    print(f"✅ Created pytest.ini")


def create_readme(base_path: Path, skill_name: str):
    """Create initial README.md"""
    readme = f"""# {skill_name}

> OpenClaw Skill with TDD+SDD Development Workflow

## Overview

Brief description of what this skill does.

## Installation

```bash
cd ~/.openclaw/workspace/skills
ln -s $(pwd)/{skill_name} ~/.openclaw/workspace/skills/{skill_name}
```

## Usage

### CLI Tools

```bash
# Add CLI usage examples here
python tools/example_tool.py --help
```

### OpenClaw Integration

```json
{{
  "name": "{skill_name}",
  "tools": ["tools/"]
}}
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test types
pytest tests/unit -v
pytest tests/integration -v
pytest tests/acceptance -v
```

### SDD Specification

See [SPEC.yaml](SPEC.yaml) for the full specification.

## License

MIT License
"""
    
    with open(base_path / "README.md", 'w') as f:
        f.write(readme)
    
    print(f"✅ Created README.md")


def create_gitignore(base_path: Path):
    """Create .gitignore"""
    gitignore = """# Python
__pycache__/
*.py[cod]
*.so
.Python
*.egg-info/

# Virtual Environments
venv/
.env

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDEs
.vscode/
.idea/
*.swp

# Logs
*.log
"""
    
    with open(base_path / ".gitignore", 'w') as f:
        f.write(gitignore)
    
    print(f"✅ Created .gitignore")


def create_requirements_txt(base_path: Path):
    """Create requirements.txt"""
    requirements = """# Add your skill's dependencies here
# pytest is required for TDD+SDD workflow
pytest>=7.0.0
pytest-asyncio>=0.21.0

# Add other dependencies
# example-package>=1.0.0
"""
    
    with open(base_path / "requirements.txt", 'w') as f:
        f.write(requirements)
    
    print(f"✅ Created requirements.txt")


def init_skill(skill_name: str, skill_path: str):
    """Initialize a new skill with TDD+SDD structure"""
    base_path = Path(skill_path).resolve()
    
    # Check if directory already exists
    if base_path.exists():
        print(f"⚠️  Directory already exists: {base_path}")
        response = input("Continue and overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return False
    
    print(f"\n🚀 Initializing skill: {skill_name}")
    print(f"📁 Location: {base_path}\n")
    
    # Create structure
    create_directory_structure(base_path)
    create_spec_yaml(base_path, skill_name)
    create_test_files(base_path)
    create_pytest_ini(base_path)
    create_readme(base_path, skill_name)
    create_gitignore(base_path)
    create_requirements_txt(base_path)
    
    print(f"\n{'='*60}")
    print(f"✅ Skill '{skill_name}' initialized successfully!")
    print(f"{'='*60}")
    print(f"\nNext steps:")
    print(f"  1. cd {base_path}")
    print(f"  2. Edit SPEC.yaml to define your skill's behavior")
    print(f"  3. pip install -r requirements.txt")
    print(f"  4. Implement your skill in lib/")
    print(f"  5. Run tests: pytest tests/unit -v")
    print(f"\nFor more info: https://github.com/Charpup/openclaw-tdd-sdd-skill")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new OpenClaw skill with TDD+SDD structure"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Name of the skill (e.g., my-awesome-skill)"
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Path where skill directory should be created"
    )
    
    args = parser.parse_args()
    
    success = init_skill(args.name, args.path)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
