#!/usr/bin/env bash
# Wraps dist/PlayLive PayID Scanner.app into a double-click installer .pkg.
# Run ./scripts/build_app.sh first. Must run on macOS (uses pkgbuild).
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ "$(uname)" != "Darwin" ]]; then
  echo "This must be run on macOS (it uses pkgbuild)." >&2
  exit 1
fi

APP="dist/PlayLive PayID Scanner.app"
if [[ ! -d "$APP" ]]; then
  echo "Build the app first: ./scripts/build_app.sh" >&2
  exit 1
fi

VERSION="$(cat VERSION)"

WORK_DIR="$(mktemp -d)"
ROOT_DIR="$WORK_DIR/root"
mkdir -p "$ROOT_DIR/Applications"
cp -R "$APP" "$ROOT_DIR/Applications/"

chmod +x packaging/postinstall

OUT="dist/PlayLive PayID Scanner Installer.pkg"
pkgbuild \
  --root "$ROOT_DIR" \
  --scripts packaging \
  --identifier com.playlive.payidscanner \
  --version "$VERSION" \
  --install-location / \
  "$OUT"

rm -rf "$WORK_DIR"

echo ""
echo "Built: $OUT"
echo ""
echo "NOTE: this package is unsigned. macOS Gatekeeper will block it on"
echo "first open on every coworker's Mac -- see docs/deployment.md for"
echo "the one-time bypass (Control-click -> Open, or System Settings ->"
echo "Privacy & Security -> Open Anyway)."
