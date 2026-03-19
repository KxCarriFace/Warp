import argparse
from src.commands.path_CRUD.add import reg_add_cmd
from src.commands.path_CRUD.read import reg_read_cmd
from src.commands.path_NAV.to import reg_to_cmd
from src.commands.path_CRUD.update import reg_update_cmd

def main():
    parser = argparse.ArgumentParser(
        prog="Warp",
        description="Warp through your file system with aliases placed by you",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    reg_add_cmd(subparsers)
    reg_read_cmd(subparsers)
    reg_update_cmd(subparsers)

    reg_to_cmd(subparsers)

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()
