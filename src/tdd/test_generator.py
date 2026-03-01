"""Test Generator for TDD workflow.

This module generates pytest tests from SPEC.yaml specifications using Jinja2 templates.
"""

import os
import re
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, PackageLoader, BaseLoader, Template


@dataclass
class GeneratedTest:
    """Represents a generated test file."""
    file_path: str
    content: str
    requirement_id: str
    scenario_name: str
    test_type: str


class TestGenerator:
    """Generates tests from SPEC.yaml specifications using Jinja2 templates."""
    
    def __init__(self, template_dir: Optional[str] = None):
        """Initialize the test generator.
        
        Args:
            template_dir: Optional custom template directory. If not provided,
                         uses the built-in templates.
        """
        self.template_dir = template_dir
        self.env = self._create_jinja_env()
    
    def _create_jinja_env(self) -> Environment:
        """Create Jinja2 environment with appropriate loader."""
        if self.template_dir and os.path.exists(self.template_dir):
            loader = FileSystemLoader(self.template_dir)
        else:
            # Use built-in templates from package
            try:
                loader = PackageLoader('tdd', 'templates')
            except:
                # Fallback: use templates relative to this file
                template_path = Path(__file__).parent / 'templates'
                loader = FileSystemLoader(str(template_path))
        
        env = Environment(
            loader=loader,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # Add custom filters
        env.filters['snake_case'] = self._to_snake_case
        env.filters['title_case'] = self._to_title_case
        
        return env
    
    def _to_snake_case(self, name: str) -> str:
        """Convert a name to snake_case."""
        s = re.sub(r'[-\s]+', '_', name)
        s = re.sub(r'[^\w_]', '', s)
        s = s.lower()
        s = s.strip('_')
        return s or 'unnamed'
    
    def _to_title_case(self, name: str) -> str:
        """Convert a name to TitleCase."""
        snake = self._to_snake_case(name)
        return ''.join(word.capitalize() for word in snake.split('_'))
    
    def generate_from_spec(self, spec_path: str, output_dir: str) -> dict:
        """Generate complete test suite from SPEC.yaml.
        
        Args:
            spec_path: Path to SPEC.yaml file
            output_dir: Directory to write generated tests
            
        Returns:
            Dictionary with generation results including:
            - status: 'success' or 'error'
            - generated_files: List of generated file paths
            - requirements_count: Number of requirements processed
            - scenarios_count: Number of scenarios processed
            - message: Human-readable summary
        """
        result = {
            "status": "success",
            "spec_path": spec_path,
            "output_dir": output_dir,
            "generated_files": [],
            "requirements_count": 0,
            "scenarios_count": 0,
            "errors": []
        }
        
        try:
            # Parse SPEC.yaml
            with open(spec_path, 'r') as f:
                spec = yaml.safe_load(f)
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Extract specification info
            spec_info = spec.get('specification', {})
            spec_name = spec_info.get('name', 'Unknown')
            module_name = self._to_snake_case(spec_name)
            timestamp = datetime.now().isoformat()
            
            # Get requirements
            requirements = spec.get('requirements', [])
            result["requirements_count"] = len(requirements)
            
            # Generate unit tests for each requirement
            all_acceptance_scenarios = []
            
            for req in requirements:
                req_id = req.get('id', 'REQ')
                scenarios = req.get('scenarios', [])
                result["scenarios_count"] += len(scenarios)
                
                # Generate unit test file
                unit_test_content = self.generate_unit_test(
                    requirement=req,
                    module_name=module_name,
                    timestamp=timestamp
                )
                
                test_filename = f"test_{self._to_snake_case(req_id)}.py"
                test_path = os.path.join(output_dir, test_filename)
                
                with open(test_path, 'w') as f:
                    f.write(unit_test_content)
                
                result["generated_files"].append(test_path)
                
                # Collect acceptance test scenarios
                for scenario in scenarios:
                    all_acceptance_scenarios.append({
                        'requirement_id': req_id,
                        'name': scenario.get('name', 'unnamed'),
                        'given': scenario.get('given', ''),
                        'when': scenario.get('when', ''),
                        'then': scenario.get('then', '')
                    })
            
            # Generate acceptance tests file if there are scenarios
            if all_acceptance_scenarios:
                acc_content = self.generate_acceptance_test(
                    spec_name=spec_name,
                    scenarios=all_acceptance_scenarios,
                    module_name=module_name,
                    timestamp=timestamp
                )
                acc_path = os.path.join(output_dir, "test_acceptance.py")
                with open(acc_path, 'w') as f:
                    f.write(acc_content)
                result["generated_files"].append(acc_path)
            
            # Generate integration tests file
            if requirements:
                int_content = self.generate_integration_test(
                    spec_name=spec_name,
                    requirements=requirements,
                    module_name=module_name,
                    timestamp=timestamp
                )
                int_path = os.path.join(output_dir, "test_integration.py")
                with open(int_path, 'w') as f:
                    f.write(int_content)
                result["generated_files"].append(int_path)
            
            # Generate __init__.py if needed
            init_path = os.path.join(output_dir, "__init__.py")
            if not os.path.exists(init_path):
                with open(init_path, 'w') as f:
                    f.write("# Auto-generated test package\n")
                result["generated_files"].append(init_path)
            
            result["message"] = f"Generated {len(result['generated_files'])} test files"
            
        except FileNotFoundError:
            result["status"] = "error"
            result["errors"].append(f"Spec file not found: {spec_path}")
        except yaml.YAMLError as e:
            result["status"] = "error"
            result["errors"].append(f"Invalid YAML in spec: {e}")
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"Error generating tests: {str(e)}")
        
        return result
    
    def generate_unit_test(self, requirement: dict, module_name: str, 
                           timestamp: Optional[str] = None) -> str:
        """Generate pytest unit test from requirement using template.
        
        Args:
            requirement: Requirement dictionary from SPEC.yaml
            module_name: Name of the module being tested
            timestamp: Optional timestamp string
            
        Returns:
            Generated test code as string
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        template = self.env.get_template('pytest_unit.j2')
        
        scenarios = requirement.get('scenarios', [])
        
        return template.render(
            requirement=requirement,
            scenarios=scenarios,
            module_name=module_name,
            timestamp=timestamp
        )
    
    def generate_acceptance_test(self, spec_name: str, scenarios: List[dict],
                                  module_name: str, 
                                  timestamp: Optional[str] = None) -> str:
        """Generate acceptance test from GIVEN-WHEN-THEN scenarios using template.
        
        Args:
            spec_name: Name of the specification
            scenarios: List of scenario dictionaries
            module_name: Name of the module being tested
            timestamp: Optional timestamp string
            
        Returns:
            Generated test code as string
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        template = self.env.get_template('pytest_acceptance.j2')
        
        return template.render(
            spec_name=spec_name,
            scenarios=scenarios,
            module_name=module_name,
            timestamp=timestamp
        )
    
    def generate_integration_test(self, spec_name: str, requirements: List[dict],
                                   module_name: str,
                                   timestamp: Optional[str] = None) -> str:
        """Generate integration test from requirements using template.
        
        Args:
            spec_name: Name of the specification
            requirements: List of requirement dictionaries
            module_name: Name of the module being tested
            timestamp: Optional timestamp string
            
        Returns:
            Generated test code as string
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        template = self.env.get_template('pytest_integration.j2')
        
        return template.render(
            spec_name=spec_name,
            requirements=requirements,
            module_name=module_name,
            timestamp=timestamp
        )


# Legacy functions for backward compatibility
def generate_tests_from_spec(spec_path: str, output_dir: str) -> Dict[str, Any]:
    """Generate pytest tests from SPEC.yaml.
    
    This is a convenience function that creates a TestGenerator instance
    and calls generate_from_spec.
    
    Args:
        spec_path: Path to SPEC.yaml file
        output_dir: Directory to write generated tests
        
    Returns:
        Dictionary with generation results
    """
    generator = TestGenerator()
    return generator.generate_from_spec(spec_path, output_dir)


def generate_unit_test(requirement: Dict[str, Any], module_name: str) -> str:
    """Generate single unit test from requirement.
    
    Legacy function for backward compatibility.
    
    Args:
        requirement: Requirement dictionary from SPEC.yaml
        module_name: Name of the module being tested
        
    Returns:
        Generated test code as string
    """
    generator = TestGenerator()
    return generator.generate_unit_test(requirement, module_name)


def generate_acceptance_test(requirement: Dict[str, Any], 
                             scenario: Dict[str, Any],
                             module_name: str) -> Optional[str]:
    """Generate acceptance test from GIVEN-WHEN-THEN scenario.
    
    Legacy function for backward compatibility. Note: This function
    now returns a single scenario wrapped in a full test class.
    
    Args:
        requirement: Requirement dictionary
        scenario: Scenario dictionary with given/when/then
        module_name: Name of the module being tested
        
    Returns:
        Generated test code as string, or None if invalid scenario
    """
    given = scenario.get('given', '')
    when = scenario.get('when', '')
    then = scenario.get('then', '')
    
    if not all([given, when, then]):
        return None
    
    generator = TestGenerator()
    spec_name = requirement.get('id', 'Unknown')
    scenarios = [{
        'requirement_id': requirement.get('id', 'REQ'),
        'name': scenario.get('name', 'unnamed'),
        'given': given,
        'when': when,
        'then': then
    }]
    
    return generator.generate_acceptance_test(spec_name, scenarios, module_name)
