#!/usr/bin/env bash
set -euo pipefail

# Only format these two trees
TARGETS=(python_app tests/python)
LINE_LEN=120

for d in "${TARGETS[@]}"; do
  [[ -e "$d" ]] || { echo "Missing target: $d" >&2; exit 1; }
done
echo "==> Targets: ${TARGETS[*]}"

# Create an isolated tools venv that is totally independent from your project's venv
TOOLS_VENV=".lintvenv"

# Prefer system Python to avoid pyenv-shimmed/broken pip; fall back to PATH python3
SYS_PY="/usr/bin/python3"
if [[ ! -x "$SYS_PY" ]]; then
  SYS_PY="$(command -v python3)"
fi
[[ -x "$SYS_PY" ]] || { echo "No python3 found" >&2; exit 1; }

if [[ ! -d "$TOOLS_VENV" ]]; then
  echo "==> Creating tools venv at $TOOLS_VENV using $SYS_PY"
  "$SYS_PY" -m venv "$TOOLS_VENV"
fi

# Activate the tools venv
# shellcheck disable=SC1091
source "$TOOLS_VENV/bin/activate"

echo "==> Tools Python: $(python -V) | pip: $(python -m pip -V || echo 'unavailable')"

# Try a trivial pip import to detect vendor corruption; if broken, re-bootstrap via ensurepip
python - <<'PY' || true
try:
    import pip  # noqa
    from pip._vendor import requests  # noqa
    from pip._internal.cli.main import main as _  # noqa
except Exception as e:
    import ensurepip
    ensurepip.bootstrap(upgrade=True)
PY

# Install compatible toolchain PINS (kept minimal)
echo "==> Installing code tools (black/isort/autoflake + click<9 for black)…"
python -m pip install --upgrade --no-input \
  "click>=8.0,<9.0" \
  "black==24.8.0" \
  "isort>=5.13,<6" \
  "autoflake>=2.3,<3"

echo "==> Running autoflake (remove unused imports/vars)…"
autoflake -r --in-place --remove-all-unused-imports --remove-unused-variables "${TARGETS[@]}"

echo "==> Running isort (organize imports)…"
isort --profile black --line-length "$LINE_LEN" "${TARGETS[@]}"

echo "==> Running black (format)…"
black --line-length "$LINE_LEN" "${TARGETS[@]}"

# Keep your existing .pylintrc if present; otherwise create a simple one
if [[ ! -f .pylintrc ]]; then
  cat > .pylintrc <<RC
[FORMAT]
max-line-length=${LINE_LEN}
[MESSAGES CONTROL]
enable=all
[MISCELLANEOUS]
notes=FIXME,XXX
RC
fi

echo "==> Done. You can now run:"
echo "    pylint python_app/ tests/python/"

