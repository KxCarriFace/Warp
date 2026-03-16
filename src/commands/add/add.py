import sys
import json
from pathlib import Path
from src.path_src import ALIASES_FILE
from datetime import datetime, timezone


#REGISTER COMMANDS/SUBCOMMANDS AND OPTIONS
def reg_add_cmd(subparsers):
    parser = subparsers.add_parser(
        "add",
        help="Add warp alias to [path] or current working directory"
    )

    parser.add_argument(
        "alias",
        help="Name of the alias"
    )

    parser.add_argument(
        "path",
        nargs="?",
        help="Optional path (defaults to current directory)"
    )

    parser.set_defaults(func=add_alias)


#MAIN FUNCTION
def add_alias(args):
    try:
        alias = PathHandler(args.alias, args.path)
        alias.save_config()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


#CLASS TO HANDLE ALL FUNCTIONS
class PathHandler:
    def __init__(self, alias, path):
        self.alias_config = self.get_alias_config()
        self.alias_name = alias.lower()
        self.path = path
        self.validated_path = self.validate_path()

    def validate_path(self):
        if self.path is None:
            p = Path.cwd()
        else:
            p = Path(self.path).expanduser()
        
        try: 
            p = p.resolve(strict=True)
        except FileNotFoundError:
            raise ValueError(f"Path does not exist: {self.path}")
        
        if not p.is_dir():
            raise ValueError(f"Path is not a directory: {self.path}")
        
        return p
    
    def validate_uniqueness(self):
        for key, arr in self.alias_config.items():
            if self.alias_name == key:
                raise ValueError("Alias already exists")
            if str(self.validated_path) == arr.get("path"):
                raise ValueError("Alias path already exists")

    def get_alias_config(self):
        if not ALIASES_FILE.exists():
            return {"aliases": {}}
        with open(ALIASES_FILE, "r") as f:
            json_data = json.load(f)
            return json_data.get('aliases')
        
    def save_config(self):
        self.validate_uniqueness()

        self.alias_config[self.alias_name] = {
            "path": str(self.validated_path),
            "description": None,
            "created_at": self.create_timestamp(),
            "last_used": None,
            "usage": 0,
            "tags": [],
        }

        full_config = {
            "aliases": self.alias_config
        }

        with open(ALIASES_FILE, "w") as f:
            json.dump(full_config, f, indent=4)

    def create_timestamp(self):
        return datetime.now(timezone.utc).isoformat()
    
