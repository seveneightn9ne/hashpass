#!/usr/bin/env bash
set -u # Error on undefined variables.

if [ $# -le 1 ]; then
    echo "Usage: $0 time text"
    exit 1
fi

LIFETIME="$1"
shift
PAYLOAD="$*"

die() {
    echo "$@" >&2
    exit 1
}

sleep_argv0="hashpass sleep on display $DISPLAY"
pkill -f "^$sleep_argv0" 2>/dev/null && sleep 0.2
echo -n "$PAYLOAD" | xclip -selection clipboard || die "Error: Could not copy data to the clipboard"
(
    ( exec -a "$sleep_argv0" sleep "$LIFETIME" )
    qdbus org.kde.klipper /klipper org.kde.klipper.klipper.clearClipboardHistory &>/dev/null
    echo -n "" | xclip -selection clipboard
) 2>/dev/null & disown
