import sys
from src.commands.PathHandler import PathHandler
from src.globals import console, RED, YELLOW


def reg_update_cmd(subparsers):
    parser = subparsers.add_parser(
        'edit',
        help="Edit an existing alias"
    )

    parser.add_argument(
        'alias_name',
        metavar="ALIAS_NAME",
        help="Name of the alias being updated"
    )

    parser.add_argument(
        "-n", "--name",
        metavar="NEW_ALIAS_NAME",
        help="New name to be given to the alias"
    )

    parser.add_argument(
        "-p", "--path",
        metavar="DIRECTORY_PATH",
        help="Path to update the alias to (use '.' for current directory)"
    )

    parser.add_argument(
        "-d", "--description",
        metavar="NEW_DESCRIPTION",
        help="Replace the current description with a new one"
    )

    parser.set_defaults(func=lambda args: update_alias(args, parser))


def update_alias(args, parser):
    if not any([args.name, args.path, args.description]):
        parser.error("At least one of -n, -p, or -d must be provided")

    alias_handler = PathHandler()
    try:
        changed = False
        current_name = args.alias_name

        if args.name:
            name_changed = alias_handler.update_name(current_name, args.name)
            if name_changed:
                changed = True
                current_name = args.name
        if args.path:
            path_changed = alias_handler.update_path(current_name, args.path)
            if path_changed:
                changed = True
        if args.description:
            alias_handler.update_description(current_name, args.description)
            changed = True

        if changed:
            alias_handler.complete_update_transaction(current_name)

    except ValueError as e:
        console.print(f"\n[{RED}]{e}[/{RED}]\n")
        sys.exit(1)

    except KeyboardInterrupt:
        console.print(f"\n[{YELLOW}]Aborted procedure safely[/{YELLOW}]")
        sys.exit(1)
