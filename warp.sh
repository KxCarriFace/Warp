#!/usr/bin/env bash

warp() {
    warp_python_exe="$HOME/.usr/warp/.venv/Scripts/python.exe"
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