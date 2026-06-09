"""Pytest fixtures placeholder.

Full async database fixtures will be implemented in Story 1.5a
when user authentication models are created.
"""

import pytest


@pytest.fixture
def sample_data() -> dict:
    """Basic fixture for unit tests."""
    return {"status": "ok"}
