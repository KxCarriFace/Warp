import urllib.request
import tarfile
import tempfile
import shutil
import sys
from datetime import datetime
from pathlib import Path
from src.globals import ROOT_DIR, console, GREEN, YELLOW, RED

REPO = "KxCarriFace/Warp"
BRANCH = "main"
RAW_VERSION_URL = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/VERSION"
RAW_CHANGELOG_URL = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/CHANGELOG.md"
TARBALL_URL = f"https://github.com/{REPO}/archive/refs/heads/{BRANCH}.tar.gz"
CACHE_FILE = ROOT_DIR / "config" / ".update_cache"
CHECK_INTERVAL = 86400  # 24 hours

# These are never touched during an update — user data and environment
SKIP = {"config", ".venv", ".git"}


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
    try:
        remote = _fetch_remote_version()
        CACHE_FILE.write_text(datetime.now().isoformat())
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
            # Extract version from "## [1.0.1] - 2026-03-27"
            version = header.split("[")[1].split("]")[0]
            if _parse_version(version) <= _parse_version(local):
                break
            if _parse_version(version) <= _parse_version(remote):
                result.append((header, lines))

        return result
    except Exception:
        return None


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

    console.print(f"\nUpdate available: v{local} \u2192 v{remote}\n")

    sections = _fetch_changelog_since(local, remote)
    if sections:
        console.print(f"[{YELLOW}]What's new:[/{YELLOW}]")
        for header, lines in sections:
            console.print(f"  [{YELLOW}]{header}[/{YELLOW}]")
            for line in lines:
                if line.strip():
                    console.print(f"  {line}")
        console.print("")

    confirm = input("Update now? [y/N] ").strip().lower()
    if confirm != 'y':
        console.print("Update cancelled.")
        return

    console.print("Downloading update...")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tarball = tmp_path / "warp.tar.gz"

            urllib.request.urlretrieve(TARBALL_URL, tarball)

            extract_dir = tmp_path / "extracted"
            extract_dir.mkdir()
            with tarfile.open(tarball) as tf:
                if sys.version_info >= (3, 12):
                    tf.extractall(extract_dir, filter='data')
                else:
                    tf.extractall(extract_dir)

            # GitHub tarballs extract into one subdirectory (e.g. Warp-main/)
            extracted_root = next(extract_dir.iterdir())

            for item in extracted_root.iterdir():
                if item.name in SKIP:
                    continue
                dest = ROOT_DIR / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)

        # Reset cache so the next run re-checks against the new version
        CACHE_FILE.unlink(missing_ok=True)
        console.print(f"[{GREEN}]Updated to v{remote} successfully![/{GREEN}]")

    except Exception as e:
        console.print(f"[{RED}]Update failed: {e}[/{RED}]")


def reg_update_cmd(subparsers):
    p = subparsers.add_parser("update", help="Check for and install updates")
    p.set_defaults(func=run_update)
