# Micro-benchmarks: OCaml vs Python Backend (MIG-INF-004)

This document explains how to run simple HTTP micro-benchmarks to compare the legacy OCaml `gwd` server with the Python proxy backend.

## What This Measures

- Baseline page load (home)
- Person page (database lookup + rendering)
- Search operation

For each endpoint, the script records N request times, then reports: avg, median, p95, p99.

## Requirements

- GeneWeb binaries available under `GeneWeb/gw/` (gwd, etc.)
- Test base available under `GeneWeb/bases/test.gwb/`
- Python virtual environment with dependencies installed

## Run

```bash
# Activate venv (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# From project root
python -m python_app.benchmarks.benchmark_runner
```

Environment variables:

| Variable | Default | Description |
|---|---|---|
| `GENEWEB_BASE` | `test` | Base name |
| `OCAML_GWD_PORT` | `2317` | OCaml `gwd` port |
| `FLASK_PORT` | `23181` | Python Flask port for the benchmark run |
| `BENCH_ITERS` | `25` | Iterations per endpoint |
| `BENCH_TIMEOUT` | `4.0` | Request timeout (seconds) |

## Output

Results are written to:

- `python_app/benchmarks/results/ocaml_results.json`
- `python_app/benchmarks/results/python_results.json`

Example JSON for one endpoint:
```json
{
  "home": {
    "count": 25,
    "avg": 0.135,
    "median": 0.128,
    "p95": 0.189,
    "p99": 0.202,
    "samples": [ ... ]
  }
}
```

## Notes & Best Practices

- Benchmarks complement golden tests (correctness). They track performance.
- Use p95/p99 percentiles to account for outliers.
- Run on a quiet machine for stable numbers; warm-up is implicit across iterations.
- The script automatically starts `gwd` and the Flask app (for Python backend) and shuts them down after.

## CI Integration (Blocking on Regression)

CI automatically runs benchmarks with reduced iterations (`BENCH_ITERS=5`) and **blocks merges** if a performance regression is detected.

**Regression Detection:**
- Compares Python backend avg response time vs OCaml backend
- **Threshold**: Python can be up to 50% slower than OCaml (configurable via `BENCH_REGRESSION_THRESHOLD`)
- If Python exceeds threshold, CI fails with error messages

**Why This Blocks:**
- Detects if migrated Python functions cause significant performance degradation
- Ensures migration doesn't introduce unacceptable slowdowns
- Threshold of 50% accounts for proxy overhead while catching real regressions

**Configuration:**
- `BENCH_ITERS=5` in CI (fast, reduced accuracy)
- `BENCH_REGRESSION_THRESHOLD=50.0` (50% max slowdown)
- Can be adjusted per environment if needed
