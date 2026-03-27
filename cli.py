import argparse
from src.commands.path_CRUD.add import reg_add_cmd
from src.commands.path_CRUD.read import reg_read_cmd
from src.commands.path_NAV.to import reg_to_cmd
from src.commands.path_CRUD.update import reg_update_cmd
from src.commands.path_CRUD.delete import reg_delete_cmd
from src.commands.path_CRUD.doctor import reg_doctor_cmd
from src.commands.update import reg_update_cmd as reg_updater_cmd, check_for_update
from src.globals import console, YELLOW

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
    reg_delete_cmd(subparsers)
    reg_to_cmd(subparsers)
    reg_doctor_cmd(subparsers)
    reg_updater_cmd(subparsers)

    args = parser.parse_args()

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("Operation aborted...")

    if args.command != "update":
        new_version = check_for_update()
        if new_version:
            console.print(f"\n[{YELLOW}]A new version (v{new_version}) is available. Run [bold]warp update[/bold] to install.[/{YELLOW}]")

    


if __name__ == "__main__":
    main()
