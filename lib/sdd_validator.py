"""
SDD Specification Validator
Validates SPEC.yaml files against the TDD+SDD schema
"""
import yaml
from typing import List, Dict, Any, Tuple
from pathlib import Path


class SDDValidator:
    """Validates SDD specification files"""
    
    REQUIRED_TOP_LEVEL = [
        "spec_version",
        "module_name", 
        "description",
        "interfaces"
    ]
    
    REQUIRED_INTERFACE_FIELDS = [
        "name",
        "type",
        "methods"
    ]
    
    REQUIRED_METHOD_FIELDS = [
        "name",
        "signature",
        "description"
    ]
    
    def __init__(self, spec_path: str):
        self.spec_path = Path(spec_path)
        self.spec = None
        self.errors = []
        self.warnings = []
    
    def load(self) -> bool:
        """Load and parse SPEC.yaml"""
        try:
            with open(self.spec_path, 'r', encoding='utf-8') as f:
                self.spec = yaml.safe_load(f)
            return True
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parsing error: {e}")
            return False
        except FileNotFoundError:
            self.errors.append(f"File not found: {self.spec_path}")
            return False
    
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate the specification
        
        Returns:
            (is_valid, errors, warnings)
        """
        if self.spec is None:
            if not self.load():
                return False, self.errors, self.warnings
        
        self._validate_top_level()
        self._validate_interfaces()
        self._validate_scenarios()
        self._validate_acceptance_criteria()
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _validate_top_level(self):
        """Validate top-level required fields"""
        for field in self.REQUIRED_TOP_LEVEL:
            if field not in self.spec:
                self.errors.append(f"Missing required field: {field}")
    
    def _validate_interfaces(self):
        """Validate interface definitions"""
        if "interfaces" not in self.spec:
            return
        
        interfaces = self.spec["interfaces"]
        if not isinstance(interfaces, list):
            self.errors.append("'interfaces' must be a list")
            return
        
        for idx, interface in enumerate(interfaces):
            self._validate_interface(interface, idx)
    
    def _validate_interface(self, interface: Dict, idx: int):
        """Validate a single interface"""
        prefix = f"Interface[{idx}]"
        
        for field in self.REQUIRED_INTERFACE_FIELDS:
            if field not in interface:
                self.errors.append(f"{prefix}: Missing required field '{field}'")
        
        if "methods" in interface:
            if not isinstance(interface["methods"], list):
                self.errors.append(f"{prefix}: 'methods' must be a list")
            else:
                for m_idx, method in enumerate(interface["methods"]):
                    self._validate_method(method, prefix, m_idx)
    
    def _validate_method(self, method: Dict, prefix: str, idx: int):
        """Validate a single method"""
        m_prefix = f"{prefix}.Method[{idx}]"
        
        for field in self.REQUIRED_METHOD_FIELDS:
            if field not in method:
                self.errors.append(f"{m_prefix}: Missing required field '{field}'")
        
        # Validate test_cases if present
        if "test_cases" in method:
            if not isinstance(method["test_cases"], list):
                self.warnings.append(f"{m_prefix}: 'test_cases' should be a list")
    
    def _validate_scenarios(self):
        """Validate scenario definitions"""
        if "scenarios" not in self.spec:
            self.warnings.append("No 'scenarios' defined (optional but recommended)")
            return
        
        scenarios = self.spec["scenarios"]
        if not isinstance(scenarios, list):
            self.errors.append("'scenarios' must be a list")
            return
        
        for idx, scenario in enumerate(scenarios):
            self._validate_scenario(scenario, idx)
    
    def _validate_scenario(self, scenario: Dict, idx: int):
        """Validate a single scenario"""
        prefix = f"Scenario[{idx}]"
        
        required = ["id", "name", "given", "when", "then"]
        for field in required:
            if field not in scenario:
                self.errors.append(f"{prefix}: Missing required field '{field}'")
    
    def _validate_acceptance_criteria(self):
        """Validate acceptance criteria"""
        if "acceptance_criteria" not in self.spec:
            self.warnings.append("No 'acceptance_criteria' defined (optional but recommended)")
            return
        
        criteria = self.spec["acceptance_criteria"]
        if not isinstance(criteria, dict):
            self.errors.append("'acceptance_criteria' must be a dictionary")


def validate_spec(spec_path: str) -> Tuple[bool, List[str], List[str]]:
    """
    Quick validation function
    
    Usage:
        is_valid, errors, warnings = validate_spec("SPEC.yaml")
    """
    validator = SDDValidator(spec_path)
    return validator.validate()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python sdd_validator.py <spec.yaml>")
        sys.exit(1)
    
    spec_path = sys.argv[1]
    is_valid, errors, warnings = validate_spec(spec_path)
    
    print(f"\n{'='*60}")
    print(f"SPEC Validation: {spec_path}")
    print(f"{'='*60}")
    print(f"Status: {'✅ VALID' if is_valid else '❌ INVALID'}")
    
    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")
    
    if is_valid and not warnings:
        print("\n✅ Specification is valid!")
    
    sys.exit(0 if is_valid else 1)
