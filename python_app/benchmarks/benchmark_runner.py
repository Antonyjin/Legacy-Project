import os
import json
import time
import signal
import subprocess
from pathlib import Path
from statistics import mean, median
from typing import Dict, List, Tuple

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GENEWEB_DIR = PROJECT_ROOT / "GeneWeb"

DEFAULT_BASE = os.getenv("GENEWEB_BASE", "test")
OCAML_PORT = int(os.getenv("OCAML_GWD_PORT", "2317"))
PY_PORT = int(os.getenv("FLASK_PORT", "23181"))
ITERATIONS = int(os.getenv("BENCH_ITERS", "25"))
TIMEOUT = float(os.getenv("BENCH_TIMEOUT", "4.0"))

RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def is_up(url: str, timeout: float = 1.0) -> bool:
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200
    except requests.RequestException:
        return False


def run_cmd(cmd: List[str]) -> subprocess.Popen:
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def start_gwd(port: int) -> subprocess.Popen:
    gwd = GENEWEB_DIR / "gw" / "gwd"
    gw_dir = GENEWEB_DIR / "gw"
    bases = GENEWEB_DIR / "bases"
    proc = run_cmd([str(gwd), "-hd", str(gw_dir), "-bd", str(bases), "-p", str(port), "-lang", "en"])
    # Wait ready
    base_url = f"http://localhost:{port}/{DEFAULT_BASE}"
    deadline = time.time() + 6.0
    while time.time() < deadline:
        if is_up(base_url):
            return proc
        time.sleep(0.2)
    raise RuntimeError("gwd did not become ready")


def stop_proc(proc: subprocess.Popen | None) -> None:
    if not proc:
        return
    try:
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=3)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def start_python_app(port: int, backend: str) -> subprocess.Popen:
    env = os.environ.copy()
    env["BACKEND"] = backend
    env["FLASK_PORT"] = str(port)
    env["GENEWEB_DIR"] = str(GENEWEB_DIR)
    env["OCAML_GWD_PORT"] = str(OCAML_PORT)  # Ensure Python backend knows OCaml port
    cmd = ["python", "-m", "python_app.app"]
    proc = subprocess.Popen(cmd, cwd=str(PROJECT_ROOT), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0)
    # Wait for Flask to start - give it time to initialize and bind to port
    base_url = f"http://localhost:{port}/health"
    # Initial delay for Flask to start (especially in CI where startup might be slower)
    time.sleep(2.0)
    deadline = time.time() + 15.0  # Increased timeout for CI (15s total: 2s initial + 13s retry)
    last_error = None
    while time.time() < deadline:
        # Check if process died
        if proc.poll() is not None:
            # Process exited, read output
            output = proc.stdout.read().decode('utf-8', errors='ignore') if proc.stdout else "No output"
            raise RuntimeError(f"Flask app exited unexpectedly (code {proc.returncode}). Output: {output[:500]}")
        try:
            r = requests.get(base_url, timeout=1.0)
            if r.status_code == 200:
                return proc
        except requests.RequestException as e:
            last_error = str(e)
        time.sleep(0.3)
    
    # Timeout - show error and output
    output = ""
    if proc.stdout:
        try:
            # Try to read what we can without blocking
            import select
            if hasattr(select, 'select') and select.select([proc.stdout], [], [], 0.1)[0]:
                output = proc.stdout.read(1000).decode('utf-8', errors='ignore')
        except (ImportError, OSError, AttributeError):
            # select not available (Windows) or other error - try direct read
            try:
                # Non-blocking read attempt
                import fcntl
                flags = fcntl.fcntl(proc.stdout, fcntl.F_GETFL)
                fcntl.fcntl(proc.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)
                output = proc.stdout.read(1000).decode('utf-8', errors='ignore')
            except (ImportError, OSError):
                # fcntl not available - try simple read
                pass
    
    error_msg = f"Flask app did not become ready after 10s (endpoint: {base_url})"
    if last_error:
        error_msg += f". Last error: {last_error}"
    if output:
        error_msg += f". Output: {output}"
    raise RuntimeError(error_msg)


def bench_endpoint(url: str, iterations: int) -> Dict[str, float | List[float]]:
    times: List[float] = []
    for _ in range(iterations):
        t0 = time.time()
        r = requests.get(url, timeout=TIMEOUT)
        elapsed = time.time() - t0
        if r.status_code == 200:
            times.append(elapsed)
        else:
            times.append(float("inf"))
    if not times:
        return {"count": 0, "avg": 0.0, "median": 0.0, "p95": 0.0, "p99": 0.0, "samples": []}
    sorted_times = sorted(times)
    n = len(sorted_times)
    def pct(p: float) -> float:
        k = min(n - 1, max(0, int(round(p * (n - 1)))))
        return sorted_times[k]
    return {
        "count": n,
        "avg": mean(sorted_times),
        "median": median(sorted_times),
        "p95": pct(0.95),
        "p99": pct(0.99),
        "samples": times,
    }


