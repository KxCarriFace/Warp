def reg_delete_cmd(subparsers):
    parser = subparsers.add_parser(
        "delete",
        help="Delete any alias of your choosing."
    )

    parser.add_argument(
        "alias",
        metavar="ALIAS_NAME",
        help="Required. Name of alias to delete. Not reversible."
    )

    parser.set_defaults(func=execute_delete)


from src.commands.PathHandler import PathHandler

def execute_delete(args):
    alias_handler = PathHandler()

    alias_handler.delete_alias(args.alias)