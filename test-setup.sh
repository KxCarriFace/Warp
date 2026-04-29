#!/usr/bin/env bash
# Local install test — builds the binary and stages it exactly as setup.sh would
# after downloading from a GitHub release.
#
# Run this BEFORE hiding/removing Python, then follow the printed instructions.

set -e

WARP_DIR="$HOME/.usr/warp"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "Step 1/2 — Building warp binary..."
echo ""

cd "$SCRIPT_DIR"

if ! command -v pyinstaller &>/dev/null; then
    pip3 install pyinstaller --quiet
fi

pyinstaller --onefile --name warp --distpath ./dist --workpath ./build --specpath . cli.py --log-level WARN

if [ ! -f "./dist/warp" ]; then
    echo ""
    echo "ERROR: Build failed — dist/warp not found."
    exit 1
fi

echo ""
echo "Step 2/2 — Staging files..."
echo ""

mkdir -p "$WARP_DIR"

cp dist/warp     "$WARP_DIR/warp"
cp warp.sh       "$WARP_DIR/warp.sh"
cp install.sh    "$WARP_DIR/install.sh"

chmod +x "$WARP_DIR/warp"
chmod +x "$WARP_DIR/install.sh"

echo "[done] Staged at $WARP_DIR"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Now hide Python to simulate a clean machine:"
echo ""
echo "  sudo mv /usr/bin/python3 /usr/bin/python3.bak"
echo "  hash -r"
echo ""
echo "Then run the installer:"
echo ""
echo "  bash \"$WARP_DIR/install.sh\""
echo ""
echo "Test it:"
echo ""
echo "  source ~/.bashrc"
echo "  warp list"
echo "  warp add test /tmp"
echo "  warp to test"
echo "  pwd   # should be /tmp"
echo ""
echo "When done, restore Python:"
echo ""
echo "  sudo mv /usr/bin/python3.bak /usr/bin/python3"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
