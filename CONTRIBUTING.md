# Contributing to Warp

## How it works

Warp is written in Python and packaged into a self-contained binary using [PyInstaller](https://pyinstaller.org). End users don't need Python installed — they just download the binary.

## Building

**Prerequisites:** Python 3.3+, pip

```bash
pip install pyinstaller
bash build.sh
```

Output:
- `dist/warp` on Linux / macOS
- `dist/warp.exe` on Windows

`build.sh` will print the exact filename to use when uploading to a GitHub release.

## Testing the install locally

Before shipping, test the full install flow without Python present:

```bash
# 1. Build and stage everything — run while Python is still installed
bash test-setup.sh

# 2. Hide Python to simulate a clean machine
sudo mv /usr/bin/python3 /usr/bin/python3.bak
hash -r

# 3. Run the installer and verify
bash "$HOME/.usr/warp/install.sh"
source ~/.bashrc
warp list
warp add test /tmp
warp to test && pwd   # should print /tmp

# 4. Restore Python when done
sudo mv /usr/bin/python3.bak /usr/bin/python3
```

## Shipping a release

1. Build the binary on each target platform
2. Create a GitHub release and attach:
   - `warp-linux`
   - `warp-macos`
   - `warp-windows.exe`
   - `warp.sh`
   - `install.sh`
