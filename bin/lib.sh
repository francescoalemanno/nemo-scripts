#!/usr/bin/env bash

# Funzioni condivise dagli script avviati dalle azioni Nemo (i file arrivano come argomenti).
set -o pipefail

notify_error() {
    zenity --error --title="Script PDF/JPEG" --text="$*" 2>/dev/null || printf 'Errore: %s\n' "$*" >&2
}

notify_info() {
    zenity --info --title="Script PDF/JPEG" --text="$*" 2>/dev/null || true
}

notify_warning() {
    zenity --warning --title="Script PDF/JPEG" --text="$*" 2>/dev/null || printf 'Attenzione: %s\n' "$*" >&2
}

require_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        notify_error "Manca il programma richiesto: $1"
        exit 1
    fi
}

load_selection() {
    if (($# == 0)); then
        notify_error "Seleziona prima uno o più file in Nemo."
        exit 1
    fi
    files=("$@")
    local -a clean=()
    local file
    for file in "${files[@]}"; do
        [[ -n $file ]] && clean+=("$file")
    done
    files=("${clean[@]}")
    if ((${#files[@]} == 0)); then
        notify_error "Non è stato selezionato alcun file."
        exit 1
    fi
}

check_extensions() {
    local description=$1 pattern=$2 file
    for file in "${files[@]}"; do
        if [[ ! -f $file || ! $file =~ $pattern ]]; then
            notify_error "Selezione non valida: '$file' non è un $description."
            exit 1
        fi
    done
}

choose_output_directory() {
    # zenity apre la cartella genitore di --filename, a meno che non termini con "/".
    local default_path=${1%/}/
    zenity --file-selection --directory --title="Scegli la cartella di destinazione" \
        --filename="$default_path" 2>/dev/null
}

show_command_error() {
    local log=$1 title=${2:-"Operazione non riuscita"}
    local detail
    detail=$(tail -n 20 "$log" 2>/dev/null | sed 's/</\\</g; s/>/\\>/g')
    local message=$title
    [[ -n $detail ]] && message+=$'\n\n'"$detail"
    notify_error "$message"
}

selected_directory() {
    dirname -- "${files[0]}"
}
