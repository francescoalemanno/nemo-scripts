#!/usr/bin/env bash
set -euo pipefail
ROOT=$(dirname -- "$(readlink -f -- "$0")")
DATA_HOME=${XDG_DATA_HOME:-"$HOME/.local/share"}
ACTION_DEST="$DATA_HOME/nemo/actions"
SCRIPT_DEST="$DATA_HOME/nemo/scripts"
# Le azioni usano Exec=<nemo-scripts/...>: Nemo cerca l'eseguibile relativo
# alla cartella delle azioni, quindi lì serve un collegamento a bin/.
HELPER_LINK="$ACTION_DEST/nemo-scripts"

# Vero se $1 è un link simbolico che punta dentro questa cartella (anche se ormai
# interrotto, come i collegamenti creati dalle versioni precedenti).
points_into_root() {
    local link
    [[ -L $1 ]] && link=$(readlink -- "$1") && [[ $link == "$ROOT/"* ]]
}

abort_unmanaged() {
    printf 'Installazione interrotta: esiste già un elemento non gestito da questo installer:\n  %s\n' "$1" >&2
    exit 1
}

shopt -s nullglob
actions=("$ROOT"/actions/*.nemo_action)
shopt -u nullglob
((${#actions[@]} > 0)) || { printf 'Nessuna azione trovata in %s/actions\n' "$ROOT" >&2; exit 1; }

# Non sostituire file o azioni preesistenti che non appartengono a questa cartella.
# Un'azione installata a mano viene adottata se è identica al sorgente.
for source in "${actions[@]}"; do
    target="$ACTION_DEST/$(basename -- "$source")"
    if [[ -e $target || -L $target ]] && ! points_into_root "$target" \
        && ! { [[ -f $target && ! -L $target ]] && cmp -s -- "$source" "$target"; }; then
        abort_unmanaged "$target"
    fi
done
if [[ -e $HELPER_LINK || -L $HELPER_LINK ]] && ! points_into_root "$HELPER_LINK"; then
    abort_unmanaged "$HELPER_LINK"
fi

mkdir -p -- "$ACTION_DEST"
for file in "$ROOT"/bin/*; do
    [[ $file == *.py ]] || chmod +x -- "$file"
done
ln -sfn -- "$ROOT/bin" "$HELPER_LINK"

declare -A current=()
for source in "${actions[@]}"; do
    name=$(basename -- "$source")
    current[$name]=1
    target="$ACTION_DEST/$name"
    if [[ -f $target && ! -L $target ]]; then
        rm -- "$target"
    fi
    ln -sfn -- "$source" "$target"
done

# Rimuove le azioni non più presenti in questa cartella e i vecchi script Nemo,
# ora sostituiti dalle azioni.
for target in "$ACTION_DEST"/*.nemo_action "$SCRIPT_DEST"/*; do
    [[ -L $target ]] || continue
    [[ $target == "$ACTION_DEST"/* && -n ${current[$(basename -- "$target")]+x} ]] && continue
    if points_into_root "$target"; then
        rm -- "$target"
        printf 'Rimosso collegamento obsoleto: %s\n' "$target"
    fi
done

printf 'Azioni Nemo installate in:\n  %s\n\nSe non compaiono subito nel menu contestuale, riavvia Nemo (nemo -q).\n' "$ACTION_DEST"
