"""Tests for __init__.py - just a simple import test."""
import pytest


def test_backend_module_imports():
    """Test that backend module can be imported."""
    from backend import __init__ as backend_module
    assert backend_module is not None
