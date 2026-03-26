from src.commands.PathHandler import PathHandler


def reg_doctor_cmd(subparsers):
    parser = subparsers.add_parser(
        "doctor-paths",
        help="Scan all aliases and soft-delete any whose paths no longer exist"
    )
    parser.add_argument(
        "--perm-delete",
        action="store_true",
        help="Permanently remove invalid paths and purge all previously soft-deleted aliases"
    )
    parser.set_defaults(func=doctor_paths)


def doctor_paths(args):
    handler = PathHandler()
    handler.doctor_paths(perm=args.perm_delete)
