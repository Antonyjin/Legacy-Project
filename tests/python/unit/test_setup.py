# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
Test Setup: Verify pytest infrastructure is working correctly.

This is the first test to run - ensures everything is configured properly.

Issue: UT-PY-001 (Setup pytest infrastructure)
"""

import sys

import pytest


class TestPytestInfrastructure:
    """Test that pytest infrastructure is configured correctly"""

    def test_pytest_works(self):
        """Verify pytest is installed and working"""
        assert True

    def test_python_version(self):
        """Verify Python version is 3.7+"""
        assert sys.version_info >= (3, 7), f"Python 3.7+ required, got {sys.version}"

    def test_imports(self):
        """Verify required packages are installed"""
        # pytest already imported at module level
        try:
            # Verify pytest is accessible
            assert pytest is not None
        except NameError as e:
            pytest.fail(f"Missing required package: {e}")


class TestCoverageAvailable:
    """Test that coverage tools are available"""

    def test_coverage_importable(self):
        """Verify pytest-cov is installed"""
        try:
            import pytest_cov
            assert pytest_cov is not None
        except ImportError:
            pytest.fail("pytest-cov not installed - run: pip install pytest-cov")


class TestMarkersWork:
    """Test that custom markers are configured"""

    @pytest.mark.unit
    def test_unit_marker(self):
        """Verify @pytest.mark.unit works"""
        assert True

    @pytest.mark.integration
    def test_integration_marker(self):
        """Verify @pytest.mark.integration works"""
        assert True

    @pytest.mark.functional
    def test_functional_marker(self):
        """Verify @pytest.mark.functional works"""
        assert True

    @pytest.mark.slow
    def test_slow_marker(self):
        """Verify @pytest.mark.slow works"""
        assert True


if __name__ == "__main__":
    # Run this test file standalone
    pytest.main([__file__, "-v"])
