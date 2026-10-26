#!/usr/bin/env bash
set -euo pipefail
ROOT=$(dirname -- "$(readlink -f -- "$0")")
DATA_HOME=${XDG_DATA_HOME:-"$HOME/.local/share"}
ACTION_DEST="$DATA_HOME/nemo/actions"
SCRIPT_DEST="$DATA_HOME/nemo/scripts"

# Vero se $1 è un link simbolico che punta dentro questa cartella.
points_into_root() {
    local link
    [[ -L $1 ]] && link=$(readlink -- "$1") && [[ $link == "$ROOT/"* ]]
}

# Rimuove i collegamenti creati da questo installer, compresi quelli delle
# versioni precedenti (vecchi script in nemo/scripts).
for target in "$ACTION_DEST"/*.nemo_action "$ACTION_DEST/nemo-scripts" "$SCRIPT_DEST"/*; do
    if points_into_root "$target"; then
        rm -- "$target"
        printf 'Rimosso: %s\n' "$target"
    fi
done
for source in "$ROOT"/actions/*.nemo_action; do
    target="$ACTION_DEST/$(basename -- "$source")"
    if [[ -e $target || -L $target ]]; then
        printf 'Non rimosso (non è un link installato da questo installer): %s\n' "$target"
    fi
done
printf 'Disinstallazione completata. I file in %s sono rimasti intatti.\n' "$ROOT"