def check_regression(ocaml_results: Dict[str, Dict], py_results: Dict[str, Dict], threshold_pct: float = 50.0) -> Tuple[bool, List[str]]:
    """
    Check if Python backend has performance regressions vs OCaml.
    
    Args:
        ocaml_results: OCaml benchmark results
        py_results: Python benchmark results
        threshold_pct: Maximum acceptable slowdown percentage (default: 50%)
    
    Returns:
        (has_regression, error_messages)
    """
    errors: List[str] = []
    has_regression = False
    
    for name in ["home", "person", "search"]:
        o = ocaml_results.get(name, {})
        p = py_results.get(name, {})
        
        o_avg = o.get("avg", 0.0)
        p_avg = p.get("avg", 0.0)
        
        if o_avg == 0.0 or p_avg == 0.0:
            errors.append(f"{name}: Missing data (ocaml={o_avg:.4f}s, python={p_avg:.4f}s)")
            has_regression = True
            continue
        
        slowdown_pct = ((p_avg - o_avg) / o_avg) * 100.0
        
        if slowdown_pct > threshold_pct:
            errors.append(
                f"{name}: Python is {slowdown_pct:.1f}% slower than OCaml "
                f"(OCaml={o_avg:.4f}s, Python={p_avg:.4f}s, threshold={threshold_pct}%)"
            )
            has_regression = True
        elif slowdown_pct < -10.0:
            # Python is faster - log as info
            print(f"✅ {name}: Python is {abs(slowdown_pct):.1f}% faster than OCaml!")
    
    return has_regression, errors


def main() -> None:
    print("== GeneWeb Micro-benchmarks ==")
    print(f"Project: {PROJECT_ROOT}")
    print(f"Base: {DEFAULT_BASE}")
    print(f"Iterations: {ITERATIONS}")

    # Ensure gwd
    print("Starting gwd (OCaml)...")
    gwd_proc = start_gwd(OCAML_PORT)

    # Benchmark OCaml directly
    ocaml_base = f"http://localhost:{OCAML_PORT}/{DEFAULT_BASE}"
    ocaml_urls = {
        "home": f"{ocaml_base}",
        "person": f"{ocaml_base}?p=Charles&n=Windsor",
        "search": f"{ocaml_base}?m=S&v=charles",
    }
    print("Benchmarking OCaml gwd...")
    ocaml_results: Dict[str, Dict[str, float | List[float]]] = {}
    for name, url in ocaml_urls.items():
        ocaml_results[name] = bench_endpoint(url, ITERATIONS)

    (RESULTS_DIR / "ocaml_results.json").write_text(json.dumps(ocaml_results, indent=2))
    print("OCaml results saved to", RESULTS_DIR / "ocaml_results.json")

    # Start Python app (python backend)
    print("Starting Python proxy (BACKEND=python)...")
    py_proc = start_python_app(PY_PORT, backend="python")
    py_base = f"http://localhost:{PY_PORT}/{DEFAULT_BASE}"
    py_urls = {
        "home": f"{py_base}",
        "person": f"{py_base}?p=Charles&n=Windsor",
        "search": f"{py_base}?m=S&v=charles",
    }
    print("Benchmarking Python backend (proxy)...")
    py_results: Dict[str, Dict[str, float | List[float]]] = {}
    for name, url in py_urls.items():
        py_results[name] = bench_endpoint(url, ITERATIONS)

    (RESULTS_DIR / "python_results.json").write_text(json.dumps(py_results, indent=2))
    print("Python results saved to", RESULTS_DIR / "python_results.json")

    # Cleanup
    stop_proc(py_proc)
    stop_proc(gwd_proc)

    print("\nSummary (avg, median, p95):")
    for name in ["home", "person", "search"]:
        o = ocaml_results.get(name, {})
        p = py_results.get(name, {})
        o_avg = o.get("avg", 0.0)
        p_avg = p.get("avg", 0.0)
        slowdown_pct = ((p_avg - o_avg) / o_avg * 100.0) if o_avg > 0 else 0.0
        print(
            f"- {name:6}  OCaml: avg={o_avg:.4f}s med={o.get('median', 0.0):.4f}s p95={o.get('p95', 0.0):.4f}s  |  "
            f"Python: avg={p_avg:.4f}s med={p.get('median', 0.0):.4f}s p95={p.get('p95', 0.0):.4f}s  "
            f"({slowdown_pct:+.1f}%)"
        )
    
    # Check for regressions (blocking in CI)
    threshold_pct = float(os.getenv("BENCH_REGRESSION_THRESHOLD", "50.0"))
    has_regression, errors = check_regression(ocaml_results, py_results, threshold_pct)
    
    if has_regression:
        print("\n❌ PERFORMANCE REGRESSION DETECTED:")
        for err in errors:
            print(f"  - {err}")
        print(f"\nThreshold: {threshold_pct}% maximum slowdown acceptable")
        print("This indicates migrated Python functions are causing significant performance degradation.")
        exit(1)
    else:
        print("\n✅ No performance regression detected (Python backend is within acceptable limits)")


if __name__ == "__main__":
    main()
