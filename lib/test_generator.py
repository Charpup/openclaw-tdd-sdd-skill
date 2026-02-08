"""
Test Generator
Generates pytest test stubs from SPEC.yaml definitions
"""
import yaml
from pathlib import Path
from typing import Dict, List, Any
from jinja2 import Template


TEST_TEMPLATE = '''"""
Auto-generated tests for {{ module_name }}
Generated from SPEC.yaml by TDD+SDD Skill
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

{% for interface in interfaces %}
class Test{{ interface.name }}:
    """Tests for {{ interface.name }} - {{ interface.description or 'No description' }}"""
    
    {% for method in interface.methods %}
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
        {% for key, value in (tc.expected or {}).items() %}
        # assert result['{{ key }}'] == {{ value | repr }}
        {% endfor %}
        pytest.skip("Test not yet implemented")
    {% endfor %}
    {% endif %}
    {% endfor %}

{% endfor %}
'''


class TestGenerator:
    """Generates test files from SDD specifications"""
    
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
        """Generate unit test file content"""
        if not self.spec:
            raise ValueError("Specification not loaded")
        
        template = Template(TEST_TEMPLATE)
        return template.render(
            module_name=self.spec.get('module_name', 'unknown'),
            interfaces=self.spec.get('interfaces', [])
        )
    
    def generate_acceptance_tests(self) -> str:
        """Generate acceptance test file content from scenarios"""
        if not self.spec:
            raise ValueError("Specification not loaded")
        
        scenarios = self.spec.get('scenarios', [])
        if not scenarios:
            return "# No scenarios defined in SPEC.yaml\n"
        
        lines = [
            '"""',
            f"Acceptance tests for {self.spec.get('module_name', 'unknown')}",
            'TDD+SDD Dual Pyramid - Acceptance Layer',
            '"""',
            'import pytest',
            '',
            '',
        ]
        
        for scenario in scenarios:
            scenario_id = scenario.get('id', 'unknown')
            scenario_name = scenario.get('name', 'Unnamed scenario')
            
            lines.append(f'@pytest.mark.acceptance')
            lines.append(f'def test_{scenario_id.lower().replace("-", "_")}():')
            lines.append(f'    """')
            lines.append(f'    Scenario: {scenario_name} (SPEC: {scenario_id})')
            lines.append(f'    ')
            
            # Given
            lines.append(f'    Given:')
            for condition in scenario.get('given', []):
                lines.append(f'      - {condition.get("condition", "Unknown")}')
            
            # When
            lines.append(f'    When:')
            for action in scenario.get('when', []):
                lines.append(f'      - {action.get("action", "Unknown")}')
            
            # Then
            lines.append(f'    Then:')
            for expectation in scenario.get('then', []):
                lines.append(f'      - {expectation.get("expectation", "Unknown")}')
            
            lines.append(f'    """')
            lines.append(f'    # TODO: Implement E2E test')
            lines.append(f'    pytest.skip("Acceptance test not yet implemented")')
            lines.append('')
        
        return '\n'.join(lines)
    
    def write_tests(self, output_dir: str):
        """Write generated tests to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unit tests
        unit_tests = self.generate_unit_tests()
        unit_test_path = output_path / 'unit' / 'test_generated.py'
        unit_test_path.parent.mkdir(exist_ok=True)
        with open(unit_test_path, 'w', encoding='utf-8') as f:
            f.write(unit_tests)
        print(f"✅ Generated: {unit_test_path}")
        
        # Generate acceptance tests
        acceptance_tests = self.generate_acceptance_tests()
        acceptance_test_path = output_path / 'acceptance' / 'test_generated.py'
        acceptance_test_path.parent.mkdir(exist_ok=True)
        with open(acceptance_test_path, 'w', encoding='utf-8') as f:
            f.write(acceptance_tests)
        print(f"✅ Generated: {acceptance_test_path}")


def generate_tests_from_spec(spec_path: str, output_dir: str):
    """CLI entry point"""
    generator = TestGenerator(spec_path)
    
    if not generator.load_spec():
        print("❌ Failed to load specification")
        return False
    
    generator.write_tests(output_dir)
    print(f"\n✅ Test generation complete!")
    return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python test_generator.py <spec.yaml> <output_dir>")
        sys.exit(1)
    
    spec_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    success = generate_tests_from_spec(spec_path, output_dir)
    sys.exit(0 if success else 1)
