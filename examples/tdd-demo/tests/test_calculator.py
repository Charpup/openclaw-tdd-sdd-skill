"""Tests for Calculator implementation.

Generated from SPEC.yaml using TDD workflow.
"""

import pytest
from calculator import Calculator


class TestCALC001:
    """Tests for CALC-001: Calculator can add two numbers"""
    
    def test_add_positive_numbers(self):
        """
        add positive numbers
        
        Given: two positive numbers 2 and 3
        When: add method is called
        Then: result should be 5
        """
        # Arrange
        calc = Calculator()
        
        # Act
        result = calc.add(2, 3)
        
        # Assert
        assert result == 5
    
    def test_add_negative_numbers(self):
        """
        add negative numbers
        
        Given: two negative numbers -2 and -3
        When: add method is called
        Then: result should be -5
        """
        # Arrange
        calc = Calculator()
        
        # Act
        result = calc.add(-2, -3)
        
        # Assert
        assert result == -5
    
    def test_add_mixed_numbers(self):
        """
        add mixed numbers
        
        Given: one positive and one negative number 5 and -3
        When: add method is called
        Then: result should be 2
        """
        # Arrange
        calc = Calculator()
        
        # Act
        result = calc.add(5, -3)
        
        # Assert
        assert result == 2


class TestCALC002:
    """Tests for CALC-002: Calculator can subtract two numbers"""
    
    def test_subtract_positive_numbers(self):
        """
        subtract positive numbers
        
        Given: two numbers 5 and 3
        When: subtract method is called
        Then: result should be 2
        """
        # Arrange
        calc = Calculator()
        
        # Act
        result = calc.subtract(5, 3)
        
        # Assert
        assert result == 2


class TestCALC003:
    """Tests for CALC-003: Calculator can multiply two numbers"""
    
    def test_multiply_positive_numbers(self):
        """
        multiply positive numbers
        
        Given: two numbers 4 and 3
        When: multiply method is called
        Then: result should be 12
        """
        # Arrange
        calc = Calculator()
        
        # Act
        result = calc.multiply(4, 3)
        
        # Assert
        assert result == 12


class TestCALC004:
    """Tests for CALC-004: Calculator can divide two numbers"""
    
    def test_divide_positive_numbers(self):
        """
        divide positive numbers
        
        Given: two numbers 12 and 4
        When: divide method is called
        Then: result should be 3
        """
        # Arrange
        calc = Calculator()
        
        # Act
        result = calc.divide(12, 4)
        
        # Assert
        assert result == 3
    
    def test_divide_by_zero(self):
        """
        divide by zero
        
        Given: divisor is 0
        When: divide method is called
        Then: should raise ValueError
        """
        # Arrange
        calc = Calculator()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            calc.divide(10, 0)
