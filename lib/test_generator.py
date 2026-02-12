"""
Test Generator Module
Generates pytest test stubs from SPEC.yaml definitions

This module implements the TDD+SDD dual-pyramid test generation:
- Unit tests: Interface-level contract tests
- Integration tests: Module collaboration tests  
- Acceptance tests: BDD-style scenario tests
"""

import yaml
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from jinja2 import Template, Environment


def _repr_filter(value):
    """Custom Jinja2 filter to get Python repr of a value"""
    return repr(value)


# Create Jinja environment with custom filters
_jinja_env = Environment()
_jinja_env.filters['repr'] = _repr_filter


# =============================================================================
# Templates for test generation
# =============================================================================

UNIT_TEST_TEMPLATE = '''"""
Auto-generated unit tests for {{ interface_name }}
Generated from SPEC.yaml by TDD+SDD Skill
"""
import pytest
from typing import Any, Dict, List, Optional


class {{ test_class_name }}:
    """Tests for {{ interface_name }} - {{ interface_description }}"""
    
    {% if has_methods %}
    {% for method in methods %}
    {% if method.test_cases %}
    {% for tc in method.test_cases %}
    def test_{{ method.name }}_{{ tc.id | lower | replace('-', '_') }}(self):
        """
        {{ tc.name }} (SPEC: {{ tc.id }})
        
        Input: {{ tc.input | default({}) }}
        Expected: {{ tc.expected | default({}) }}
        """
        # TODO: Implement test
        # Arrange
        {% for key, value in (tc.input or {}).items() %}
        {{ key }} = {{ value | repr }}
        {% endfor %}
        
        # Act
        # result = {{ method.name }}({% for key in (tc.input or {}).keys() %}{{ key }}{% if not loop.last %}, {% endif %}{% endfor %})
        
        # Assert
        {% if tc.expected and 'exception' in tc.expected %}
        # with pytest.raises({{ tc.expected.exception }}):
        #     {{ method.name }}(...)
        {% else %}
        {% for key, value in (tc.expected or {}).items() %}
        # assert result['{{ key }}'] == {{ value | repr }}
        {% endfor %}
        {% endif %}
        pytest.skip("Test not yet implemented")
    {% endfor %}
    {% else %}
    def test_{{ method.name }}_exists(self):
        """Test {{ method.name }} method exists and is callable"""
        # TODO: Implement test
        pytest.skip("Test not yet implemented")
    {% endif %}
    {% endfor %}
    {% else %}
    def test_{{ interface_name | lower }}_initialization(self):
        """Test {{ interface_name }} can be initialized"""
        # TODO: Implement test
        pytest.skip("Test not yet implemented")
    {% endif %}
    
    {% if contract_preconditions %}
    def test_contract_preconditions(self):
        """Test contract preconditions are enforced"""
        # TODO: Implement based on SPEC preconditions:
        {% for pre in contract_preconditions %}
        # - {{ pre }}
        {% endfor %}
        pytest.skip("Test not yet implemented")
    {% endif %}
    
    {% if contract_postconditions %}
    def test_contract_postconditions(self):
        """Test contract postconditions are satisfied"""
        # TODO: Implement based on SPEC postconditions:
        {% for post in contract_postconditions %}
        # - {{ post }}
        {% endfor %}
        pytest.skip("Test not yet implemented")
    {% endif %}
'''


ACCEPTANCE_TEST_TEMPLATE = '''"""
Auto-generated acceptance tests for {{ scenario_id }}
Generated from SPEC.yaml by TDD+SDD Skill
"""
import pytest


class {{ test_class_name }}:
    """Scenario: {{ scenario_name }}"""
    
    def test_given_{{ given_slug }}_when_{{ when_slug }}_then_{{ then_slug }}(self):
        """
        {{ scenario_name }} (SPEC: {{ scenario_id }})
        
        Given:
        {% for condition in given_conditions %}
          - {{ condition }}
        {% endfor %}
        
        When:
        {% for action in when_actions %}
          - {{ action }}
        {% endfor %}
        
        Then:
        {% for expectation in then_expectations %}
          - {{ expectation }}
        {% endfor %}
        """
        # TODO: Implement acceptance test
        {% if quality_attributes %}
        # Quality attributes to verify:
        {% for qa in quality_attributes %}
        # - {{ qa.name }}: {{ qa.threshold }}
        {% endfor %}
        {% endif %}
        pytest.skip("Acceptance test not yet implemented")
'''


