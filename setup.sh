#!/usr/bin/env bash

GITHUB_USER="KxCarriFace"
GITHUB_REPO="warp"
GITHUB_BRANCH="main"
DOWNLOAD_URL="https://github.com/$GITHUB_USER/$GITHUB_REPO/archive/refs/heads/$GITHUB_BRANCH.tar.gz"

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

# ── 2. Skip download if already installed ─────────────────────────────────────

if [ -d "$WARP_DIR" ]; then
    echo ""
    echo "Warp is already present at $WARP_DIR"
    echo "Skipping download and jumping straight to install..."
    echo ""
    bash "$WARP_DIR/install.sh"
    exit $?
fi

# ── 3. Download and extract the project ───────────────────────────────────────

echo ""
echo "Downloading Warp..."
echo ""

TMP_DIR="$(mktemp -d)"

if [ "$DOWNLOADER" = "curl" ]; then
    curl -sL "$DOWNLOAD_URL" | tar -xz -C "$TMP_DIR" --strip-components=1
else
    wget -qO- "$DOWNLOAD_URL" | tar -xz -C "$TMP_DIR" --strip-components=1
fi

if [ $? -ne 0 ]; then
    rm -rf "$TMP_DIR"
    echo ""
    echo "ERROR: Failed to download or extract Warp."
    echo ""
    echo "Check that the repository is public and the URL is reachable:"
    echo "  $DOWNLOAD_URL"
    echo ""
    exit 1
fi

# ── 4. Move project into place ────────────────────────────────────────────────

mkdir -p "$HOME/.usr"
mv "$TMP_DIR" "$WARP_DIR"

echo "[done] Warp downloaded to $WARP_DIR"

# ── 5. Hand off to install.sh ─────────────────────────────────────────────────

chmod +x "$WARP_DIR/install.sh"
bash "$WARP_DIR/install.sh"
