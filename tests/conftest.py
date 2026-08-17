"""
Pytest configuration and shared fixtures
"""

import pytest
import os
import sys

# Add the project root to the path so imports work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root path"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
