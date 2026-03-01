"""TDD State Tracker - Track TDD cycle progress.

This module provides persistent state tracking for TDD cycles,
allowing recovery and monitoring of TDD workflow progress.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict


@dataclass
class TDDStateRecord:
    """Record of a TDD state snapshot."""
    timestamp: str
    state: str
    spec_id: Optional[str] = None
    cycle_id: Optional[str] = None
    phase: Optional[str] = None
    test_count: int = 0
    pass_count: int = 0
    fail_count: int = 0
    coverage: float = 0.0
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class TDDStateTracker:
    """Track TDD cycle progress with persistent storage."""
    
    STATE_DIR = ".tdd"
    STATE_FILE = "state.json"
    HISTORY_FILE = "history.json"
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.state_dir = self.project_path / self.STATE_DIR
    
    def _ensure_state_dir(self):
        """Ensure the state directory exists."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_state_path(self) -> Path:
        """Get the path to the state file."""
        return self.state_dir / self.STATE_FILE
    
    def _get_history_path(self) -> Path:
        """Get the path to the history file."""
        return self.state_dir / self.HISTORY_FILE
    
    def save_state(self, project_path: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Save current TDD state to .tdd/state.json.
        
        Args:
            project_path: Path to the project directory
            state: Dictionary containing TDD state information
                Required keys:
                - state: Current TDD state (IDLE, RED, GREEN, REFACTOR, COMPLETE)
                Optional keys:
                - spec_id: Specification identifier
                - cycle_id: Cycle identifier
                - phase: Current phase name
                - test_count: Total number of tests
                - pass_count: Number of passing tests
                - fail_count: Number of failing tests
                - coverage: Code coverage percentage
                - notes: Additional notes
                - metadata: Any additional metadata
                
        Returns:
            Dictionary with save operation results
        """
        self.project_path = Path(project_path)
        self.state_dir = self.project_path / self.STATE_DIR
        
        result = {
            "status": "success",
            "saved": False,
            "path": str(self._get_state_path()),
            "timestamp": datetime.now().isoformat(),
            "message": ""
        }
        
        try:
            self._ensure_state_dir()
            
            # Create state record
            state_record = {
                "timestamp": result["timestamp"],
                "state": state.get("state", "IDLE"),
                "spec_id": state.get("spec_id"),
                "cycle_id": state.get("cycle_id"),
                "phase": state.get("phase"),
                "test_count": state.get("test_count", 0),
                "pass_count": state.get("pass_count", 0),
                "fail_count": state.get("fail_count", 0),
                "coverage": state.get("coverage", 0.0),
                "notes": state.get("notes", ""),
                "metadata": state.get("metadata", {})
            }
            
            # Save to state.json
            state_path = self._get_state_path()
            with open(state_path, 'w') as f:
                json.dump(state_record, f, indent=2)
            
            result["saved"] = True
            result["message"] = f"State saved to {state_path}"
            
            # Also append to history
            self._append_to_history(state_record)
            
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Error saving state: {str(e)}"
        
        return result
    
    def _append_to_history(self, state_record: Dict[str, Any]):
        """Append state record to history file.
        
        Args:
            state_record: The state record to append
        """
        history_path = self._get_history_path()
        
        # Load existing history
        history = []
        if history_path.exists():
            try:
                with open(history_path, 'r') as f:
                    history = json.load(f)
            except (json.JSONDecodeError, IOError):
                history = []
        
        # Append new record
        history.append(state_record)
        
        # Keep only last 100 records to prevent file bloat
        history = history[-100:]
        
        # Save history
        with open(history_path, 'w') as f:
            json.dump(history, f, indent=2)
    
    def load_state(self, project_path: str) -> Dict[str, Any]:
        """Load TDD state from .tdd/state.json.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Dictionary with loaded state information
            Returns default IDLE state if no state file exists
        """
        self.project_path = Path(project_path)
        self.state_dir = self.project_path / self.STATE_DIR
        
        result = {
            "status": "success",
            "loaded": False,
            "path": str(self._get_state_path()),
            "state": None,
            "message": ""
        }
        
        try:
            state_path = self._get_state_path()
            
            if not state_path.exists():
                result["message"] = "No state file found, returning default IDLE state"
                result["state"] = self._get_default_state()
                return result
            
            with open(state_path, 'r') as f:
                state_data = json.load(f)
            
            result["loaded"] = True
            result["state"] = state_data
            result["message"] = f"State loaded from {state_path}"
            
        except json.JSONDecodeError as e:
            result["status"] = "error"
            result["message"] = f"Invalid JSON in state file: {str(e)}"
            result["state"] = self._get_default_state()
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Error loading state: {str(e)}"
            result["state"] = self._get_default_state()
        
        return result
    
    def _get_default_state(self) -> Dict[str, Any]:
        """Get default IDLE state.
        
        Returns:
            Dictionary with default state values
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "state": "IDLE",
            "spec_id": None,
            "cycle_id": None,
            "phase": None,
            "test_count": 0,
            "pass_count": 0,
            "fail_count": 0,
            "coverage": 0.0,
            "notes": "",
            "metadata": {}
        }
    
    def get_history(self, project_path: str, limit: int = 10) -> Dict[str, Any]:
        """Get TDD state history.
        
        Args:
            project_path: Path to the project directory
            limit: Maximum number of history entries to return
            
        Returns:
            Dictionary with history entries
        """
        self.project_path = Path(project_path)
        self.state_dir = self.project_path / self.STATE_DIR
        
        result = {
            "status": "success",
            "loaded": False,
            "count": 0,
            "history": [],
            "message": ""
        }
        
        try:
            history_path = self._get_history_path()
            
            if not history_path.exists():
                result["message"] = "No history file found"
                return result
            
            with open(history_path, 'r') as f:
                history = json.load(f)
            
            # Return most recent entries first
            result["history"] = history[-limit:][::-1]
            result["count"] = len(result["history"])
            result["loaded"] = True
            result["message"] = f"Loaded {result['count']} history entries"
            
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Error loading history: {str(e)}"
        
        return result
    
    def clear_state(self, project_path: str, clear_history: bool = False) -> Dict[str, Any]:
        """Clear TDD state.
        
        Args:
            project_path: Path to the project directory
            clear_history: If True, also clear history file
            
        Returns:
            Dictionary with clear operation results
        """
        self.project_path = Path(project_path)
        self.state_dir = self.project_path / self.STATE_DIR
        
        result = {
            "status": "success",
            "cleared": False,
            "message": ""
        }
        
        try:
            state_path = self._get_state_path()
            
            if state_path.exists():
                state_path.unlink()
                result["cleared"] = True
                result["message"] = "State file cleared"
            else:
                result["message"] = "No state file to clear"
            
            if clear_history:
                history_path = self._get_history_path()
                if history_path.exists():
                    history_path.unlink()
                    result["message"] += ", history cleared"
            
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Error clearing state: {str(e)}"
        
        return result
    
    def update_state_field(self, project_path: str, field: str, value: Any) -> Dict[str, Any]:
        """Update a specific field in the current state.
        
        Args:
            project_path: Path to the project directory
            field: Field name to update
            value: New value for the field
            
        Returns:
            Dictionary with update operation results
        """
        # Load current state
        load_result = self.load_state(project_path)
        
        if load_result["status"] == "error" and load_result["state"] is None:
            return {
                "status": "error",
                "message": "Cannot load current state",
                "updated": False
            }
        
        state = load_result["state"] or self._get_default_state()
        
        # Update field
        valid_fields = ["state", "spec_id", "cycle_id", "phase", 
                       "test_count", "pass_count", "fail_count", 
                       "coverage", "notes", "metadata"]
        
        if field not in valid_fields:
            return {
                "status": "error",
                "message": f"Invalid field: {field}. Valid fields: {valid_fields}",
                "updated": False
            }
        
        state[field] = value
        state["timestamp"] = datetime.now().isoformat()
        
        # Save updated state
        return self.save_state(project_path, state)


# Convenience functions for direct usage
def save_tdd_state(project_path: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to save TDD state.
    
    Args:
        project_path: Path to the project directory
        state: Dictionary containing TDD state information
        
    Returns:
        Dictionary with save operation results
    """
    tracker = TDDStateTracker(project_path)
    return tracker.save_state(project_path, state)


def load_tdd_state(project_path: str) -> Dict[str, Any]:
    """Convenience function to load TDD state.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Dictionary with loaded state information
    """
    tracker = TDDStateTracker(project_path)
    return tracker.load_state(project_path)


def get_tdd_history(project_path: str, limit: int = 10) -> Dict[str, Any]:
    """Convenience function to get TDD history.
    
    Args:
        project_path: Path to the project directory
        limit: Maximum number of history entries to return
        
    Returns:
        Dictionary with history entries
    """
    tracker = TDDStateTracker(project_path)
    return tracker.get_history(project_path, limit)
