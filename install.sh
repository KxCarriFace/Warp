#!/usr/bin/env bash

WARP_DIR="$HOME/.usr/warp"
WARP_SH="$WARP_DIR/warp.sh"
WARP_PYTHON="$WARP_DIR/.venv/Scripts/python.exe"
WARP_PIP="$WARP_DIR/.venv/Scripts/pip"
BASHRC="$HOME/.bashrc"
SOURCE_LINE="source \"$WARP_DIR/warp.sh\""

# ── 1. Check Python is installed ──────────────────────────────────────────────

if ! command -v python &>/dev/null && ! command -v python3 &>/dev/null; then
    echo ""
    echo "ERROR: Python is not installed or not on your PATH."
    echo ""
    echo "Warp requires Python 3. Install it from:"
    echo "  https://www.python.org/downloads/"
    echo ""
    echo "Make sure to check 'Add Python to PATH' during installation."
    echo ""
    exit 1
fi

# Prefer python3, fall back to python
if command -v python3 &>/dev/null; then
    SYS_PYTHON="python3"
else
    SYS_PYTHON="python"
fi

# Verify it's Python 3
PY_VERSION=$("$SYS_PYTHON" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
if [ "$PY_VERSION" != "3" ]; then
    echo ""
    echo "ERROR: Python 3 is required, but the available Python is version $PY_VERSION."
    echo ""
    echo "Install Python 3 from:"
    echo "  https://www.python.org/downloads/"
    echo ""
    exit 1
fi

# ── 2. Verify warp is in the expected location ────────────────────────────────

if [ ! -d "$WARP_DIR" ]; then
    echo ""
    echo "ERROR: Warp project not found at the required location."
    echo ""
    echo "  Expected:  $WARP_DIR"
    echo ""
    echo "The easiest way to get started is to run the bootstrap script:"
    echo ""
    echo "  bash setup.sh"
    echo ""
    echo "Or manually place the project at the expected location:"
    echo ""
    echo "  mkdir -p \"\$HOME/.usr\""
    echo "  mv /path/to/warp \"\$HOME/.usr/warp\""
    echo ""
    exit 1
fi

if [ ! -f "$WARP_SH" ]; then
    echo ""
    echo "ERROR: warp.sh not found inside $WARP_DIR"
    echo "The project appears incomplete. Please re-download it."
    echo ""
    exit 1
fi

echo ""
echo "Warp found at $WARP_DIR — starting setup..."
echo ""

# ── 3. Create virtual environment ─────────────────────────────────────────────

if [ -f "$WARP_PYTHON" ]; then
    echo "[skip] Virtual environment already exists"
else
    echo "[....] Creating virtual environment..."
    "$SYS_PYTHON" -m venv "$WARP_DIR/.venv"
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to create the virtual environment."
        echo "Make sure the 'venv' module is available (it ships with Python 3.3+)."
        echo ""
        exit 1
    fi
    echo "[done] Virtual environment created"
fi

# ── 4. Install dependencies ───────────────────────────────────────────────────

if [ ! -f "$WARP_DIR/requirements.txt" ]; then
    echo ""
    echo "ERROR: requirements.txt not found in $WARP_DIR"
    echo "The project appears incomplete. Please re-download it."
    echo ""
    exit 1
fi

echo "[....] Installing dependencies from requirements.txt..."
"$WARP_PIP" install -r "$WARP_DIR/requirements.txt" --quiet
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install dependencies."
    echo "Try running manually:"
    echo "  \"$WARP_PIP\" install -r \"$WARP_DIR/requirements.txt\""
    echo ""
    exit 1
fi
echo "[done] Dependencies installed"

# ── 5. Add source line to .bashrc ─────────────────────────────────────────────

if grep -qF "$SOURCE_LINE" "$BASHRC" 2>/dev/null; then
    echo "[skip] warp.sh is already sourced in $BASHRC"
else
    {
        echo ""
        echo "# Warp — filesystem alias navigator"
        echo "$SOURCE_LINE"
    } >> "$BASHRC"
    echo "[done] Added warp.sh source line to $BASHRC"
fi

# ── 6. Create config/alias.json with default home alias ───────────────────────

ALIAS_JSON="$WARP_DIR/config/alias.json"

if [ -f "$ALIAS_JSON" ]; then
    echo "[skip] alias.json already exists — leaving it untouched"
else
    "$WARP_PYTHON" - <<'PYEOF'
import json
from pathlib import Path
from datetime import datetime, timezone

aliases_file = Path.home() / ".usr" / "warp" / "config" / "alias.json"
aliases_file.parent.mkdir(parents=True, exist_ok=True)

data = {
    "home": {
        "path": str(Path.home()),
        "description": "Home directory",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_used": None,
        "usage": 0,
        "tags": [],
        "delete_info": None,
    }
}

with open(aliases_file, "x") as f:
    json.dump(data, f, indent=4)

print("[done] Created alias.json with default 'home' alias")
PYEOF

    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to create alias.json."
        echo ""
        exit 1
    fi
fi

# ── 7. Reload .bashrc ─────────────────────────────────────────────────────────

# shellcheck disable=SC1090
source "$BASHRC"

echo ""
echo "Setup complete. Warp is ready to use."
echo ""
echo "  Try it:  warp list"
echo ""
echo "NOTE: If 'warp' is not found in your current terminal, run:"
echo "  source ~/.bashrc"
echo ""
