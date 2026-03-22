import sys
from src.commands.PathHandler import PathHandler


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
    handler = PathHandler()

    try:
        alias_data = handler._get_alias(args.alias)
    except ValueError:
        print(f"Alias '{args.alias}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        resolved = handler._validate_path(alias_data["path"])
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    print(resolved.as_posix())
