from pathlib import Path
from rich.console import Console

# Paths
ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT_DIR / "config"
ALIASES_FILE = CONFIG_DIR / "alias.json"

# Console instances
console = Console()
stderr_console = Console(stderr=True)

# Colors
YELLOW = "yellow"
GREEN = "#0af034"
ORANGE = "#ab8a07"
RED = "#c71208"
TURQ = "#0799a3"
