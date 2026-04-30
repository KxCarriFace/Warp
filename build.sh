#!/usr/bin/env bash
# Builds the warp binary for the current platform using PyInstaller.
#
# Usage (from project root, with your venv active):
#   pip install pyinstaller
#   bash build.sh
#
# Output:
#   dist/warp        (Linux / macOS)
#   dist/warp.exe    (Windows)

set -e

echo ""
echo "Building warp binary..."
echo ""

pyinstaller \
    --onefile \
    --name warp \
    --distpath ./dist \
    --workpath ./build \
    --specpath . \
    --collect-all rich \
    cli.py

echo ""

# Rename to platform-specific name for GitHub release uploads
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    echo "[done] Binary: dist/warp.exe"
    echo ""
    echo "Upload dist/warp.exe to the GitHub release as:  warp-windows.exe"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "[done] Binary: dist/warp"
    echo ""
    echo "Upload dist/warp to the GitHub release as:  warp-macos"
else
    echo "[done] Binary: dist/warp"
    echo ""
    echo "Upload dist/warp to the GitHub release as:  warp-linux"
fi

echo ""
