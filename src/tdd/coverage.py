"""Coverage Checker for TDD workflow.

This module analyzes test coverage and validates against thresholds.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


def _get_python_cmd() -> str:
    """Get the Python command to use."""
    return sys.executable


@dataclass
class FileCoverage:
    """Coverage information for a single file."""
    path: str
    percentage: float
    total_lines: int
    covered_lines: int
    missing_lines: List[int]


@dataclass
class CoverageReport:
    """Complete coverage report."""
    overall_percentage: float
    files: List[FileCoverage]
    threshold: float
    meets_threshold: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_percentage": self.overall_percentage,
            "threshold": self.threshold,
            "meets_threshold": self.meets_threshold,
            "files": [
                {
                    "path": f.path,
                    "percentage": f.percentage,
                    "total_lines": f.total_lines,
                    "covered_lines": f.covered_lines,
                    "missing_lines": f.missing_lines
                }
                for f in self.files
            ]
        }


class CoverageAnalyzer:
    """Analyzes test coverage."""
    
    def __init__(self, source_path: str = "."):
        self.source_path = Path(source_path)
    
    def check(self, test_path: str = ".", threshold: float = 80.0) -> CoverageReport:
        """Check coverage against threshold.
        
        Args:
            test_path: Path to tests (to run for coverage)
            threshold: Minimum coverage percentage required
            
        Returns:
            CoverageReport with results
        """
        result = check_coverage(str(self.source_path), test_path, threshold)
        
        files = []
        for file_data in result.get("files", []):
            files.append(FileCoverage(
                path=file_data.get("path", ""),
                percentage=file_data.get("percentage", 0.0),
                total_lines=file_data.get("total_lines", 0),
                covered_lines=file_data.get("covered_lines", 0),
                missing_lines=file_data.get("missing_lines", [])
            ))
        
        return CoverageReport(
            overall_percentage=result.get("coverage", 0.0),
            files=files,
            threshold=threshold,
            meets_threshold=result.get("meets_threshold", False)
        )
    
    def get_uncovered_lines(self, file_path: str) -> List[int]:
        """Get list of uncovered line numbers for a file.
        
        Args:
            file_path: Path to source file
            
        Returns:
            List of uncovered line numbers
        """
        report = self.check()
        
        for file_cov in report.files:
            if file_cov.path == file_path or file_cov.path.endswith(file_path):
                return file_cov.missing_lines
        
        return []


def check_coverage(source_path: str = ".", test_path: str = ".", threshold: float = 80.0) -> Dict[str, Any]:
    """Check if coverage meets threshold.
    
    This function:
    1. Runs tests with coverage
    2. Compares against threshold
    3. Returns pass/fail status
    
    Args:
        source_path: Path to source code
        test_path: Path to tests (to run for coverage)
        threshold: Minimum coverage percentage required
        
    Returns:
        Dictionary with coverage results
    """
    result = {
        "status": "unknown",
        "source_path": source_path,
        "threshold": threshold,
        "coverage": 0.0,
        "meets_threshold": False,
        "files": [],
        "output": "",
        "error": None
    }
    
    try:
        # Run with pytest-cov
        result = _check_coverage_with_pytest(source_path, test_path, threshold)
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result


def _check_coverage_with_pytest(source_path: str, test_path: str, threshold: float) -> Dict[str, Any]:
    """Check coverage using pytest-cov.
    
    Args:
        source_path: Path to source code
        test_path: Path to tests
        threshold: Minimum coverage percentage
        
    Returns:
        Dictionary with coverage results
    """
    python_cmd = _get_python_cmd()
    
    result = {
        "status": "unknown",
        "source_path": source_path,
        "threshold": threshold,
        "coverage": 0.0,
        "meets_threshold": False,
        "files": [],
        "output": "",
        "error": None
    }
    
    # Run pytest with coverage
    cmd = [
        python_cmd, "-m", "pytest",
        test_path,
        "--cov", source_path,
        "--cov-report", "term-missing",
        "-v"
    ]
    
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd() + ':' + env.get('PYTHONPATH', '')
    
    process = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        env=env
    )
    
    output = process.stdout + process.stderr
    result["output"] = output
    
    # Parse coverage from output
    parsed = _parse_coverage_output(output)
    result["coverage"] = parsed.get("overall", 0.0)
    result["files"] = parsed.get("files", [])
    result["meets_threshold"] = result["coverage"] >= threshold
    
    if result["meets_threshold"]:
        result["status"] = "pass"
    else:
        result["status"] = "fail"
    
    return result


def _parse_coverage_output(output: str) -> Dict[str, Any]:
    """Parse coverage report output.
    
    Args:
        output: Raw coverage output
        
    Returns:
        Dictionary with parsed coverage data
    """
    result = {
        "overall": 0.0,
        "files": []
    }
    
    lines = output.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Parse file lines
        # Format: "src/calculator.py      11      0   100%"
        # Format: "filename.py 50 40 10 80% 1-10, 20-30"
        file_match = re.match(r'^(\S+\.py)\s+(\d+)\s+(\d+)\s+(\d+)%\s*(.*)?$', line)
        if file_match and 'TOTAL' not in line.upper():
            file_data = {
                "path": file_match.group(1),
                "total_lines": int(file_match.group(2)),
                "covered_lines": int(file_match.group(2)) - int(file_match.group(3)),
                "missing_count": int(file_match.group(3)),
                "percentage": float(file_match.group(4)),
                "missing_lines_str": file_match.group(5) or ""
            }
            
            # Parse missing line numbers
            file_data["missing_lines"] = _parse_missing_lines(file_data["missing_lines_str"])
            
            result["files"].append(file_data)
        
        # Parse TOTAL line
        # Format: "TOTAL                  11      0   100%"
        total_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', line)
        if total_match:
            result["overall"] = float(total_match.group(1))
    
    return result


def _parse_missing_lines(missing_str: str) -> List[int]:
    """Parse missing line numbers from coverage output.
    
    Args:
        missing_str: String like "1-10, 15, 20-25"
        
    Returns:
        List of line numbers
    """
    lines = []
    
    if not missing_str:
        return lines
    
    parts = missing_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # Range like "1-10"
            try:
                start, end = part.split('-')
                lines.extend(range(int(start), int(end) + 1))
            except ValueError:
                pass
        else:
            # Single line
            try:
                lines.append(int(part))
            except ValueError:
                pass
    
    return sorted(lines)


def generate_coverage_report(source_path: str, output_format: str = "html") -> Dict[str, Any]:
    """Generate a coverage report in specified format.
    
    Args:
        source_path: Path to source code
        output_format: Report format (html, xml, json)
        
    Returns:
        Dictionary with report generation results
    """
    python_cmd = _get_python_cmd()
    
    result = {
        "status": "unknown",
        "source_path": source_path,
        "format": output_format,
        "output_path": None,
        "error": None
    }
    
    format_options = {
        "html": "html",
        "xml": "xml",
        "json": "json",
        "lcov": "lcov"
    }
    
    if output_format not in format_options:
        result["status"] = "error"
        result["error"] = f"Unsupported format: {output_format}"
        return result
    
    try:
        output_dir = f"coverage_{output_format}"
        
        cmd = [
            python_cmd, "-m", "coverage",
            format_options[output_format],
            "-d", output_dir
        ]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if process.returncode == 0:
            result["status"] = "success"
            result["output_path"] = output_dir
        else:
            result["status"] = "error"
            result["error"] = process.stderr
            
    except FileNotFoundError:
        result["status"] = "error"
        result["error"] = "Coverage not found. Install with: pip install coverage"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result


class CoverageChecker:
    """Checks test coverage against thresholds and generates reports."""
    
    def __init__(self, source_path: str = "."):
        """Initialize CoverageChecker.
        
        Args:
            source_path: Path to source code directory
        """
        self.source_path = source_path
    
    def check_coverage(self, threshold: float = 80.0) -> dict:
        """Check if coverage meets threshold.
        
        This method:
        1. Runs coverage analysis
        2. Compares against threshold
        3. Returns pass/fail status
        
        Args:
            threshold: Minimum coverage percentage required
            
        Returns:
            Dictionary with coverage results containing:
            - status: "pass" or "fail"
            - coverage: Overall coverage percentage
            - threshold: The threshold that was checked
            - meets_threshold: Boolean indicating if threshold was met
            - files: List of file coverage details
            - output: Raw coverage output
            - error: Error message if any
        """
        return check_coverage(self.source_path, threshold)
    
    def generate_coverage_report(self, output_path: str) -> dict:
        """Generate HTML coverage report.
        
        Args:
            output_path: Directory path where HTML report will be saved
            
        Returns:
            Dictionary with report generation results containing:
            - status: "success" or "error"
            - output_path: Path to generated report
            - error: Error message if any
        """
        result = {
            "status": "unknown",
            "output_path": None,
            "error": None
        }
        
        try:
            cmd = [
                "python", "-m", "coverage", "html",
                "-d", output_path
            ]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if process.returncode == 0:
                result["status"] = "success"
                result["output_path"] = output_path
            else:
                result["status"] = "error"
                result["error"] = process.stderr
                
        except FileNotFoundError:
            result["status"] = "error"
            result["error"] = "Coverage not found. Install with: pip install coverage"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
