#!/bin/bash
# Quick test to verify Flask startup improvements work

set -e

cd "$(dirname "$0")"

echo "=== Quick Flask Startup Test ==="
echo ""
echo "This will test if Flask starts within the new timeout (24s max)"
echo ""

# Kill any existing processes on test ports
pkill -f "gwd.*-p 23179" 2>/dev/null || true
pkill -f "python.*python_app.*23182" 2>/dev/null || true
sleep 1

# Test 1: Start OCaml gwd
echo "1. Starting OCaml gwd on port 23179..."
cd GeneWeb
./gw/gwd -hd ./gw -bd ./bases -p 23179 -lang en > /tmp/gwd_test.log 2>&1 &
GWD_PID=$!
cd ..
sleep 3

# Check if gwd is up
if curl -s http://localhost:23179/test > /dev/null; then
    echo "   ✅ OCaml gwd is responding"
else
    echo "   ❌ OCaml gwd not responding"
    kill $GWD_PID 2>/dev/null || true
    exit 1
fi

# Test 2: Start Flask app in background and check if it starts within timeout
echo ""
echo "2. Starting Flask app (BACKEND=python) on port 23182..."
BACKEND=python FLASK_PORT=23182 GENEWEB_DIR=./GeneWeb OCAML_GWD_PORT=23179 \
    python3 -m python_app.app > /tmp/flask_test.log 2>&1 &
FLASK_PID=$!

echo "   Waiting for Flask to start (max 24s)..."
START_TIME=$(date +%s)
MAX_WAIT=24
SUCCESS=0

for i in $(seq 1 $MAX_WAIT); do
    if curl -s http://localhost:23182/health > /dev/null 2>&1; then
        ELAPSED=$(($(date +%s) - START_TIME))
        echo "   ✅ Flask started and responding after ${ELAPSED}s"
        SUCCESS=1
        break
    fi
    sleep 1
    if [ $((i % 5)) -eq 0 ]; then
        echo "   ⏳ Still waiting... (${i}s elapsed)"
    fi
done

if [ $SUCCESS -eq 0 ]; then
    echo "   ❌ Flask did not start within ${MAX_WAIT}s"
    echo "   Checking Flask output:"
    tail -20 /tmp/flask_test.log || echo "   (no output)"
    kill $FLASK_PID 2>/dev/null || true
    kill $GWD_PID 2>/dev/null || true
    exit 1
fi

# Test 3: Verify health endpoint
echo ""
echo "3. Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:23182/health)
if echo "$HEALTH_RESPONSE" | grep -q '"backend":"python"'; then
    echo "   ✅ Health endpoint works, backend is Python"
else
    echo "   ⚠️  Health endpoint response: $HEALTH_RESPONSE"
fi

# Cleanup
echo ""
echo "4. Cleaning up..."
kill $FLASK_PID 2>/dev/null || true
kill $GWD_PID 2>/dev/null || true
pkill -f "gwd.*-p 23179" 2>/dev/null || true
pkill -f "python.*python_app.*23182" 2>/dev/null || true
sleep 1

echo ""
echo "✅ Flask startup test passed!"
echo ""
echo "You can now run the full benchmark test:"
echo "  BENCH_ITERS=2 OCAML_GWD_PORT=23179 FLASK_PORT=23182 python3 -m python_app.benchmarks.benchmark_runner"

