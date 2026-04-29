#!/usr/bin/env bash

warp() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        warp_exe="$HOME/.usr/warp/warp.exe"
    else
        warp_exe="$HOME/.usr/warp/warp"
    fi

    case "$1" in
        to)
            shift
            dest="$("$warp_exe" to "$1")" || return 1
            cd "$dest" || return 1
            ;;
        *)
            "$warp_exe" "$@"
            ;;
    esac
}
