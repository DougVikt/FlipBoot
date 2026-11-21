"""Tests for FlipBoot."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from flipboot import __version__


def test_version():
    """Test that version is set correctly."""
    assert __version__ == "0.1.0-alpha"


def test_imports():
    """Test that all modules can be imported."""
    from flipboot import detector
    from flipboot import security
    from flipboot import tool_checker
    from flipboot import ui
    assert detector is not None
    assert security is not None
    assert tool_checker is not None
    assert ui is not None