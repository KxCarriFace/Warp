## [1.0.2] - 2026-04-29
- Fixed compatibility with Ubuntu, Debian, and other Linux distros
- `install.sh` now detects OS and uses correct venv paths (`.venv/bin/python` on Linux/macOS vs `.venv/Scripts/python.exe` on Windows)
- Shell config injection now targets the active shell (`.zshrc` for zsh, `.bashrc` for bash) instead of always writing to `.bashrc`
- Added `python3-venv` install hint for Ubuntu/Debian if virtual environment creation fails

## [1.0.1] - 2026-03-27
- Fixed last used time displaying in UTC instead of local timezone
- Added `warp update` command to update Warp from the terminal
- Added automatic update notifications after commands (checks once per day)

## [1.0.0] - 2026-03-22
- Initial release
