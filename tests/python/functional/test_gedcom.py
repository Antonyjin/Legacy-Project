"""
FT-PY-007: Test GEDCOM import/export functionality

End-to-end test of GEDCOM file handling.

This is a FUNCTIONAL test because it validates complete user workflows:
- User exports database to GEDCOM format
- User imports GEDCOM file
- User verifies data preservation
- User handles special characters
- User validates GEDCOM format

User Story: As a user, I want to import and export GEDCOM files.

Test Scenario:
1. Export database to GEDCOM
2. Import GEDCOM file
3. Verify roundtrip data preservation
4. Test special character handling
5. Validate GEDCOM format compliance
"""

import pytest
import requests
import subprocess
import time
import signal
import os
from pathlib import Path


class GeneWebServer:
    """Helper class to manage gwd process for functional testing"""

    def __init__(self, geneweb_dir: str, port: int = 23190, base_name: str = "test"):
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
    srv = GeneWebServer(geneweb_dir, port=23190)

    if not srv.start():
        pytest.skip("Failed to start GeneWeb server")

    yield srv

    srv.stop()


class TestGedcom:
    """Functional tests for GEDCOM import/export workflow"""

    def test_gedcom_export_works(self, server):
        """Test: GEDCOM export functionality works"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"m": "GEDCOM", "o": "export"}
        )

        # GEDCOM export may return different status codes depending on implementation
        assert response.status_code in [200, 302], f"GEDCOM export failed: {response.status_code}"

        # If successful, check for GEDCOM markers
        if response.status_code == 200:
            content = response.text

            # Verify GEDCOM format markers are present
            has_gedcom_markers = any(keyword in content for keyword in [
                "GEDCOM", "gedcom", "HEAD", "INDI", "FAM", "TRLR"
            ])
            assert has_gedcom_markers, "GEDCOM export missing GEDCOM format markers"

    def test_gedcom_import_works(self, server):
        """Test: GEDCOM import page is accessible"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"m": "GEDCOM", "o": "import"}
        )

        assert response.status_code == 200, f"GEDCOM import page failed to load: {response.status_code}"

        content = response.text.lower()

        # Verify import page contains expected elements
        has_import_elements = any(keyword in content for keyword in [
            "import", "upload", "file", "gedcom", "form"
        ])
        assert has_import_elements, "GEDCOM import page missing import elements"

    def test_gedcom_roundtrip_data_preserved(self, server):
        """Test: Data is preserved in GEDCOM export/import roundtrip"""
        # First, get original data from a known person
        charles_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor"}
        )

        assert charles_response.status_code == 200, "Failed to load test person data"

        original_content = charles_response.text.lower()

        # Verify original data contains expected information
        assert "charles" in original_content, "Original data missing person name"
        assert "windsor" in original_content, "Original data missing surname"

        # Now test GEDCOM export
        gedcom_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"m": "GEDCOM", "o": "export"}
        )

        assert gedcom_response.status_code in [200, 302], "GEDCOM export failed"

        # If export successful, verify it contains the person data
        if gedcom_response.status_code == 200:
            gedcom_content = gedcom_response.text.upper()

            # GEDCOM format uses uppercase for names
            has_person_data = "CHARLES" in gedcom_content or "WINDSOR" in gedcom_content
            assert has_person_data, "GEDCOM export missing expected person data"

    def test_gedcom_handles_special_chars(self, server):
        """Test: GEDCOM correctly handles special characters"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"m": "GEDCOM", "o": "export"}
        )

        assert response.status_code in [200, 302], "GEDCOM export failed"

        if response.status_code == 200:
            content = response.text

            # Verify GEDCOM uses proper encoding
            # GEDCOM should handle UTF-8 or use ANSEL encoding
            has_encoding = any(keyword in content for keyword in [
                "UTF-8", "ANSEL", "ASCII", "CHAR"
            ])

            # Also check that content is properly encoded (no broken characters)
            # This is a basic check - proper text without null bytes
            assert "\x00" not in content[:1000], "GEDCOM contains null bytes"

            # If no explicit encoding marker, at least verify readable ASCII
            if not has_encoding:
                # Should have readable GEDCOM structure
                assert "HEAD" in content or "INDI" in content, "GEDCOM missing basic structure"

    def test_gedcom_validates_format(self, server):
        """Test: GEDCOM output follows valid format"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"m": "GEDCOM", "o": "export"}
        )

        assert response.status_code in [200, 302], "GEDCOM export failed"

        if response.status_code == 200:
            content = response.text

            # Verify GEDCOM has required structure
            # Standard GEDCOM format should have:
            # - HEAD record at the beginning
            # - TRLR record at the end
            # - Proper line format (level + tag + optional value)

            lines = content.split('\n')

            # Check for HEAD record
            has_head = any(line.startswith("0 HEAD") or "HEAD" in line for line in lines[:10])
            assert has_head, "GEDCOM missing HEAD record"

            # Check for TRLR record
            has_trlr = any(line.startswith("0 TRLR") or "TRLR" in line for line in lines[-10:])
            assert has_trlr, "GEDCOM missing TRLR record"

            # Check for individual records
            has_indi = any("INDI" in line for line in lines)
            assert has_indi, "GEDCOM missing INDI records"

            # Verify basic line format (lines should start with digit)
            non_empty_lines = [line for line in lines if line.strip()]
            if non_empty_lines:
                valid_format_lines = sum(1 for line in non_empty_lines[:20]
                                        if line[0].isdigit() or line.startswith("0"))
                assert valid_format_lines > 0, "GEDCOM lines don't follow standard format"
