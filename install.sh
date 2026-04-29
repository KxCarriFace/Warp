#!/usr/bin/env bash

WARP_DIR="$HOME/.usr/warp"
WARP_SH="$WARP_DIR/warp.sh"
SOURCE_LINE="source \"$WARP_DIR/warp.sh\""

# Detect OS and set venv binary paths
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    WARP_PYTHON="$WARP_DIR/.venv/Scripts/python.exe"
    WARP_PIP="$WARP_DIR/.venv/Scripts/pip"
else
    WARP_PYTHON="$WARP_DIR/.venv/bin/python"
    WARP_PIP="$WARP_DIR/.venv/bin/pip"
fi

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
        echo "On Ubuntu/Debian, install it with:"
        echo "  sudo apt install python3-venv"
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

# ── 5. Add source line to shell config ────────────────────────────────────────

_warp_add_source() {
    local cfg="$1"
    if grep -qF "$SOURCE_LINE" "$cfg" 2>/dev/null; then
        echo "[skip] warp.sh is already sourced in $cfg"
    else
        { echo ""; echo "# Warp — filesystem alias navigator"; echo "$SOURCE_LINE"; } >> "$cfg"
        echo "[done] Added warp.sh source line to $cfg"
    fi
}

CURRENT_SHELL="$(basename "${SHELL:-bash}")"

case "$CURRENT_SHELL" in
    zsh)  SHELL_RC="$HOME/.zshrc" ;;
    *)    SHELL_RC="$HOME/.bashrc" ;;
esac

_warp_add_source "$SHELL_RC"

# On macOS, bash login shells use .bash_profile — add there too if it exists
if [ "$CURRENT_SHELL" = "bash" ] && [ -f "$HOME/.bash_profile" ]; then
    _warp_add_source "$HOME/.bash_profile"
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

# ── 7. Reload shell config ────────────────────────────────────────────────────

# shellcheck disable=SC1090
source "$SHELL_RC" 2>/dev/null || true

echo ""
echo "Setup complete. Warp is ready to use."
echo ""
echo "  Try it:  warp list"
echo ""
echo "NOTE: If 'warp' is not found in your current terminal, run:"
echo "  source $SHELL_RC"
echo ""
