#!/usr/bin/env bash

warp() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        warp_python_exe="$HOME/.usr/warp/.venv/Scripts/python.exe"
    else
        warp_python_exe="$HOME/.usr/warp/.venv/bin/python"
    fi
    warp_cli_handler="$HOME/.usr/warp/cli.py"

case "$1" in
    to)
        shift

        dest="$("$warp_python_exe" "$warp_cli_handler" to "$1")" || return 1

        cd "$dest" || return 1
        ;;
    *)
        "$warp_python_exe" "$warp_cli_handler" "$@"
        ;;
esac
}