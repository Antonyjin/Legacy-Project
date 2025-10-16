#!/bin/sh
set -eu

# Golden Master Test Harness
# Captures GEDCOM export and HTML pages from legacy GeneWeb for regression testing.
# Usage: run_golden.sh [create|validate]

MODE=${1:-validate}

ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
GENEWEB_DIR="$ROOT_DIR/GeneWeb"
BASE_DIR="$GENEWEB_DIR/bases"

OUT_DIR="$ROOT_DIR/tests/golden"
GOLD_DIR="$OUT_DIR/goldens/v1"
REP_DIR="$OUT_DIR/reports"
TMP_DIR="$OUT_DIR/tmp"

mkdir -p "$GOLD_DIR" "$REP_DIR" "$TMP_DIR"

export LC_ALL=C.UTF-8
export TZ=UTC

# Detect which base to use (prefer test.gwb, fallback to base.gwb)
BASE_NAME=""
if [ -d "$BASE_DIR/test.gwb" ]; then
  BASE_NAME="test"
elif [ -d "$BASE_DIR/base.gwb" ]; then
  BASE_NAME="base"
else
  echo "ERROR: No test.gwb or base.gwb found in $BASE_DIR"
  exit 1
fi

EXPORT_BASE_PATH="$BASE_DIR/${BASE_NAME}.gwb"

# Sanity checks
if [ ! -x "$GENEWEB_DIR/gw/gwb2ged" ]; then
  echo "ERROR: Missing executable $GENEWEB_DIR/gw/gwb2ged"
  exit 1
fi
if [ ! -x "$GENEWEB_DIR/gw/gwd" ]; then
  echo "ERROR: Missing executable $GENEWEB_DIR/gw/gwd"
  exit 1
fi

echo "==> Using base: $BASE_NAME"

# ============================================================================
# 1) Export GEDCOM from existing base
# ============================================================================
EXPORT_RAW="$TMP_DIR/export.ged"
EXPORT_NORM="$TMP_DIR/export.ged.norm"

echo "==> Exporting GEDCOM from $EXPORT_BASE_PATH..."
"$GENEWEB_DIR/gw/gwb2ged" "$EXPORT_BASE_PATH" -o "$EXPORT_RAW"

# Normalize GEDCOM (drop timestamps, trim trailing spaces)
sed -E 's/^(1 DATE|2 TIME) .*/\1 <normalized>/g' "$EXPORT_RAW" | \
  sed -E 's/[[:space:]]+$//g' > "$EXPORT_NORM"

# ============================================================================
# 2) Start gwd and fetch HTML pages
# ============================================================================
PORT=23179
echo "==> Starting gwd on port $PORT..."
"$GENEWEB_DIR/gw/gwd" -hd "$GENEWEB_DIR/gw" -bd "$BASE_DIR" -p "$PORT" -lang en \
  > "$TMP_DIR/gwd.out" 2>&1 &
GWD_PID=$!

# Wait for gwd to be ready
sleep 3

# Verify gwd is running
if ! kill -0 "$GWD_PID" 2>/dev/null; then
  echo "ERROR: gwd failed to start. Log:"
  cat "$TMP_DIR/gwd.out"
  exit 1
fi

# Define routes to snapshot (name::path relative to base)
# GeneWeb serves pages under: http://localhost:PORT/BASE_NAME/path
ROUTES="
home::
home_fr::?lang=fr
person_charles::?p=Charles&n=Windsor
family_charles::?m=F&p=charles&n=windsor
calendar::?m=CAL
firstnames::?m=P
surnames::?m=N
statistics::?m=STAT
descendants_elizabeth::?m=D&p=Elizabeth&n=Windsor
"
# Note: Relationship page (?m=C or ?m=REL) requires Sosa reference configuration
# See docs/Issues/ISSUE_85_SKIPPED.md for details

DIFF_FILE="$REP_DIR/diff.txt"
if [ "$MODE" != "create" ]; then
  rm -f "$DIFF_FILE"
fi

