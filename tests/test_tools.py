
import sys
from pathlib import Path

# Add the directory containing tools.py to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = PROJECT_ROOT / "multi-tool-autonomous-agent"
sys.path.insert(0, str(CODE_DIR))

from tools import calculate, read_local_file


def test_calculate_multiplication():
    assert calculate("125 * 8") == "125 * 8 = 1000"


def test_calculate_subtraction():
    assert calculate("2026 - 2024") == "2026 - 2024 = 2"


def test_calculator_rejects_unsupported_expression():
    result = calculate("__import__('os').system('echo test')")
    assert result.startswith("Calculation failed:")


def test_read_project_notes():
    content = read_local_file("project_notes.txt")
    assert "compound research questions" in content


def test_reader_blocks_access_outside_workspace():
    result = read_local_file("../README.md")
    assert result == "Error: Access outside the workspace is not allowed."

