# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
Shared pytest configuration and fixtures for GeneWeb tests.

This file is automatically loaded by pytest and provides:
- Common fixtures (gwd connection, test data)
- Test markers
- Setup/teardown hooks
- Utilities

Issue: UT-PY-001 (Setup pytest infrastructure)
"""

import os
import time

import pytest
import requests

# =============================================================================
# Configuration
# =============================================================================

BASE_URL = os.getenv("GENEWEB_URL", "http://localhost:23179")
DATABASE = os.getenv("GENEWEB_DB", "test")
FULL_URL = f"{BASE_URL}/{DATABASE}"
TIMEOUT = int(os.getenv("GENEWEB_TIMEOUT", "5"))


# =============================================================================
# Session-level Fixtures
# =============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Setup test environment once for entire test session.
    Ensures deterministic behavior.
    """
    # Set deterministic environment
    os.environ["LC_ALL"] = "C.UTF-8"
    os.environ["TZ"] = "UTC"

    yield

    # Cleanup (if needed)


@pytest.fixture(scope="session")
def gwd_url() -> str:
    """Return the GeneWeb daemon URL"""
    return FULL_URL


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL (without database)"""
    return BASE_URL


@pytest.fixture(scope="session")
def database_name() -> str:
    """Return the database name"""
    return DATABASE


# =============================================================================
# Module-level Fixtures
# =============================================================================

@pytest.fixture(scope="module")
def check_gwd_running():
    """
    Check if gwd is running before running any tests in a module.
    Skip entire module if gwd is not accessible.
    """
    try:
        response = requests.get(FULL_URL, timeout=TIMEOUT)
        if response.status_code != 200:
            pytest.skip(f"gwd not accessible at {FULL_URL} (status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        pytest.skip(f"gwd not running at {FULL_URL}: {e}")


# =============================================================================
# Function-level Fixtures
# =============================================================================

@pytest.fixture
def http_client():
    """
    HTTP client for making requests to gwd.
    Automatically checks if gwd is running.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "GeneWeb-Python-Tests/1.0"
    })

    # Verify gwd is accessible
    try:
        response = session.get(FULL_URL, timeout=TIMEOUT)
        if response.status_code != 200:
            pytest.skip(f"gwd not accessible at {FULL_URL}")
    except requests.exceptions.RequestException:
        pytest.skip(f"gwd not running at {FULL_URL}")

    yield session

    session.close()


@pytest.fixture
def get_person(http_client):
    """
    Helper fixture to get a person page.

    Usage:
        def test_example(get_person):
            response = get_person("Charles", "Windsor")
            assert response.status_code == 200
    """
    def _get_person(firstname: str, surname: str, oc: int = None):
        params = {"p": firstname, "n": surname}
        if oc is not None:
            params["oc"] = oc
        return http_client.get(FULL_URL, params=params)

    return _get_person


@pytest.fixture
def search(http_client):
    """
    Helper fixture to perform a search.

    Usage:
        def test_example(search):
            response = search("Windsor")
            assert "Charles" in response.text
    """
    def _search(query: str):
        params = {"m": "S", "s": query}
        return http_client.get(FULL_URL, params=params)

    return _search


# =============================================================================
# Utility Functions (not fixtures, but useful)
# =============================================================================

def wait_for_gwd(max_attempts: int = 10, delay: float = 1.0) -> bool:
    """
    Wait for gwd to become available.

    Args:
        max_attempts: Maximum number of connection attempts
        delay: Delay between attempts in seconds

    Returns:
        True if gwd is available, False otherwise
    """
    for attempt in range(max_attempts):
        try:
            response = requests.get(FULL_URL, timeout=TIMEOUT)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass

        if attempt < max_attempts - 1:
            time.sleep(delay)

    return False


# =============================================================================
# Pytest Hooks
# =============================================================================

def pytest_configure(config):
    """
    Configure pytest with custom markers.
    """
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests (require gwd)")
    config.addinivalue_line("markers", "functional: Functional tests (end-to-end)")
    config.addinivalue_line("markers", "slow: Slow tests (>1 second)")
    config.addinivalue_line("markers", "skip_ci: Skip in CI environment")
    config.addinivalue_line("markers", "requires_gwd: Test requires gwd daemon running")


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection:
    - Add markers automatically based on test location
    - Skip tests if gwd is not running (for marked tests)
    """
    for item in items:
        # Auto-mark tests based on directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
            item.add_marker(pytest.mark.requires_gwd)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.requires_gwd)
        elif "functional" in str(item.fspath):
            item.add_marker(pytest.mark.functional)
            item.add_marker(pytest.mark.requires_gwd)


def pytest_report_header(config):
    """
    Add custom header to pytest output.
    """
    return [
        f"GeneWeb URL: {FULL_URL}",
        f"Database: {DATABASE}",
        f"Timeout: {TIMEOUT}s",
    ]