echo "$ROUTES" | while IFS= read -r item; do
  [ -z "$item" ] && continue
  
  name=$(echo "$item" | cut -d: -f1)
  path=$(echo "$item" | cut -d: -f3-)
  
  RAW="$TMP_DIR/${name}.html"
  NORM="$TMP_DIR/${name}.html.norm"
  
  # Build URL: http://localhost:PORT/BASE_NAME[?path]
  if [ -z "$path" ]; then
    URL="http://localhost:$PORT/$BASE_NAME"
  else
    # path already contains ? if needed, just append
    URL="http://localhost:$PORT/$BASE_NAME$path"
  fi
  
  echo "  Fetching: $URL"
  
  set +e
  curl -sf "$URL" -o "$RAW" 2>/dev/null
  CURL_RC=$?
  set -e
  
  if [ $CURL_RC -ne 0 ]; then
    echo "ERROR: Failed to fetch $URL (curl exit code: $CURL_RC)"
    echo "==> gwd log tail:"
    tail -n 50 "$TMP_DIR/gwd.out" || true
    kill "$GWD_PID" 2>/dev/null || true
    exit 1
  fi
  
  # Normalize HTML (trim trailing spaces, collapse multiple spaces, remove volatile data)
  # First: convert non-breaking spaces to regular spaces
  sed 's/\xC2\xA0/ /g' "$RAW" | \
    # Then: collapse multiple spaces and trim trailing
    sed -E 's/[[:space:]]+$//g; s/[[:space:]]{2,}/ /g' | \
    # Normalize whitespace after &#010; entities
    sed -E 's/&#010; +/\&#010; /g' | \
    sed -E 's/\?i=[0-9]+/?i=RANDOM/g; s/\&i=[0-9]+/\&i=RANDOM/g' | \
    sed -E 's/var q_time = [0-9.]+;/var q_time = TIME;/g' | \
    sed -E 's/fa-dice-[a-z]+/fa-dice-RANDOM/g' | \
    # Mask age computations that vary day-to-day
    sed -E 's/=[[:space:]]*[0-9,]+ days old/= AGE_DAYS old/g' | \
    sed -E 's/[0-9]+ years, [0-9]+ months, [0-9]+ days old/AGE_YMD old/g' | \
    # Mask ages in tooltips (after &#010; normalization)
    sed -E 's/&#010; [0-9,]+ years/\&#010; AGE_YEARS years/g' | \
    # Mask timestamps in calendar page header (only in h3 tags, not HTML comments)
    sed -E 's/(<h3[^>]*>[^<]+ - )[0-9]{2}:[0-9]{2}:[0-9]{2}/\1HH:MM:SS/g' > "$NORM"
  
  if [ "$MODE" = "create" ]; then
    cp "$NORM" "$GOLD_DIR/expected_${name}.html.norm"
    echo "  Created golden: expected_${name}.html.norm"
  else
    if [ ! -f "$GOLD_DIR/expected_${name}.html.norm" ]; then
      echo "ERROR: Missing golden reference: expected_${name}.html.norm"
      kill "$GWD_PID" 2>/dev/null || true
      exit 1
    fi
    diff -u "$GOLD_DIR/expected_${name}.html.norm" "$NORM" >> "$DIFF_FILE" 2>/dev/null || true
  fi
done

# Stop gwd
kill "$GWD_PID" 2>/dev/null || true
wait "$GWD_PID" 2>/dev/null || true

# ============================================================================
# 3) Compare results
# ============================================================================
if [ "$MODE" = "create" ]; then
  cp "$EXPORT_NORM" "$GOLD_DIR/expected_export.ged.norm"
  echo "==> Golden references created under $GOLD_DIR"
  echo "==> Files created:"
  ls -lh "$GOLD_DIR"
  exit 0
fi

# Validate mode: also diff export
diff -u "$GOLD_DIR/expected_export.ged.norm" "$EXPORT_NORM" >> "$DIFF_FILE" 2>/dev/null || true

if [ -s "$DIFF_FILE" ]; then
  echo "==> Golden test FAILED. Differences found:"
  head -n 100 "$DIFF_FILE"
  echo "==> Full diff saved to: $DIFF_FILE"
  exit 1
else
  echo "==> Golden test PASSED. All outputs match references."
  rm -f "$DIFF_FILE"
fi
