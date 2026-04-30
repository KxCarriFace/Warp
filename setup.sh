#!/usr/bin/env bash

GITHUB_USER="KxCarriFace"
GITHUB_REPO="warp"

WARP_DIR="$HOME/.usr/warp"

# ── 1. Check download tool is available ───────────────────────────────────────

if command -v curl &>/dev/null; then
    DOWNLOADER="curl"
elif command -v wget &>/dev/null; then
    DOWNLOADER="wget"
else
    echo ""
    echo "ERROR: Neither curl nor wget was found."
    echo ""
    echo "Install one of them and try again:"
    echo "  sudo apt install curl     # Debian / Ubuntu / WSL"
    echo "  sudo pacman -S curl       # Arch"
    echo "  brew install curl         # macOS"
    echo ""
    exit 1
fi

# ── 2. Detect platform and pick the right binary ──────────────────────────────

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    ASSET_NAME="warp-windows.exe"
    BINARY_NAME="warp.exe"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    ASSET_NAME="warp-macos"
    BINARY_NAME="warp"
else
    ASSET_NAME="warp-linux"
    BINARY_NAME="warp"
fi

DOWNLOAD_URL="https://github.com/$GITHUB_USER/$GITHUB_REPO/releases/latest/download/$ASSET_NAME"

# ── 3. Download the binary ────────────────────────────────────────────────────

echo ""
echo "Downloading Warp..."
echo ""

mkdir -p "$WARP_DIR"

if [ "$DOWNLOADER" = "curl" ]; then
    curl -sL "$DOWNLOAD_URL" -o "$WARP_DIR/$BINARY_NAME"
else
    wget -qO "$WARP_DIR/$BINARY_NAME" "$DOWNLOAD_URL"
fi

if [ $? -ne 0 ] || [ ! -s "$WARP_DIR/$BINARY_NAME" ]; then
    rm -f "$WARP_DIR/$BINARY_NAME"
    echo ""
    echo "ERROR: Failed to download the Warp binary."
    echo ""
    echo "Check that a release exists and the URL is reachable:"
    echo "  $DOWNLOAD_URL"
    echo ""
    exit 1
fi

echo "[done] Binary downloaded to $WARP_DIR/$BINARY_NAME"

# ── 4. Also download warp.sh and VERSION ─────────────────────────────────────

WARP_SH_URL="https://github.com/$GITHUB_USER/$GITHUB_REPO/releases/latest/download/warp.sh"

if [ "$DOWNLOADER" = "curl" ]; then
    curl -sL "$WARP_SH_URL" -o "$WARP_DIR/warp.sh"
else
    wget -qO "$WARP_DIR/warp.sh" "$WARP_SH_URL"
fi

if [ $? -ne 0 ] || [ ! -s "$WARP_DIR/warp.sh" ]; then
    rm -f "$WARP_DIR/warp.sh"
    echo ""
    echo "ERROR: Failed to download warp.sh."
    echo ""
    echo "Check that the release includes warp.sh:"
    echo "  $WARP_SH_URL"
    echo ""
    exit 1
fi

echo "[done] warp.sh downloaded"

VERSION_URL="https://github.com/$GITHUB_USER/$GITHUB_REPO/releases/latest/download/VERSION"

if [ "$DOWNLOADER" = "curl" ]; then
    curl -sL "$VERSION_URL" -o "$WARP_DIR/VERSION"
else
    wget -qO "$WARP_DIR/VERSION" "$VERSION_URL"
fi

if [ $? -ne 0 ] || [ ! -s "$WARP_DIR/VERSION" ]; then
    rm -f "$WARP_DIR/VERSION"
    echo ""
    echo "ERROR: Failed to download VERSION."
    echo ""
    echo "Check that the release includes VERSION:"
    echo "  $VERSION_URL"
    echo ""
    exit 1
fi

echo "[done] VERSION downloaded"

# ── 5. Hand off to install.sh ─────────────────────────────────────────────────

INSTALL_SH_URL="https://github.com/$GITHUB_USER/$GITHUB_REPO/releases/latest/download/install.sh"

if [ "$DOWNLOADER" = "curl" ]; then
    curl -sL "$INSTALL_SH_URL" -o "$WARP_DIR/install.sh"
else
    wget -qO "$WARP_DIR/install.sh" "$INSTALL_SH_URL"
fi

chmod +x "$WARP_DIR/install.sh"
bash "$WARP_DIR/install.sh"
