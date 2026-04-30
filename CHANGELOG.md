## [1.0.3] - 2026-04-29
- Migrated from Python script to self-contained binary — Python is no longer required on the user's machine
- `warp update` now downloads the platform binary from GitHub releases instead of the Python source tarball
- Fresh installs now correctly track the installed version (no more false update prompts)
- Added `build.sh` to produce platform binaries with PyInstaller

## [1.0.2] - 2026-04-29
- Fixed compatibility with Ubuntu, Debian, and other Linux distros
- `install.sh` now detects OS and uses correct venv paths (`.venv/bin/python` on Linux/macOS vs `.venv/Scripts/python.exe` on Windows)
- Shell config injection now targets the active shell (`.zshrc` for zsh, `.bashrc` for bash) instead of always writing to `.bashrc`
- Added `python3-venv` install hint for Ubuntu/Debian if virtual environment creation fails
- Fixed `warp update` crashing on Windows with `WinError 32` (file in use) when replacing `src/` directory
- Fixed `warp list` crashing with `TypeError` if an alias had a timezone-naive `created_at` timestamp
- Fixed unclear error message when downloaded update archive is empty or malformed

## [1.0.1] - 2026-03-27
- Fixed last used time displaying in UTC instead of local timezone
- Added `warp update` command to update Warp from the terminal
- Added automatic update notifications after commands (checks once per day)

## [1.0.0] - 2026-03-22
- Initial release
