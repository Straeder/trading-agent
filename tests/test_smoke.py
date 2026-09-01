"""Smoke test: the scaffold imports and the test runner works."""

import execution
import riskengine


def test_packages_import() -> None:
    """Both packages exist and expose a docstring."""
    assert riskengine.__doc__ is not None
    assert execution.__doc__ is not None
