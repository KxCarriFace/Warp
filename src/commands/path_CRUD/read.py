from src.commands.PathHandler import PathHandler

def reg_read_cmd(subparsers):
    parser = subparsers.add_parser(
        "list",
        help="Read all aliases stored and their metadata"
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--alias",
        metavar="ALIAS_NAME",
        help="Provides specific alias to display only"
    )

    group.add_argument(
        "-s", "--search",
        metavar="SEARCH_STRING",
        help="Provides all aliases that match the search criteria"
    )

    parser.set_defaults(func=read_alias)


def read_alias(args):
    alias_handler = PathHandler()

    alias_handler.read_aliases(alias_name=args.alias, search_val=args.search)
    