CONFTEST_TEMPLATE = '''"""
Shared fixtures for pytest
Generated from SPEC.yaml by TDD+SDD Skill
"""
import pytest
from typing import Any, Dict, List, Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


{% for fixture in fixtures %}
@pytest.fixture
def {{ fixture.name }}():
    """{{ fixture.description }}"""
    # TODO: Implement fixture
    {% if fixture.default_value is defined %}
    return {{ fixture.default_value | repr }}
    {% else %}
    return None
    {% endif %}

{% endfor %}
{% if not fixtures %}
# TODO: Add shared fixtures here
# Example:
# @pytest.fixture
# def mock_data():
#     return {"key": "value"}
{% endif %}
'''


INTEGRATION_TEST_TEMPLATE = '''"""
Auto-generated integration tests for {{ module_name }}
Generated from SPEC.yaml by TDD+SDD Skill
"""
import pytest
from typing import Any, Dict, List, Optional


class Test{{ module_name | capitalize }}Collaboration:
    """Integration tests for {{ module_name }} module collaboration"""
    
    def test_module_initialization(self):
        """Test all components initialize correctly together"""
        # TODO: Implement integration test
        pytest.skip("Integration test not yet implemented")
    
    {% for interface in interfaces %}
    def test_{{ interface.name | lower }}_integration(self):
        """Test {{ interface.name }} collaborates with other components"""
        # TODO: Implement integration test for {{ interface.name }}
        pytest.skip("Integration test not yet implemented")
    {% endfor %}
'''


# =============================================================================
# Helper Functions
# =============================================================================

def _slugify(text: str) -> str:
    """Convert text to a valid Python identifier slug"""
    # Remove non-alphanumeric characters and convert to lowercase
    slug = re.sub(r'[^\w\s]', '', text.lower())
    # Replace spaces with underscores
    slug = re.sub(r'\s+', '_', slug)
    # Remove leading/trailing underscores
    slug = slug.strip('_')
    return slug or "unknown"


def _to_valid_identifier(name: str) -> str:
    """Convert a name to a valid Python identifier"""
    # Replace invalid characters with underscores
    identifier = re.sub(r'[^\w]', '_', name)
    # Ensure it doesn't start with a digit
    if identifier and identifier[0].isdigit():
        identifier = '_' + identifier
    return identifier


def _extract_contract_conditions(interface: Dict[str, Any]) -> tuple:
    """Extract all preconditions and postconditions from interface methods"""
    preconditions = []
    postconditions = []
    
    for method in interface.get('methods', []):
        contract = method.get('contract', {})
        preconditions.extend(contract.get('preconditions', []))
        postconditions.extend(contract.get('postconditions', []))
    
    return preconditions, postconditions


# =============================================================================
# Public API Functions
# =============================================================================

def generate_tests_from_spec(spec_path: str, output_dir: str = "tests") -> dict:
    """
    Generate test files from SPEC.yaml.
    
    Creates test stubs organized into the dual-pyramid structure:
    - tests/unit/         : Function-level unit tests for each interface
    - tests/integration/  : Module collaboration tests
    - tests/acceptance/   : End-to-end acceptance tests for each scenario
    
    Also generates tests/conftest.py with shared fixtures.
    
    Args:
        spec_path: Path to the SPEC.yaml file
        output_dir: Directory where tests will be generated (default: "tests")
    
    Returns:
        dict: {
            "test_files": list,     # List of generated test file paths
            "total_tests": int,     # Total number of test cases generated
            "status": str           # "generated" | "partial" | "error"
        }
    
    Example:
        >>> result = generate_tests_from_spec("./SPEC.yaml", "tests")
        >>> print(f"Generated {result['total_tests']} tests")
        >>> for f in result["test_files"]:
        ...     print(f"  - {f}")
    """
    spec_file = Path(spec_path)
    if not spec_file.exists():
        return {
            "test_files": [],
            "total_tests": 0,
            "status": "error",
            "error": f"Specification file not found: {spec_path}"
        }
    
    # Load SPEC.yaml
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            spec = yaml.safe_load(f)
    except Exception as e:
        return {
            "test_files": [],
            "total_tests": 0,
            "status": "error",
            "error": f"Failed to parse SPEC.yaml: {str(e)}"
        }
    
    output_path = Path(output_dir)
    test_files = []
    total_tests = 0
    
    module_name = spec.get('module_name', 'unknown')
    interfaces = spec.get('interfaces', [])
    scenarios = spec.get('scenarios', [])
    
    # Create output directories
    unit_dir = output_path / 'unit'
    integration_dir = output_path / 'integration'
    acceptance_dir = output_path / 'acceptance'
    
    unit_dir.mkdir(parents=True, exist_ok=True)
    integration_dir.mkdir(parents=True, exist_ok=True)
    acceptance_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unit tests for each interface
    for interface in interfaces:
        interface_name = interface.get('name', 'unknown')
        output_file = unit_dir / f"test_{interface_name.lower()}.py"
        generate_unit_test(interface, str(output_file))
        test_files.append(str(output_file))
        
        # Count test cases
        for method in interface.get('methods', []):
            test_cases = method.get('test_cases', [])
            total_tests += len(test_cases) if test_cases else 1
    
    # Generate integration test file
    integration_file = integration_dir / f"test_{module_name}_collaboration.py"
    _generate_integration_test(spec, str(integration_file))
    test_files.append(str(integration_file))
    
    # Generate acceptance tests for each scenario
    for scenario in scenarios:
        scenario_id = scenario.get('id', 'unknown')
        output_file = acceptance_dir / f"test_{_slugify(scenario_id)}.py"
        generate_acceptance_test(scenario, str(output_file))
        test_files.append(str(output_file))
        total_tests += 1
    
    # Generate conftest.py with shared fixtures
    conftest_file = output_path / 'conftest.py'
    fixtures = spec.get('fixtures', [])
    generate_conftest(fixtures, str(conftest_file))
    test_files.append(str(conftest_file))
    
    return {
        "test_files": test_files,
        "total_tests": total_tests,
        "status": "generated"
    }


