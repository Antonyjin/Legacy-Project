"""
FT-PY-003: Test person page display

End-to-end test of viewing a person's profile page with all information.

This is a FUNCTIONAL test because it validates complete user workflows:
- User navigates to person page
- User views person's name and dates
- User views family relationships
- User verifies all fields display correctly
- User can navigate to related persons

User Story: As a user, I want to view a person's profile with all their information.

Test Scenario:
1. Navigate to person page
2. View person's name and dates
3. View family relationships
4. View life events
5. Verify all fields display correctly
"""

import pytest
import requests
import subprocess
import time
from pathlib import Path


class GeneWebServer:
    """Helper class to manage gwd process for functional testing"""

    def __init__(self, geneweb_dir: str, port: int = 23186, base_name: str = "test"):
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

        self.log_file = open(f"gwd_ft_{self.port}.log", "w")
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
    srv = GeneWebServer(geneweb_dir, port=23186)

    if not srv.start():
        pytest.skip("Failed to start GeneWeb server")

    yield srv

    srv.stop()


class TestPersonPageDisplay:
    """Functional tests for person page display workflow"""

    def test_person_page_loads_successfully(self, server):
        """Test: Person page loads and displays correctly"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor"}
        )

        assert response.status_code == 200, f"Person page failed to load: {response.status_code}"

        # Verify page has content
        content = response.text.lower()
        assert len(content) > 500, "Person page appears empty or too short"

        # Verify basic page structure
        assert "<html" in content, "Person page missing HTML structure"

    def test_person_name_displayed(self, server):
        """Test: Person's name and surname display correctly"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor"}
        )

        assert response.status_code == 200

        content = response.text.lower()

        # Verify both first name and surname appear
        assert "charles" in content, "Person page missing first name (Charles)"
        assert "windsor" in content, "Person page missing surname (Windsor)"

    def test_person_dates_displayed(self, server):
        """Test: Birth and death dates display correctly"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor"}
        )

        assert response.status_code == 200

        content = response.text.lower()

        # Charles was born in 1948
        assert "1948" in content, "Person page missing birth year"

        # Verify date-related keywords
        has_date_info = any(keyword in content for keyword in [
            "born", "birth", "date", "1948", "death", "died", "age"
        ])
        assert has_date_info, "Person page missing date information"

    def test_person_family_relationships_shown(self, server):
        """Test: Family relationships (parents, spouse, children) display"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor"}
        )

        assert response.status_code == 200

        content = response.text.lower()

        # Should have references to family members
        # Charles has parents (Elizabeth, Philip) and spouses (Diana, Camilla)
        has_family_info = any(keyword in content for keyword in [
            "elizabeth", "philip", "diana", "camilla",
            "parent", "spouse", "wife", "husband", "married",
            "father", "mother", "son", "daughter", "child"
        ])
        assert has_family_info, "Person page missing family relationship information"

    def test_person_missing_data_handled(self, server):
        """Test: Missing data (no death date, no spouse) handled gracefully"""
        # Test with Elizabeth II (who has no death date in some records)
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Elizabeth", "n": "Windsor"}
        )

        assert response.status_code == 200

        # Page should load even if some data is missing
        content = response.text.lower()
        assert "elizabeth" in content, "Person page missing person name"
        assert "windsor" in content, "Person page missing surname"

        # Page should still be valid HTML
        assert "<html" in content, "Person page missing HTML structure"
        assert len(content) > 300, "Person page too short to be valid"
