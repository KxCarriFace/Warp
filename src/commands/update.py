import sys
import os
import urllib.request
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from src.globals import ROOT_DIR, console, GREEN, YELLOW, RED

REPO = "KxCarriFace/warp"
BRANCH = "main"
RAW_VERSION_URL = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/VERSION"
RAW_CHANGELOG_URL = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/CHANGELOG.md"
RELEASES_BASE = f"https://github.com/{REPO}/releases/latest/download"
CACHE_FILE = ROOT_DIR / "config" / ".update_cache"
CHECK_INTERVAL = 86400  # 24 hours


def _platform_asset():
    if sys.platform == "win32":
        return "warp-windows.exe", "warp.exe"
    elif sys.platform == "darwin":
        return "warp-macos", "warp"
    else:
        return "warp-linux", "warp"


def _parse_version(v):
    try:
        return tuple(int(x) for x in v.strip().split('.'))
    except ValueError:
        return (0,)


def _local_version():
    vf = ROOT_DIR / "VERSION"
    return vf.read_text().strip() if vf.exists() else "0.0.0"


def _fetch_remote_version():
    with urllib.request.urlopen(RAW_VERSION_URL, timeout=3) as r:
        return r.read().decode().strip()


def _should_check():
    if not CACHE_FILE.exists():
        return True
    try:
        last = datetime.fromisoformat(CACHE_FILE.read_text().strip())
        return (datetime.now() - last).total_seconds() > CHECK_INTERVAL
    except Exception:
        return True


def check_for_update():
    """Returns remote version string if update is available, else None. Silent on error."""
    if not _should_check():
        return None
    CACHE_FILE.write_text(datetime.now().isoformat())
    try:
        remote = _fetch_remote_version()
        if _parse_version(remote) > _parse_version(_local_version()):
            return remote
    except Exception:
        pass
    return None


def _fetch_changelog_since(local, remote):
    try:
        with urllib.request.urlopen(RAW_CHANGELOG_URL, timeout=3) as r:
            changelog = r.read().decode()
        sections = []
        current_header = None
        current_lines = []
        for line in changelog.splitlines():
            if line.startswith("## ["):
                if current_header:
                    sections.append((current_header, current_lines))
                current_header = line
                current_lines = []
            elif current_header:
                current_lines.append(line)
        if current_header:
            sections.append((current_header, current_lines))

        result = []
        for header, lines in sections:
            version = header.split("[")[1].split("]")[0]
            if _parse_version(version) <= _parse_version(local):
                break
            if _parse_version(version) <= _parse_version(remote):
                result.append((header, lines))

        return result
    except Exception:
        return None


def show_version():
    local = _local_version()
    console.print(f"Warp v{local}")
    try:
        remote = _fetch_remote_version()
        if _parse_version(remote) > _parse_version(local):
            console.print(f"[{YELLOW}]Update available: v{remote}. Run [bold]warp update[/bold] to install.[/{YELLOW}]")
        else:
            console.print(f"[{GREEN}]You're up to date.[/{GREEN}]")
    except Exception:
        pass


def run_update(args):
    local = _local_version()
    console.print("Checking for updates...")
    try:
        remote = _fetch_remote_version()
    except Exception as e:
        console.print(f"[{RED}]Could not reach GitHub: {e}[/{RED}]")
        return

    if _parse_version(remote) <= _parse_version(local):
        console.print(f"[{GREEN}]Already up to date (v{local})[/{GREEN}]")
        return

    if args.details:
        sections = _fetch_changelog_since(local, remote)
        if sections:
            console.print(f"\n[{YELLOW}]Changes from v{local} to v{remote}:[/{YELLOW}]\n")
            for header, lines in sections:
                console.print(f"  [{YELLOW}]{header}[/{YELLOW}]")
                for line in lines:
                    if line.strip():
                        console.print(f"  {line}")
            console.print("")
        return

    console.print(f"Update available: v{local} → v{remote}")
    confirm = input("Update now? [y/N] ").strip().lower()
    if confirm != 'y':
        console.print("Update cancelled.")
        return

    asset_name, binary_name = _platform_asset()
    binary_url = f"{RELEASES_BASE}/{asset_name}"
    warp_sh_url = f"{RELEASES_BASE}/warp.sh"

    binary_dest = ROOT_DIR / binary_name
    warp_sh_dest = ROOT_DIR / "warp.sh"
    version_dest = ROOT_DIR / "VERSION"

    console.print("Downloading update...")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            tmp_binary = tmp_path / binary_name
            urllib.request.urlretrieve(binary_url, tmp_binary)

            tmp_warp_sh = tmp_path / "warp.sh"
            urllib.request.urlretrieve(warp_sh_url, tmp_warp_sh)

            shutil.copy2(tmp_binary, binary_dest)
            if sys.platform != "win32":
                os.chmod(binary_dest, 0o755)

            shutil.copy2(tmp_warp_sh, warp_sh_dest)
            version_dest.write_text(remote)

        CACHE_FILE.unlink(missing_ok=True)
        console.print(f"[{GREEN}]Updated to v{remote} successfully![/{GREEN}]\n")

        sections = _fetch_changelog_since(local, remote)
        if sections:
            console.print(f"[{YELLOW}]What changed:[/{YELLOW}]")
            for header, lines in sections:
                console.print(f"  [{YELLOW}]{header}[/{YELLOW}]")
                for line in lines:
                    if line.strip():
                        console.print(f"  {line}")
            console.print("")

    except Exception as e:
        console.print(f"[{RED}]Update failed: {e}[/{RED}]")


def reg_update_cmd(subparsers):
    p = subparsers.add_parser("update", help="Check for and install updates")
    p.add_argument("--details", action="store_true", help="Show what changed without updating")
    p.set_defaults(func=run_update)
