#!/usr/bin/env bash
# Builds dist/PlayLive PayID Scanner.app. Must run on macOS -- PyInstaller
# does not cross-compile .app bundles from other platforms.
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ "$(uname)" != "Darwin" ]]; then
  echo "This must be run on macOS (it builds a .app bundle)." >&2
  exit 1
fi

if ! command -v brew >/dev/null; then
  echo "Homebrew is required (for tesseract). See https://brew.sh" >&2
  exit 1
fi

if ! brew list tesseract >/dev/null 2>&1; then
  echo "Installing tesseract via Homebrew..."
  brew install tesseract
fi

TESS_PREFIX="$(brew --prefix tesseract)"
export TESSERACT_BIN="$TESS_PREFIX/bin/tesseract"
export TESSDATA_DIR="$TESS_PREFIX/share/tessdata"
export APP_VERSION="$(cat VERSION)"

if [[ ! -x "$TESSERACT_BIN" ]]; then
  echo "Could not find tesseract binary at $TESSERACT_BIN" >&2
  exit 1
fi

echo "Setting up build environment..."
python3 -m venv .venv-build
source .venv-build/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements-app.txt >/dev/null

echo "Building app bundle..."
rm -rf build dist
pyinstaller --noconfirm packaging/PlayLivePayIDScanner.spec

deactivate

echo ""
echo "Built: dist/PlayLive PayID Scanner.app"
echo "Next: ./scripts/build_pkg.sh to create an installer .pkg"
