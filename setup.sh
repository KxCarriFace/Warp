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

# ── 2. Download and extract the project ───────────────────────────────────────

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

# ── 3. Move or update project files ───────────────────────────────────────────

mkdir -p "$HOME/.usr"

if [ -d "$WARP_DIR" ]; then
    echo "Warp is already installed — updating source files..."
    for item in "$TMP_DIR"/*/; do
        name="$(basename "$item")"
        [ "$name" = "config" ] && continue
        [ "$name" = ".venv" ] && continue
        [ "$name" = ".git" ] && continue
        rm -rf "$WARP_DIR/$name"
        cp -r "$TMP_DIR/$name" "$WARP_DIR/$name"
    done
    # copy root-level files
    find "$TMP_DIR" -maxdepth 1 -type f | while read -r f; do
        cp "$f" "$WARP_DIR/$(basename "$f")"
    done
    rm -rf "$TMP_DIR"
    echo "[done] Source files updated"
else
    mv "$TMP_DIR" "$WARP_DIR"
    echo "[done] Warp downloaded to $WARP_DIR"
fi

# ── 5. Hand off to install.sh ─────────────────────────────────────────────────

chmod +x "$WARP_DIR/install.sh"
bash "$WARP_DIR/install.sh"
