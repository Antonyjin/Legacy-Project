"""Test performance benchmarks via HTTP API."""
import requests
import pytest
import time

BASE_URL = "http://localhost:23179/test"

class TestPerformance:
    """Test performance characteristics"""

    def test_home_page_load_time(self):
        """Test home page loads in reasonable time"""
        start = time.time()
        r = requests.get(f"{BASE_URL}")
        elapsed = time.time() - start
        assert r.status_code == 200
        assert elapsed < 5.0

    def test_person_page_load_time(self):
        """Test person page loads quickly"""
        start = time.time()
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        elapsed = time.time() - start
        assert r.status_code == 200
        assert elapsed < 5.0

    def test_search_performance(self):
        """Test search completes quickly"""
        start = time.time()
        r = requests.get(f"{BASE_URL}?m=S&s=Windsor")
        elapsed = time.time() - start
        assert r.status_code == 200
        assert elapsed < 5.0

    def test_family_page_load_time(self):
        """Test family page loads quickly"""
        start = time.time()
        r = requests.get(f"{BASE_URL}?m=F&p=Charles&n=Windsor")
        elapsed = time.time() - start
        assert r.status_code == 200
        assert elapsed < 5.0

    def test_calendar_load_time(self):
        """Test calendar loads quickly"""
        start = time.time()
        r = requests.get(f"{BASE_URL}?m=CAL")
        elapsed = time.time() - start
        assert r.status_code == 200
        assert elapsed < 5.0

    def test_statistics_load_time(self):
        """Test statistics loads quickly"""
        start = time.time()
        r = requests.get(f"{BASE_URL}?m=STAT")
        elapsed = time.time() - start
        assert r.status_code == 200
        assert elapsed < 5.0

    def test_sequential_requests_performance(self):
        """Test sequential requests maintain performance"""
        times = []
        for i in range(5):
            start = time.time()
            r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
            elapsed = time.time() - start
            times.append(elapsed)
            assert r.status_code == 200
        
        # Each request should be reasonably fast
        for t in times:
            assert t < 5.0

    def test_response_size_reasonable(self):
        """Test response sizes are reasonable"""
        r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
        assert r.status_code == 200
        # Response should be between 1KB and 1MB
        assert 1000 < len(r.text) < 1000000

    def test_concurrent_requests_handled(self):
        """Test handling of multiple requests"""
        import concurrent.futures
        
        def make_request():
            r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
            return r.status_code == 200
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(make_request, range(5)))
        
        # At least 80% should succeed (OCaml limitation)
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.8

    @pytest.mark.slow
    def test_many_sequential_requests(self):
        """Test handling of many sequential requests"""
        success = 0
        for i in range(20):
            r = requests.get(f"{BASE_URL}?p=Charles&n=Windsor")
            if r.status_code == 200:
                success += 1
        
        # All should succeed
        assert success == 20
