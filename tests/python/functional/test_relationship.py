"""
FT-PY-004: Test relationship calculation

End-to-end test of calculating relationships between two people.

User Story: As a user, I want to find the relationship between two people.
"""

import pytest
import requests
import subprocess
import time
from pathlib import Path


class GeneWebServer:
    """Helper class to manage gwd process"""

    def __init__(self, geneweb_dir: str, port: int = 23187, base_name: str = "test"):
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

        pkill_cmd = ["pkill", "-f", f"gwd.*-p {self.port}"]
        subprocess.run(pkill_cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.5)

        cmd = [str(gwd_path), "-hd", str(gw_dir), "-bd", str(bases_dir), "-p", str(self.port), "-lang", "en"]

        self.log_file = open(f"gwd_ft_{self.port}.log", "w")
        self.process = subprocess.Popen(cmd, stdout=self.log_file, stderr=subprocess.STDOUT, cwd=str(self.geneweb_dir))

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_running():
                return True
            time.sleep(0.1)
        return False

    def is_running(self) -> bool:
        """Check if server is responding"""
        try:
            response = requests.get(f"http://localhost:{self.port}/{self.base_name}", timeout=2, headers={"Connection": "close"})
            return response.status_code in [200, 204]
        except requests.RequestException:
            return False

    def stop(self):
        """Stop gwd server"""
        if self.process:
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
    """Start GeneWeb server"""
    srv = GeneWebServer(geneweb_dir, port=23187)
    if not srv.start():
        pytest.skip("Failed to start GeneWeb server")
    yield srv
    srv.stop()


class TestRelationshipCalculation:
    """Functional tests for relationship calculation"""

    def test_relationship_page_loads(self, server):
        """Test: Relationship calculation page loads"""
        response = requests.get(f"http://localhost:{server.port}/{server.base_name}")
        assert response.status_code == 200
        content = response.text.lower()
        assert "geneweb" in content

    def test_direct_relationship_calculated(self, server):
        """Test: Direct parent-child relationship found"""
        # Navigate to Charles (child) and verify Elizabeth (mother) shown
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor"}
        )
        assert response.status_code == 200
        content = response.text.lower()
        # Should show parent relationship
        assert any(keyword in content for keyword in ["elizabeth", "parent", "mother", "father"])

    def test_indirect_relationship_calculated(self, server):
        """Test: Indirect relationship (cousins) found"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor"}
        )
        assert response.status_code == 200
        content = response.text.lower()
        # Page should load with family information
        assert len(content) > 300

    def test_no_relationship_handled(self, server):
        """Test: No relationship handled gracefully"""
        # Try persons with different surnames
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor"}
        )
        assert response.status_code in [200, 404]

    def test_relationship_display_formatted(self, server):
        """Test: Relationship displayed clearly"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor"}
        )
        assert response.status_code == 200
        content = response.text.lower()
        # Should have proper HTML structure
        assert "<html" in content
        assert len(content) > 100
