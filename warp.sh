warp() {
    local warp_python="$HOME/Documents/github/warp/.venv/Scripts/python.exe"
    local warp_cli="$HOME/Documents/github/warp/main.py"

    if [ "$1" = "to" ]; then
        shift

        if [ -z "$1" ]; then
            echo "Usage: warp to <alias>" >&2
            return 1
        fi

        local dest
        dest="$("$warp_python" "$warp_cli" resolve "$1")" || return 1

        if [ -z "$dest" ]; then
            echo "No path returned for alias '$1'." >&2
            return 1
        fi

        cd "$dest" || return 1
        return 0
    fi

    "$warp_python" "$warp_cli" "$@"
}