def generate_unit_test(interface: Dict[str, Any], output_path: str) -> None:
    """
    Generate unit test file for a single interface.
    
    Args:
        interface: Interface definition from SPEC.yaml
        output_path: Path where the test file will be written
    
    Example:
        >>> interface = {
        ...     "name": "Service",
        ...     "description": "Main service class",
        ...     "methods": [
        ...         {
        ...             "name": "process",
        ...             "test_cases": [{"id": "TC-001", "name": "Valid input"}]
        ...         }
        ...     ]
        ... }
        >>> generate_unit_test(interface, "tests/unit/test_service.py")
    """
    interface_name = interface.get('name', 'Unknown')
    interface_description = interface.get('description', 'No description')
    methods = interface.get('methods', [])
    
    # Extract contract conditions from all methods
    preconditions, postconditions = _extract_contract_conditions(interface)
    
    template = _jinja_env.from_string(UNIT_TEST_TEMPLATE)
    content = template.render(
        interface_name=interface_name,
        test_class_name=f"Test{interface_name}",
        interface_description=interface_description,
        methods=methods,
        has_methods=len(methods) > 0,
        contract_preconditions=preconditions,
        contract_postconditions=postconditions
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_acceptance_test(scenario: Dict[str, Any], output_path: str) -> None:
    """
    Generate BDD-style acceptance test for a scenario.
    
    Args:
        scenario: Scenario definition from SPEC.yaml with given/when/then structure
        output_path: Path where the acceptance test file will be written
    
    Example:
        >>> scenario = {
        ...     "id": "E2E-001",
        ...     "name": "Extract text from PDF",
        ...     "given": [{"condition": "Valid PDF file exists"}],
        ...     "when": [{"action": "Extract text is called"}],
        ...     "then": [{"expectation": "Text is returned"}]
        ... }
        >>> generate_acceptance_test(scenario, "tests/acceptance/test_e2e_001.py")
    """
    scenario_id = scenario.get('id', 'unknown')
    scenario_name = scenario.get('name', 'Unnamed scenario')
    
    # Extract Gherkin-style conditions
    given_conditions = [g.get('condition', '') for g in scenario.get('given', [])]
    when_actions = [w.get('action', '') for w in scenario.get('when', [])]
    then_expectations = [t.get('expectation', '') for t in scenario.get('then', [])]
    quality_attributes = scenario.get('quality_attributes', [])
    
    # Create slugs for method name
    given_slug = _slugify(given_conditions[0]) if given_conditions else "setup"
    when_slug = _slugify(when_actions[0]) if when_actions else "action"
    then_slug = _slugify(then_expectations[0]) if then_expectations else "result"
    
    template = _jinja_env.from_string(ACCEPTANCE_TEST_TEMPLATE)
    content = template.render(
        scenario_id=scenario_id,
        scenario_name=scenario_name,
        test_class_name=f"Test{_to_valid_identifier(scenario_id)}",
        given_slug=given_slug,
        when_slug=when_slug,
        then_slug=then_slug,
        given_conditions=given_conditions,
        when_actions=when_actions,
        then_expectations=then_expectations,
        quality_attributes=quality_attributes
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_conftest(fixtures: List[Dict[str, Any]], output_path: str) -> None:
    """
    Generate conftest.py with shared fixtures.
    
    Args:
        fixtures: List of fixture definitions from SPEC.yaml
        output_path: Path where conftest.py will be written
    
    Example:
        >>> fixtures = [
        ...     {"name": "mock_service", "description": "Mock service fixture"},
        ...     {"name": "test_data", "description": "Sample test data", "default_value": {"key": "value"}}
        ... ]
        >>> generate_conftest(fixtures, "tests/conftest.py")
    """
    template = _jinja_env.from_string(CONFTEST_TEMPLATE)
    content = template.render(fixtures=fixtures)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


# =============================================================================
# Private Helper Functions
# =============================================================================

def _generate_integration_test(spec: Dict[str, Any], output_path: str) -> None:
    """
    Generate integration test file for module collaboration.
    
    This is an internal helper function used by generate_tests_from_spec.
    
    Args:
        spec: Full specification dictionary loaded from SPEC.yaml
        output_path: Path where the integration test file will be written
    """
    module_name = spec.get('module_name', 'unknown')
    interfaces = spec.get('interfaces', [])
    
    template = _jinja_env.from_string(INTEGRATION_TEST_TEMPLATE)
    content = template.render(
        module_name=module_name,
        interfaces=interfaces
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


# =============================================================================
# Legacy Class-Based API (for backward compatibility)
# =============================================================================

class TestGenerator:
    """
    Legacy class-based test generator.
    
    This class is maintained for backward compatibility.
    New code should use the module-level functions directly.
    """
    
    def __init__(self, spec_path: str):
        self.spec_path = Path(spec_path)
        self.spec = None
    
    def load_spec(self) -> bool:
        """Load specification from YAML"""
        try:
            with open(self.spec_path, 'r', encoding='utf-8') as f:
                self.spec = yaml.safe_load(f)
            return True
        except Exception as e:
            print(f"Error loading spec: {e}")
            return False
    
    def generate_unit_tests(self) -> str:
        """Generate unit test file content (legacy - all interfaces in one file)"""
        if not self.spec:
            raise ValueError("Specification not loaded")
        
        interfaces = self.spec.get('interfaces', [])
        all_content = []
        
        for interface in interfaces:
            interface_name = interface.get('name', 'unknown')
            output_file = f"/tmp/test_{interface_name.lower()}.py"
            generate_unit_test(interface, output_file)
            with open(output_file, 'r') as f:
                all_content.append(f.read())
        
        return '\n\n'.join(all_content)
    
    def generate_acceptance_tests(self) -> str:
        """Generate acceptance test file content from scenarios (legacy)"""
        if not self.spec:
            raise ValueError("Specification not loaded")
        
        scenarios = self.spec.get('scenarios', [])
        if not scenarios:
            return "# No scenarios defined in SPEC.yaml\n"
        
        all_content = []
        for scenario in scenarios:
            scenario_id = scenario.get('id', 'unknown')
            output_file = f"/tmp/test_{_slugify(scenario_id)}.py"
            generate_acceptance_test(scenario, output_file)
            with open(output_file, 'r') as f:
                all_content.append(f.read())
        
        return '\n\n'.join(all_content)
    
    def write_tests(self, output_dir: str) -> List[str]:
        """
        Write generated tests to files (legacy method).
        
        Returns:
            List of generated file paths
        """
        result = generate_tests_from_spec(str(self.spec_path), output_dir)
        return result.get('test_files', [])


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """CLI entry point for test generation"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python test_generator.py <spec.yaml> <output_dir>")
        print("\nGenerates test files from SPEC.yaml:")
        print("  - tests/unit/test_{interface}.py       # Unit tests")
        print("  - tests/integration/test_{module}_collaboration.py  # Integration tests")
        print("  - tests/acceptance/test_{scenario}.py  # Acceptance tests")
        print("  - tests/conftest.py                    # Shared fixtures")
        sys.exit(1)
    
    spec_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    print(f"📄 Loading specification: {spec_path}")
    result = generate_tests_from_spec(spec_path, output_dir)
    
    if result['status'] == 'error':
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)
    
    print(f"\n✅ Test generation complete!")
    print(f"   Generated {result['total_tests']} test cases in {len(result['test_files'])} files")
    print(f"\n📁 Generated files:")
    for f in result['test_files']:
        print(f"   - {f}")


if __name__ == "__main__":
    main()
