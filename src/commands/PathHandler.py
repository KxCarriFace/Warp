from src.globals import ALIASES_FILE, console, YELLOW, GREEN, ORANGE, RED, TURQ
from datetime import datetime, timezone
from pathlib import Path
import json
from rich.table import Table

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

    def _is_active(self, alias_data):
        return not alias_data.get("delete_info")

    def _get_alias_data(self, key):
        return [data.get(key) for data in self.aliases.values() if self._is_active(data)]

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
        existing = self.aliases.get(alias_name)
        if existing and self._is_active(existing):
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
            "delete_info": None,
        }

    def complete_add_transaction(self):
        self.aliases[self.new_alias_name] = self.new_alias

        with open(ALIASES_FILE, "w") as f:
            json.dump(self.aliases, f, indent=4)

        console.print(f"\n[{GREEN}]Successfully added new alias[/{GREEN}]\n")

    ###### READ METHODS ######
    def read_aliases(self, alias_name=None, search_val=None, show_all=False):
        pool = self.aliases if show_all else {k: v for k, v in self.aliases.items() if self._is_active(v)}

        if not pool:
            console.print(f"\n[i][{RED}]No data to display...[/{RED}][/i]\n")
            return

        if search_val:
            matches = {k: v for k, v in pool.items() if search_val.lower() in k.lower()}
            if not matches:
                console.print(f"\n[i][{RED}]No aliases matching '{search_val}'[/{RED}][/i]\n")
                return
            self._print_table(matches, show_all=show_all)
            return

        if alias_name:
            if alias_name not in pool:
                console.print(
                    f"\n[i][{RED}]'{alias_name}' is not an existing alias[/{RED}][/i]\n"
                )
                return
            self._print_specific_alias({alias_name: pool[alias_name]})
            return

        self._print_table(pool, show_all=show_all)

    def _to_local(self, dt):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone()

    def _print_specific_alias(self, data):
        for alias, md in data.items():
            last_used = md.get('last_used')
            if last_used:
                last_used_dt = self._to_local(datetime.fromisoformat(last_used))
                if last_used_dt.date() == datetime.now().date():
                    last_used = last_used_dt.strftime('%m-%d-%Y %I:%M %p')
                else:
                    last_used = last_used_dt.strftime('%m-%d-%Y')
            console.print(f"\n[{TURQ}]Alias Name:[/{TURQ}] {alias}")
            console.print(f"[{TURQ}]Path:[/{TURQ}] {md.get('path') or '---'}")
            console.print(f"[{TURQ}]Description:[/{TURQ}] {md.get('description') or '---'}")
            console.print(f"[{TURQ}]Alias Age:[/{TURQ}] {self._get_alias_age(md['created_at'])}")
            console.print(f"[{TURQ}]Last Used:[/{TURQ}] {last_used or '---'}")
            console.print(f"[{TURQ}]Usage:[/{TURQ}] [{YELLOW}]{md.get('usage', 0)}[/{YELLOW}]\n")

    def _print_table(self, data, show_all=False):
        table = self._create_table(show_all=show_all)
        for alias, md in data.items():
            last_used = md.get('last_used')
            if last_used:
                last_used_dt = self._to_local(datetime.fromisoformat(last_used))
                if last_used_dt.date() == datetime.now().date():
                    last_used = last_used_dt.strftime('%m-%d-%Y %I:%M %p')
                else:
                    last_used = last_used_dt.strftime('%m-%d-%Y')
            path = md.get('path')
            usage = (
                f"[{RED}]{md.get('usage')}[/{RED}]" if md.get('usage') == 0 else
                f"[{YELLOW}]{md.get('usage')}[/{YELLOW}]" if md.get('usage') < 20 else
                f"[{GREEN}]{md.get('usage')}[/{GREEN}]")
            row = [
                alias,
                f"[{YELLOW}]{self._shorten_path(path)}[/{YELLOW}]" if path else '---',
                md.get('description') or '---',
                self._get_alias_age(md['created_at']),
                last_used or '---',
                usage,
            ]
            if show_all:
                if md.get('delete_info'):
                    row.append(f"[{RED}]D[/{RED}]")
                else:
                    row.append(f"[{GREEN}]A[/{GREEN}]")
            table.add_row(*row)
        console.print(table)

    def _create_table(self, show_all=False):
        table = Table(title="\n[bold]Alias List[/bold]\n", title_justify="center", caption="\n")

        table.add_column(header="[cyan][bold]Alias Name[/bold][/cyan]", min_width=5, max_width=15, no_wrap=True)
        table.add_column(header="[cyan][bold]Path[/bold][/cyan]", min_width=10, max_width=25, no_wrap=True)
        table.add_column(header="[cyan][bold]Description[/bold][/cyan]", min_width=10, max_width=30, no_wrap=True)
        table.add_column(header="[cyan][bold]Alias Age[/bold][/cyan]", max_width=20, no_wrap=True)
        table.add_column(header="[cyan][bold]Last Used[/bold][/cyan]", max_width=20, no_wrap=True)
        table.add_column(header="[cyan][bold]Usage[/bold][/cyan]", justify="center")
        if show_all:
            table.add_column(header="[cyan][bold]Status[/bold][/cyan]", justify="center")
        return table

    def _shorten_path(self, path_str):
        path = Path(path_str)
        try:
            relative = path.relative_to(Path.home())
            return "~/" + relative.as_posix()
        except ValueError:
            return path_str

    def _pluralize(self, n, unit):
        return f"{n} {unit}{'s' if n != 1 else ''}"

    def _days_to_human(self, days: int):
        if days == 0:
            return ""
        if days < 7:
            return self._pluralize(days, "day")
        if days < 42:
            return self._pluralize(round(days / 7), "week")
        return self._pluralize(round(days / 30.44), "month")

    def _get_alias_age(self, created_at: str):
        created = datetime.fromisoformat(created_at)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - created

        total_seconds = delta.total_seconds()
        total_minutes = total_seconds / 60
        total_hours = total_minutes / 60
        total_days = delta.days

        if total_seconds < 60:
            return f"[{GREEN}]{self._pluralize(round(total_seconds), 'second')}[/{GREEN}]"
        if total_minutes < 50:
            return f"[{GREEN}]{self._pluralize(round(total_minutes), 'minute')}[/{GREEN}]"
        if total_hours < 24:
            return f"[{GREEN}]{self._pluralize(max(1, round(total_hours)), 'hour')}[/{GREEN}]"
        if total_days < 7:
            return f"[{GREEN}]{self._pluralize(total_days, 'day')}[/{GREEN}]"
        if total_days < 42:
            return f"[{GREEN}]{self._pluralize(round(total_days / 7), 'week')}[/{GREEN}]"
        if total_days <= 366:
            return f"[{ORANGE}]{self._pluralize(round(total_days / 30.44), 'month')}[/{ORANGE}]"

        years = total_days // 365
        year_str = self._pluralize(years, "year")
        remainder = self._days_to_human(total_days - (years * 365))
        return f"[{RED}]{year_str} {remainder}[/{RED}]" if remainder else f"[{RED}]{year_str}[/{RED}]"

    ###### UPDATE METHODS ######
    def _get_alias(self, alias_name):
        alias = self.aliases.get(alias_name)
        if not alias or not self._is_active(alias):
            raise ValueError(f"'{alias_name}' does not exist")
        return alias

    def update_name(self, alias_name, new_name):
        self._get_alias(alias_name)
        if alias_name == new_name:
            console.print(f"\n[{YELLOW}]'{alias_name}' is already named that[/{YELLOW}]\n")
            return False
        existing = self.aliases.get(new_name)
        if existing and self._is_active(existing):
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

    def _soft_delete(self, alias_name, method):
        self.aliases[alias_name]["delete_info"] = {
            "deleted_at": str(datetime.now(timezone.utc).isoformat()),
            "method": method,
        }

    def delete_alias(self, alias_name, permanent=False):
        try:
            self._get_alias(alias_name)
            res = self._validate_input("\nAre you sure you want to delete? (y/N)")
            if res.lower() in ['yes', 'y', 'yeah', 'yea', 'ye']:
                if permanent:
                    del self.aliases[alias_name]
                else:
                    self._soft_delete(alias_name, "user_delete")
            else:
                console.print(f"\n[{YELLOW}]Deletion cancelled...[/{YELLOW}]\n")
                return
        except ValueError as e:
            console.print(f"\n[{YELLOW}]Error: {e}. No aliases were removed.[/{YELLOW}]")
            return

        with open(ALIASES_FILE, 'w') as f:
            json.dump(self.aliases, f, indent=4)

        console.print(f"\n[{YELLOW}]Successfully [underline]deleted[/underline] {alias_name}[/{YELLOW}]\n")

    ###### DOCTOR METHODS ######

    def doctor_paths(self, perm=False):
        active = {k: v for k, v in self.aliases.items() if self._is_active(v)}
        soft_deleted = {k: v for k, v in self.aliases.items() if not self._is_active(v)}
        invalid = {name for name, data in active.items()
                   if not Path(data.get("path", "")).exists()}

        if not active and not soft_deleted:
            console.print(f"\n[{GREEN}]No aliases found.[/{GREEN}]\n")
            return

        if active:
            self._print_doctor_scan_table(active, invalid, perm)

        if invalid:
            if perm:
                for name in invalid:
                    del self.aliases[name]
            else:
                for name in invalid:
                    self._soft_delete(name, "doctored")

        if perm and soft_deleted:
            self._print_doctor_purge_table(soft_deleted)
            for name in soft_deleted:
                del self.aliases[name]
        elif not perm and soft_deleted:
            console.print(f"[{YELLOW}]{len(soft_deleted)} soft-deleted alias(es) on record. Run with --perm-delete to purge permanently.[/{YELLOW}]\n")

        if invalid or (perm and soft_deleted):
            with open(ALIASES_FILE, "w") as f:
                json.dump(self.aliases, f, indent=4)

    def _print_doctor_scan_table(self, active, invalid, perm):
        table = Table(
            title="\n[bold]Doctor Report — Active Aliases[/bold]\n",
            title_justify="center",
            caption="\n"
        )
        table.add_column(header="[cyan][bold]Alias Name[/bold][/cyan]", min_width=5, max_width=15, no_wrap=True)
        table.add_column(header="[cyan][bold]Path[/bold][/cyan]", min_width=10, max_width=30, no_wrap=True)
        table.add_column(header="[cyan][bold]Description[/bold][/cyan]", min_width=10, max_width=25, no_wrap=True)
        table.add_column(header="[cyan][bold]Status[/bold][/cyan]", justify="center", min_width=12)

        for alias, data in active.items():
            path = data.get("path")
            if alias in invalid:
                status_label = "Perm. Deleted" if perm else "Soft-deleted"
                status = f"[{RED}]{status_label}[/{RED}]"
            else:
                status = f"[{GREEN}]Validated[/{GREEN}]"
            table.add_row(
                alias,
                f"[{YELLOW}]{self._shorten_path(path)}[/{YELLOW}]" if path else "---",
                data.get("description") or "---",
                status,
            )
        console.print(table)

    def _print_doctor_purge_table(self, soft_deleted):
        table = Table(
            title="\n[bold]Doctor Report — Purged Soft-Deleted Aliases[/bold]\n",
            title_justify="center",
            caption="\n"
        )
        table.add_column(header="[cyan][bold]Alias Name[/bold][/cyan]", min_width=5, max_width=15, no_wrap=True)
        table.add_column(header="[cyan][bold]Path[/bold][/cyan]", min_width=10, max_width=30, no_wrap=True)
        table.add_column(header="[cyan][bold]Description[/bold][/cyan]", min_width=10, max_width=25, no_wrap=True)
        table.add_column(header="[cyan][bold]Deleted On[/bold][/cyan]", max_width=20, no_wrap=True)
        table.add_column(header="[cyan][bold]Method[/bold][/cyan]", justify="center")

        for alias, data in soft_deleted.items():
            delete_info = data.get("delete_info") or {}
            deleted_at = delete_info.get("deleted_at")
            if deleted_at:
                deleted_at_dt = self._to_local(datetime.fromisoformat(deleted_at))
                deleted_at_str = deleted_at_dt.strftime('%m-%d-%Y %I:%M %p')
            else:
                deleted_at_str = "---"
            method = delete_info.get("method", "---")
            path = data.get("path")
            table.add_row(
                alias,
                f"[{YELLOW}]{self._shorten_path(path)}[/{YELLOW}]" if path else "---",
                data.get("description") or "---",
                deleted_at_str,
                f"[{TURQ}]{method}[/{TURQ}]",
            )
        console.print(table)

    def write_config(self):
        data = json.dumps(self.aliases, indent=4)
        with open(ALIASES_FILE, "w") as f:
            f.write(data)