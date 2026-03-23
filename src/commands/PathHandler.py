from src.path_src import ALIASES_FILE
from datetime import datetime, timezone
from pathlib import Path
import json
from rich.console import Console
from rich.table import Table

console = Console()

YELLOW = "yellow"
GREEN = "#0af034"
ORANGE = "#ab8a07"
RED = "#c71208"
TURQ = "#0799a3"

class PathHandler:
    def __init__(self):
        self.aliases = self._load_json()
        self.abort_keywords = ["abort", "x", "exit", ":q", "quit"]
        self.cancel_process = "USER_REQ_CANCEL"

    ########### REUSABLE METHODS ###########
    def _load_json(self):
        # If json nonexistent, create it, otherwise load it up
        try:
            with open(ALIASES_FILE, "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {}
            ALIASES_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(ALIASES_FILE, "x") as f:
                json.dump(config, f, indent=4)
        return config

    def _get_alias_data(self, key):
        return [data.get(key) for data in self.aliases.values()]

    def _validate_input(self, msg):
        while True:
            user_input = input(msg).strip()
            if user_input in self.abort_keywords:
                raise KeyboardInterrupt()
            if user_input == "":
                print("Input cannot be empty, please try again. Type 'cancel' to soft-cancel or 'exit'/'quit' to abort")
                continue
            if user_input.lower() == "cancel":
                print("Cancelling...\n")
                return self.cancel_process
            break
        return user_input

    ###### CREATE METHODS ######
    def add_new_alias(self, alias_name, path=None):
        self.new_alias = self._new_alias_blueprint()
        self.new_alias_name = alias_name
        if alias_name in self.aliases:
            raise ValueError(f"'{alias_name}' already exists")
        if not path:
            raise ValueError("A path must be provided. Use '.' to use the current directory.")
        validated_path = str(self._validate_path(path))

        curr_paths = self._get_alias_data("path")

        if validated_path in curr_paths:
            raise ValueError(f"Path already is attached to an alias")

        self.new_alias["path"] = validated_path

    def _validate_path(self, path_str):
        path = Path(path_str).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        path = path.resolve()
        if not path.exists():
            raise ValueError("Path does not exist")

        if not path.is_dir():
            raise ValueError("Path is not a directory")

        return path

    def add_description(self, desc):
        self.new_alias["description"] = desc

    def _new_alias_blueprint(self):
        return {
            "path": "",
            "description": None,
            "created_at": str(datetime.now(timezone.utc).isoformat()),
            "last_used": None,
            "usage": 0,
            "tags": [],
        }

    def complete_add_transaction(self):
        self.aliases[self.new_alias_name] = self.new_alias

        with open(ALIASES_FILE, "w") as f:
            json.dump(self.aliases, f, indent=4)

        console.print(f"\n[{GREEN}]Successfully added new alias[/{GREEN}]\n")

    ###### READ METHODS ######
    def read_aliases(self, alias_name=None, search_val=None):
        if not self.aliases:
            console.print(f"\n[i][{RED}]No data to display...[/{RED}][/i]\n")
            return

        if search_val:
            matches = {k: v for k, v in self.aliases.items() if search_val.lower() in k.lower()}
            if not matches:
                console.print(f"\n[i][{RED}]No aliases matching '{search_val}'[/{RED}][/i]\n")
                return
            self._print_table(matches)
            return

        if alias_name:
            if alias_name not in self.aliases:
                console.print(
                    f"\n[i][{RED}]'{alias_name}' is not an existing alias[/{RED}][/i]\n"
                )
                return
            self._print_specific_alias({alias_name: self.aliases[alias_name]})
            return

        self._print_table(self.aliases)

    def _print_specific_alias(self, data):
        for alias, md in data.items():
            console.print(f"\n[{TURQ}]Alias Name:[/{TURQ}] {alias}")
            console.print(f"[{TURQ}]Path:[/{TURQ}] {md.get('path', "---")}")
            console.print(f"[{TURQ}]Description:[/{TURQ}] {md.get('description', "---")}")
            console.print(f"[{TURQ}]Alias Age:[/{TURQ}]")
            console.print(f"[{TURQ}]Last Used:[/{TURQ}]")
            console.print(f"[{TURQ}]Usage:[/{TURQ}] [{YELLOW}]{md.get('usage', 0)}[/{YELLOW}]\n")

    def _print_table(self, data):
        table = self._create_table()
        for alias, md in data.items():
            last_used = md.get('last_used')
            if last_used:
                last_used_dt = datetime.fromisoformat(last_used)
                if last_used_dt.date() == datetime.now().date():
                    last_used = last_used_dt.strftime('%m-%d-%Y %I:%M %p')
                else:
                    last_used = last_used_dt.strftime('%m-%d-%Y')
            path = md.get('path')
            usage = (
                f"[{RED}]{md.get('usage')}[/{RED}]" if md.get('usage') == 0 else 
                f"[{YELLOW}]{md.get('usage')}[/{YELLOW}]" if md.get('usage') < 20 else
                f"[{GREEN}]{md.get('usage')}[/{GREEN}]")
            table.add_row(
                alias,
                f"[{YELLOW}]{self._shorten_path(path)}[/{YELLOW}]" if path else '---',
                md.get('description') or '---',
                self._get_alias_age(md['created_at']),
                last_used or '---',
                usage,
            )
        console.print(table)

    def _create_table(self):
        table = Table(title="\n[bold]Alias List[/bold]\n", title_justify="center", caption="\n")

        table.add_column(header="[cyan][bold]Alias Name[/bold][/cyan]", min_width=5, max_width=15, no_wrap=True)
        table.add_column(header="[cyan][bold]Path[/bold][/cyan]", min_width=10, max_width=25, no_wrap=True)
        table.add_column(header="[cyan][bold]Description[/bold][/cyan]", min_width=10, max_width=30, no_wrap=True)
        table.add_column(header="[cyan][bold]Alias Age[/bold][/cyan]", max_width=20, no_wrap=True)
        table.add_column(header="[cyan][bold]Last Used[/bold][/cyan]", max_width=20, no_wrap=True)
        table.add_column(header="[cyan][bold]Usage[/bold][/cyan]", justify="center")
        return table

    def _shorten_path(self, path_str):
        path = Path(path_str)
        try:
            relative = path.relative_to(Path.home())
            return "~/" + relative.as_posix()
        except ValueError:
            return path_str

    def _get_alias_age(self, created_at: str):
        created = datetime.fromisoformat(created_at)
        now = datetime.now(timezone.utc)
        delta = now - created

        total_seconds = delta.total_seconds()
        total_minutes = total_seconds / 60
        total_hours = total_minutes / 60
        total_days = delta.days

        if total_seconds < 60:
            s = round(total_seconds)
            return f"[{GREEN}]{s} second{'s' if s != 1 else ''}[/{GREEN}]"

        if total_minutes < 50:
            m = round(total_minutes)
            return f"[{GREEN}]{m} minute{'s' if m != 1 else ''}[/{GREEN}]"

        if total_hours < 24:
            h = max(1, round(total_hours))
            return f"[{GREEN}]{h} hour{'s' if h != 1 else ''}[/{GREEN}]"

        if total_days < 7:
            return f"[{GREEN}]{total_days} day{'s' if total_days != 1 else ''}[/{GREEN}]"

        if total_days < 42:
            w = round(total_days / 7)
            return f"[{GREEN}]{w} week{'s' if w != 1 else ''}[/{GREEN}]"

        if total_days <= 366:
            mo = round(total_days / 30.44)
            return f"[{ORANGE}]{mo} month{'s' if mo != 1 else ''}[/{ORANGE}]"

        years = total_days // 365
        remaining_days = total_days - (years * 365)
        year_str = f"{years} year{'s' if years != 1 else ''}"

        remainder = self._format_remaining_days(remaining_days)
        return f"[{RED}]{year_str} {remainder}[/{RED}]" if remainder else f"[{RED}]{year_str}[/{RED}]"

    def _format_remaining_days(self, days: int):
        if days == 0:
            return ""
        if days < 7:
            return f"{days} day{'s' if days != 1 else ''}"
        if days < 42:
            w = round(days / 7)
            return f"{w} week{'s' if w != 1 else ''}"
        mo = round(days / 30.44)
        return f"{mo} month{'s' if mo != 1 else ''}"

    ###### UPDATE METHODS ######
    def _get_alias(self, alias_name):
        if alias_name not in self.aliases:
            raise ValueError(f"'{alias_name}' does not exist")
        return self.aliases[alias_name]

    def update_name(self, alias_name, new_name):
        self._get_alias(alias_name)
        if alias_name == new_name:
            console.print(f"\n[{YELLOW}]'{alias_name}' is already named that[/{YELLOW}]\n")
            return False
        if new_name in self.aliases:
            raise ValueError(f"'{new_name}' is already in use")
        self.aliases[new_name] = self.aliases.pop(alias_name)
        return True

    def update_path(self, alias_name, new_path):
        alias = self._get_alias(alias_name)
        validated_path = str(self._validate_path(new_path))

        if alias["path"] == validated_path:
            console.print(f"\n[{YELLOW}]'{alias_name}' is already set to that path[/{YELLOW}]\n")
            return False

        curr_paths = self._get_alias_data("path")
        if validated_path in curr_paths:
            raise ValueError("Path is already attached to an alias")

        alias["path"] = validated_path
        return True

    def update_description(self, alias_name, new_desc):
        alias = self._get_alias(alias_name)
        alias["description"] = new_desc

    def complete_update_transaction(self, alias_name):
        with open(ALIASES_FILE, "w") as f:
            json.dump(self.aliases, f, indent=4)

        console.print(f"\n[{GREEN}]Successfully updated '{alias_name}'[/{GREEN}]\n")

    ###### DELETE METHODS ######

    def delete_alias(self, alias_name):
        try:
            res = self._validate_input("\nAre you sure you want to delete? Deletion is permanent. (y/N)")
            if res.lower() in ['yes', 'y', 'yeah', 'yea', 'ye']:

                self.aliases.pop(alias_name)
            else:
                console.print(f"\n[{YELLOW}]Deletion cancelled...[/{YELLOW}]\n")
                return
        except KeyError:
            console.print(f"\n[{YELLOW}]Error: {alias_name} does not exist. No aliases were removed.[/{YELLOW}]")
            return
        
        with open(ALIASES_FILE, 'w') as f:
            json.dump(self.aliases, f, indent=4)
        
        console.print(f"\n[{YELLOW}]Successfully [underline]deleted[/underline] {alias_name}[/{YELLOW}]\n")

    def write_config(self):
        data = json.dumps(self.aliases, indent=4)
        with open(ALIASES_FILE, "w") as f:
            f.write(data)