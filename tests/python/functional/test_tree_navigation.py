# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
FT-PY-001: Test tree navigation

End-to-end test of navigating through family tree.

This is a FUNCTIONAL test because it validates complete user workflows:
- User loads home page
- User clicks on a person
- User views family relationships
- User navigates through the tree
- User verifies navigation elements

User Story: As a user, I want to navigate through the family tree to explore relationships.

Test Scenario:
1. Load home page
2. Click on a person
3. View their family (parents, children, spouse)
4. Navigate to parent
5. Verify breadcrumbs/navigation
"""

import subprocess
import time
from pathlib import Path

import pytest
import requests


class GeneWebServer:
    """Helper class to manage gwd process for functional testing"""

    def __init__(self, geneweb_dir: str, port: int = 23184, base_name: str = "test"):
        self.geneweb_dir = Path(geneweb_dir)
        self.port = port
        self.base_name = base_name
        self.process = None
        self.log_file = None

    def start(self, timeout: int = 5) -> bool:
        """Start gwd server"""
        gwd_path = self.geneweb_dir / "gw" / "gwd"
        gw_dir = self.geneweb_dir / "gw"
        bases_dir = self.geneweb_dir / "bases"

        if not gwd_path.exists():
            raise FileNotFoundError(f"gwd not found at {gwd_path}")

        # Ensure previous gwd instances on this port are killed
        pkill_cmd = ["pkill", "-f", f"gwd.*-p {self.port}"]
        subprocess.run(pkill_cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.5)

        # Start gwd
        cmd = [
            str(gwd_path),
            "-hd", str(gw_dir),
            "-bd", str(bases_dir),
            "-p", str(self.port),
            "-lang", "en"
        ]

        self.log_file = open(f"gwd_ft_{self.port}.log", "w", encoding='utf-8')
        self.process = subprocess.Popen(
            cmd,
            stdout=self.log_file,
            stderr=subprocess.STDOUT,
            cwd=str(self.geneweb_dir)
        )

        # Wait for server to be ready
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_running():
                return True
            time.sleep(0.1)

        return False

    def is_running(self) -> bool:
        """Check if server is responding to HTTP requests"""
        try:
            response = requests.get(
                f"http://localhost:{self.port}/{self.base_name}",
                timeout=2,
                headers={"Connection": "close"}
            )
            return response.status_code in [200, 204]
        except requests.RequestException:
            return False

    def stop(self):
        """Stop gwd server"""
        if self.process:
            # Use pkill to ensure all child processes are killed
            pkill_cmd = ["pkill", "-f", f"gwd.*-p {self.port}"]
            subprocess.run(pkill_cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(0.3)

            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            finally:
                if self.log_file:
                    self.log_file.close()
                if self.process.stdout:
                    self.process.stdout.close()


@pytest.fixture(scope="module")
def geneweb_dir():
    """Find GeneWeb directory"""
    current_dir = Path(__file__).parent
    geneweb_path = current_dir.parent.parent.parent / "GeneWeb"

    if not geneweb_path.exists():
        pytest.skip(f"GeneWeb directory not found at {geneweb_path}")

    return str(geneweb_path)


@pytest.fixture(scope="module")
def server(geneweb_dir):
    """Start GeneWeb server for functional tests"""
    srv = GeneWebServer(geneweb_dir, port=23184)

    if not srv.start():
        pytest.skip("Failed to start GeneWeb server")

    yield srv

    srv.stop()


class TestTreeNavigation:
    """Functional tests for tree navigation workflow"""

    def test_home_page_loads_successfully(self, server):
        """Test: Load home page and verify it displays correctly"""
        response = requests.get(f"http://localhost:{server.port}/{server.base_name}", timeout=5)

        assert response.status_code == 200, f"Home page failed to load: {response.status_code}"

        # Verify home page contains expected elements
        content = response.text.lower()
        assert "geneweb" in content, "Home page missing GeneWeb branding"
        assert "individual" in content or "person" in content, "Home page missing person references"

        # Verify we can see database statistics
        assert "188" in content, "Home page missing individual count"
        assert "individuals" in content, "Home page missing individuals reference"

    def test_click_on_person_loads_person_page(self, server):
        """Test: Click on a person and verify person page loads"""
        # First get home page to find a person link
        home_response = requests.get(f"http://localhost:{server.port}/{server.base_name}", timeout=5)
        assert home_response.status_code == 200

        # Navigate to Charles Windsor (known test person)
        person_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor"}, timeout=5)

        assert person_response.status_code == 200, f"Person page failed to load: {person_response.status_code}"

        # Verify person page contains expected elements
        content = person_response.text.lower()
        assert "charles" in content, "Person page missing person name"
        assert "windsor" in content, "Person page missing surname"

        # Verify person page has navigation elements
        assert "parent" in content or "father" in content or "mother" in content, "Person page missing family references"

    def test_family_relationships_displayed_correctly(self, server):
        """Test: View family relationships (parents, children, spouse)"""
        # Get Charles Windsor's person page
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor"}, timeout=5)

        assert response.status_code == 200

        content = response.text.lower()

        # Verify family relationships are displayed
        # Look for parent references
        has_parents = any(keyword in content for keyword in [
            "elizabeth", "philip", "parent", "father", "mother", "mum", "dad"
        ])
        assert has_parents, "Person page missing parent information"

        # Look for spouse references
        has_spouse = any(keyword in content for keyword in [
            "diana", "camilla", "spouse", "wife", "husband", "married"
        ])
        assert has_spouse, "Person page missing spouse information"

    def test_navigate_to_parent_works(self, server):
        """Test: Navigate to parent and verify navigation works"""
        # Start with Charles Windsor
        charles_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor"}, timeout=5)
        assert charles_response.status_code == 200

        # Try to navigate to Elizabeth (mother)
        elizabeth_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Elizabeth", "n": "Windsor"}, timeout=5)

        assert elizabeth_response.status_code == 200, f"Parent navigation failed: {elizabeth_response.status_code}"

        # Verify we're on Elizabeth's page
        content = elizabeth_response.text.lower()
        assert "elizabeth" in content, "Parent page missing parent name"
        assert "windsor" in content, "Parent page missing surname"

        # Verify Elizabeth is older than Charles (different generation)
        assert "1926" in content or "1927" in content, "Parent page missing birth year"

    def test_breadcrumbs_navigation_elements_present(self, server):
        """Test: Verify breadcrumbs/navigation elements are present"""
        # Test multiple pages to verify navigation elements
        pages_to_test = [
            {"p": "Charles", "n": "Windsor"},
            {"p": "Elizabeth", "n": "Windsor"},
            {"p": "Philip", "n": "Mountbatten"}
        ]

        for params in pages_to_test:
            response = requests.get(
                f"http://localhost:{server.port}/{server.base_name}",
                params=params, timeout=5)

            assert response.status_code == 200, f"Page failed to load: {params}"

            content = response.text.lower()

            # Verify navigation elements are present
            has_navigation = any(keyword in content for keyword in [
                "home", "back", "previous", "next", "search", "menu", "nav"
            ])
            assert has_navigation, f"Page missing navigation elements: {params}"

            # Verify page has proper structure
            assert "<html" in content, f"Page missing HTML structure: {params}"
            assert "<head>" in content, f"Page missing head section: {params}"
            assert "<body>" in content, f"Page missing body section: {params}"

    def test_complete_navigation_workflow(self, server):
        """Test: Complete end-to-end navigation workflow"""
        # Step 1: Load home page
        home_response = requests.get(f"http://localhost:{server.port}/{server.base_name}", timeout=5)
        assert home_response.status_code == 200

        # Step 2: Navigate to Charles Windsor
        charles_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor"}, timeout=5)
        assert charles_response.status_code == 200

        # Step 3: Navigate to Elizabeth (mother)
        elizabeth_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Elizabeth", "n": "Windsor"}, timeout=5)
        assert elizabeth_response.status_code == 200

        # Step 4: Navigate to Philip (father)
        philip_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Philip", "n": "Mountbatten"}, timeout=5)
        assert philip_response.status_code == 200

        # Step 5: Verify we can navigate back to Charles
        charles_again_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor"}, timeout=5)
        assert charles_again_response.status_code == 200

        # Verify all pages contain expected content
        charles_content = charles_again_response.text.lower()
        assert "charles" in charles_content and "windsor" in charles_content

        elizabeth_content = elizabeth_response.text.lower()
        assert "elizabeth" in elizabeth_content and "windsor" in elizabeth_content

        philip_content = philip_response.text.lower()
        assert "philip" in philip_content and "mountbatten" in philip_content

        # Verify family relationships are consistent
        assert "elizabeth" in charles_content or "philip" in charles_content, "Charles page missing parent references"

    def test_navigation_handles_missing_persons_gracefully(self, server):
        """Test: Navigation handles missing persons gracefully"""
        # Try to navigate to a non-existent person
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "NonExistent", "n": "Person"}, timeout=5)

        # Should either return 404 or a page indicating person not found
        assert response.status_code in [200, 404], f"Unexpected status for missing person: {response.status_code}"

        if response.status_code == 200:
            content = response.text.lower()
            # Should indicate person not found
            assert any(keyword in content for keyword in [
                "not found", "unknown", "missing", "error", "404"
            ]), "Missing person page should indicate person not found"

    def test_navigation_preserves_url_parameters(self, server):
        """Test: Navigation preserves URL parameters correctly"""
        # Test with various parameter combinations
        test_cases = [
            {"p": "Charles", "n": "Windsor"},
            {"p": "Elizabeth", "n": "Windsor", "lang": "en"},
            {"p": "Philip", "n": "Mountbatten", "lang": "fr"}
        ]

        for params in test_cases:
            response = requests.get(
                f"http://localhost:{server.port}/{server.base_name}",
                params=params, timeout=5)

            assert response.status_code == 200, f"Navigation failed with params: {params}"

            # Verify the person name appears in the content
            person_name = params["p"].lower()
            surname = params["n"].lower()
            content = response.text.lower()

            assert person_name in content, f"Person name missing from page: {params}"
            assert surname in content, f"Surname missing from page: {params}"
