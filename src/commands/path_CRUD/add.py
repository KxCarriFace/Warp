import sys
from src.commands.PathHandler import PathHandler
from src.globals import console, RED, YELLOW


#REGISTER COMMANDS/SUBCOMMANDS AND OPTIONS
def reg_add_cmd(subparsers):
    parser = subparsers.add_parser(
        "add",
        help="Add warp alias to [path] or current working directory"
    )
    parser.add_argument(
        "path",
        metavar="DIRECTORY_PATH",
        help="Path to the directory (use '.' for current directory)"
    )
    parser.add_argument(
        "alias",
        metavar="NEW_ALIAS_NAME",
        help="Name of the alias"
    )

    parser.add_argument(
        '-d', '--description',
        metavar="NEW_ALIAS_DESCRIPTION",
        help="Add a description before saving the alias"
    )


    parser.set_defaults(func=lambda args: add_alias(args, parser))

def add_alias(args, parser):
    alias_handler = PathHandler()
    try:
        alias_handler.add_new_alias(args.alias, args.path)

        if args.description:
            alias_handler.add_description(args.description)

        alias_handler.complete_add_transaction()

    except ValueError as e:
        console.print(f"\n[{RED}]{e}[/{RED}]\n")
        sys.exit(1)

    except KeyboardInterrupt:
        console.print(f"\n[{YELLOW}]Aborted procedure safely[/{YELLOW}]")
        sys.exit(1)

