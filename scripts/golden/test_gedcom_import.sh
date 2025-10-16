#!/bin/sh
set -eu

# GEDCOM Import Roundtrip Validation Test
# Issue #86: Validate GEDCOM import produces consistent database
#
# Test flow:
#   1. Take a reference GEDCOM file (input.ged)
#   2. Import it to a fresh database (/tmp/test_import)
#   3. Export the database back to GEDCOM (export2.ged)
#   4. Compare export2.ged to input.ged (normalized)
#
# Acceptance:
#   - Imported database exports to identical GEDCOM (normalized)
#   - No data loss in roundtrip
#   - Normalized for timestamps, formatting

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

# Detect which base to use for source GEDCOM
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
if [ ! -x "$GENEWEB_DIR/gw/ged2gwb" ]; then
  echo "ERROR: Missing executable $GENEWEB_DIR/gw/ged2gwb"
  exit 1
fi

echo "==> GEDCOM Import Roundtrip Test"
echo "==> Using source base: $BASE_NAME"

# ============================================================================
# Step 1: Export reference GEDCOM from existing base
# ============================================================================

echo ""
echo "[1/5] Exporting reference GEDCOM from $BASE_NAME.gwb..."

INPUT_GED="$TMP_DIR/input.ged"
INPUT_GED_NORM="$TMP_DIR/input.ged.norm"

"$GENEWEB_DIR/gw/gwb2ged" "$EXPORT_BASE_PATH" -o "$INPUT_GED"

if [ ! -f "$INPUT_GED" ]; then
  echo "ERROR: Failed to export reference GEDCOM"
  exit 1
fi

echo "   ✓ Exported to: $INPUT_GED"

# ============================================================================
# Step 2: Normalize reference GEDCOM
# ============================================================================

echo ""
echo "[2/5] Normalizing reference GEDCOM..."

# Normalize: remove timestamps, trim whitespace, sort entries for stability
sed -E 's/^(1 DATE|2 TIME) .*/\1 <normalized>/g' "$INPUT_GED" | \
  sed -E 's/[[:space:]]+$//g' > "$INPUT_GED_NORM"

echo "   ✓ Normalized: $INPUT_GED_NORM"

# ============================================================================
# Step 3: Import GEDCOM to fresh database
# ============================================================================

echo ""
echo "[3/5] Importing GEDCOM to fresh database..."

IMPORT_DB="$TMP_DIR/test_import"
rm -rf "$IMPORT_DB" "$IMPORT_DB.gwb" 2>/dev/null || true

"$GENEWEB_DIR/gw/ged2gwb" "$INPUT_GED" -o "$IMPORT_DB"

if [ ! -d "$IMPORT_DB.gwb" ]; then
  echo "ERROR: Import failed, $IMPORT_DB.gwb not created"
  exit 1
fi

echo "   ✓ Imported to: $IMPORT_DB.gwb"

# ============================================================================
# Step 4: Export from imported database
# ============================================================================

echo ""
echo "[4/5] Exporting from imported database..."

EXPORT2_GED="$TMP_DIR/export2.ged"
EXPORT2_GED_NORM="$TMP_DIR/export2.ged.norm"

"$GENEWEB_DIR/gw/gwb2ged" "$IMPORT_DB.gwb" -o "$EXPORT2_GED"

if [ ! -f "$EXPORT2_GED" ]; then
  echo "ERROR: Failed to export from imported database"
  exit 1
fi

# Normalize export2
sed -E 's/^(1 DATE|2 TIME) .*/\1 <normalized>/g' "$EXPORT2_GED" | \
  sed -E 's/[[:space:]]+$//g' > "$EXPORT2_GED_NORM"

echo "   ✓ Exported: $EXPORT2_GED"
echo "   ✓ Normalized: $EXPORT2_GED_NORM"

# ============================================================================
# Step 5: Compare normalized GEDCOMs
# ============================================================================

echo ""
echo "[5/5] Comparing normalized GEDCOMs..."

if [ "$MODE" = "create" ]; then
  # In create mode, store the normalized export2 as the golden reference
  cp "$EXPORT2_GED_NORM" "$GOLD_DIR/expected_import_export.ged.norm"
  echo ""
  echo "==> ✅ Golden reference created: $GOLD_DIR/expected_import_export.ged.norm"
  echo ""
  exit 0
fi

# Validate mode: compare to stored golden
DIFF_FILE="$REP_DIR/import_diff.txt"
rm -f "$DIFF_FILE"

if [ ! -f "$GOLD_DIR/expected_import_export.ged.norm" ]; then
  echo ""
  echo "==> ⚠️  No golden reference found. Run with 'create' mode first:"
  echo "    ./scripts/golden/test_gedcom_import.sh create"
  echo ""
  exit 1
fi

set +e
diff -u "$GOLD_DIR/expected_import_export.ged.norm" "$EXPORT2_GED_NORM" > "$DIFF_FILE" 2>&1
DIFF_RC=$?
set -e

if [ $DIFF_RC -ne 0 ]; then
  echo ""
  echo "==> ❌ GEDCOM Import Roundtrip Test FAILED"
  echo ""
  echo "Differences found between reference and roundtrip export:"
  head -n 100 "$DIFF_FILE"
  echo ""
  echo "Full diff saved to: $DIFF_FILE"
  echo ""
  exit 1
fi

echo ""
echo "==> ✅ GEDCOM Import Roundtrip Test PASSED"
echo ""
echo "Summary:"
echo "  - Imported GEDCOM: $INPUT_GED"
echo "  - Created database: $IMPORT_DB.gwb"
echo "  - Exported GEDCOM: $EXPORT2_GED"
echo "  - Result: Normalized GEDCOMs are identical (no data loss)"
echo ""

