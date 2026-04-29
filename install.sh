#!/usr/bin/env bash

WARP_DIR="$HOME/.usr/warp"
WARP_SH="$WARP_DIR/warp.sh"
SOURCE_LINE="source \"$WARP_DIR/warp.sh\""

# Detect platform
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    WARP_BIN="$WARP_DIR/warp.exe"
else
    WARP_BIN="$WARP_DIR/warp"
fi

# ── 1. Verify the binary and warp.sh are present ──────────────────────────────

if [ ! -f "$WARP_BIN" ]; then
    echo ""
    echo "ERROR: Warp binary not found at $WARP_BIN"
    echo ""
    echo "Re-run the setup script to download it:"
    echo "  bash <(curl -sL https://raw.githubusercontent.com/KxCarriFace/warp/main/setup.sh)"
    echo ""
    exit 1
fi

if [ ! -f "$WARP_SH" ]; then
    echo ""
    echo "ERROR: warp.sh not found at $WARP_SH"
    echo ""
    echo "Re-run the setup script to download it:"
    echo "  bash <(curl -sL https://raw.githubusercontent.com/KxCarriFace/warp/main/setup.sh)"
    echo ""
    exit 1
fi

echo ""
echo "Warp found at $WARP_DIR — finishing setup..."
echo ""

# ── 2. Make binary executable (Linux / macOS) ─────────────────────────────────

if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "cygwin" && "$OSTYPE" != "win32" ]]; then
    chmod +x "$WARP_BIN"
    echo "[done] Binary marked as executable"
fi

# ── 3. Add source line to shell config ────────────────────────────────────────

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

# ── 4. Create config/alias.json with default home alias ───────────────────────

ALIAS_JSON="$WARP_DIR/config/alias.json"

if [ -f "$ALIAS_JSON" ]; then
    echo "[skip] alias.json already exists — leaving it untouched"
else
    mkdir -p "$WARP_DIR/config"
    cat > "$ALIAS_JSON" <<EOF
{
    "home": {
        "path": "$HOME",
        "description": "Home directory",
        "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%S+00:00")",
        "last_used": null,
        "usage": 0,
        "tags": [],
        "delete_info": null
    }
}
EOF
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to create alias.json."
        echo ""
        echo "Steps to fix:"
        echo "  1. Make sure the config directory is writable:"
        echo "       ls -la \"$WARP_DIR/config\""
        echo ""
        echo "  2. Create it manually:"
        echo "       mkdir -p \"$WARP_DIR/config\""
        echo "       chmod u+w \"$WARP_DIR/config\""
        echo ""
        echo "  3. Re-run the installer:"
        echo "       bash \"$WARP_DIR/install.sh\""
        echo ""
        exit 1
    fi
    echo "[done] Created alias.json with default 'home' alias"
fi

# ── 5. Reload shell config ────────────────────────────────────────────────────

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
