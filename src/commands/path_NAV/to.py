import sys
from datetime import datetime
from src.commands.PathHandler import PathHandler
from rich.console import Console

console = Console(stderr=True)

def reg_to_cmd(subparsers):
    parser = subparsers.add_parser(
        "to",
        help="Warp to an alias"
    )
    parser.add_argument(
        "alias",
        metavar="ALIAS",
        help="Alias name to warp to"
    )
    parser.set_defaults(func=handle_to)


def handle_to(args):
    if not args.alias:
        console.print("\nAn alias is required to warp through the file system.\n")
        sys.exit(1)

    handler = PathHandler()

    try:
        alias_data = handler._get_alias(args.alias)
    except ValueError as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        sys.exit(1)

    try:
        resolved = handler._validate_path(alias_data["path"])
    except ValueError as e:
        console.print(f"\n[red]{e}[/red]\n")
        sys.exit(1)
    print(resolved)
    alias_data['usage'] += 1
    #TODO fix datetime so it prints as a string
    alias_data['last_used'] = datetime.now()
    handler.write_config()

    sys.exit(0)