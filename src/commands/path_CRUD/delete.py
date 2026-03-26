from src.commands.PathHandler import PathHandler


def reg_delete_cmd(subparsers):
    parser = subparsers.add_parser(
        "delete",
        help="Delete an alias. Soft-deletes by default; use --permanent to remove it entirely."
    )

    parser.add_argument(
        "alias",
        metavar="ALIAS_NAME",
        help="Name of the alias to delete"
    )

    parser.add_argument(
        "-p", "--permanent",
        action="store_true",
        help="Permanently remove the alias with no recovery. Default is soft-delete."
    )

    parser.set_defaults(func=execute_delete)


def execute_delete(args):
    alias_handler = PathHandler()
    alias_handler.delete_alias(args.alias, permanent=args.permanent)
