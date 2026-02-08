"""
Unit tests for SDD Validator
"""
import pytest
import tempfile
from pathlib import Path

from lib.sdd_validator import SDDValidator, validate_spec


class TestSDDValidator:
    """Tests for SDDValidator class"""
    
    def test_load_valid_yaml(self):
        """TEST: Can load valid YAML file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
spec_version: "1.0"
module_name: "test_module"
description: "Test module"
interfaces: []
""")
            f.flush()
            
            validator = SDDValidator(f.name)
            assert validator.load() is True
            
            Path(f.name).unlink()
    
    def test_load_invalid_yaml(self):
        """TEST: Returns False for invalid YAML"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: [")
            f.flush()
            
            validator = SDDValidator(f.name)
            assert validator.load() is False
            assert len(validator.errors) > 0
            
            Path(f.name).unlink()
    
    def test_validate_missing_required_fields(self):
        """TEST: Detects missing required fields"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
spec_version: "1.0"
# Missing module_name and interfaces
""")
            f.flush()
            
            is_valid, errors, warnings = validate_spec(f.name)
            assert is_valid is False
            assert any("module_name" in e for e in errors)
            assert any("interfaces" in e for e in errors)
            
            Path(f.name).unlink()
    
    def test_validate_valid_spec(self):
        """TEST: Valid spec passes validation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
spec_version: "1.0"
module_name: "test_module"
description: "Test module"
interfaces:
  - name: "TestInterface"
    type: "class"
    methods:
      - name: "test_method"
        signature: "() -> None"
        description: "Test method"
""")
            f.flush()
            
            is_valid, errors, warnings = validate_spec(f.name)
            assert is_valid is True
            
            Path(f.name).unlink()


class TestValidateSpecFunction:
    """Tests for validate_spec convenience function"""
    
    def test_nonexistent_file(self):
        """TEST: Handles nonexistent file gracefully"""
        is_valid, errors, warnings = validate_spec("/nonexistent/spec.yaml")
        assert is_valid is False
        assert any("not found" in e.lower() for e in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
