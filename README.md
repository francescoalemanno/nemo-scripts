# Azioni PDF/JPEG per Nemo

Questa cartella contiene azioni per il menu contestuale di Nemo. Ogni azione compare solo quando la selezione è adatta (per esempio **PDF join** solo con almeno due PDF selezionati):

- **PDF join** — unisce almeno due PDF selezionati in un unico documento. Una finestra mostra l'elenco dei PDF: si riordinano trascinando le righe (oppure con Alt+↑/↓) e si sceglie il nome del file, che viene creato nella cartella del primo PDF selezionato.
- **PDF 2 JPEG** — converte tutte le pagine di uno o più PDF in JPEG a 150 dpi. Chiede una cartella di destinazione.
- **IMG 2 PDF** — crea un PDF multipagina dalle immagini selezionate (JPEG, PNG, GIF, BMP, TIFF e WebP). La stessa finestra di **PDF join** mostra le miniature: si riordinano le pagine trascinando le righe (oppure con Alt+↑/↓) e si sceglie il nome del PDF, che viene creato nella cartella della prima immagine selezionata. L'orientamento EXIF delle foto viene rispettato.
- **PDF reduce** — comprime uno o più PDF con Ghostscript verso una dimensione massima in KB (per ciascun PDF). Chiede il limite e salva automaticamente ogni risultato accanto al rispettivo originale come `nome-ridotto.pdf`. Prova progressivamente risoluzioni e qualità inferiori. Se il contenuto non può essere compresso abbastanza, salva il risultato più piccolo ottenuto e segnala che il limite non è stato raggiunto.
- **Bulk rename** — rinomina i file selezionati mantenendo l’estensione e usando il pattern `{stringa}{progressivo}.{estensione}`. Un unico dialog Python mostra l’anteprima aggiornata mentre si digita; il pulsante di rinomina conferma l’operazione. La numerazione parte da 1 e non vengono sovrascritti elementi già esistenti.
- **Apri Ghostty qui** — apre Ghostty nella cartella corrente dal menu sullo sfondo; **Apri Ghostty in questa cartella** apre la cartella selezionata dal menu contestuale della cartella.

I file di destinazione già presenti non vengono mai sovrascritti.

## Installazione

Da terminale:

```bash
cd ~/nemo-scripts
./install.sh
```

Le azioni (`actions/*.nemo_action`) vengono collegate in `~/.local/share/nemo/actions`, insieme al collegamento `nemo-scripts` → `bin/`: le azioni avviano i programmi con `Exec=<nemo-scripts/…>`, che Nemo risolve rispetto alla propria cartella delle azioni. L'installer rimuove anche i collegamenti in `~/.local/share/nemo/scripts` creati dalle versioni precedenti, quando le funzioni erano script. Se le azioni non compaiono subito, riavvia Nemo con `nemo -q`.

Ordine e sottomenu delle azioni si possono personalizzare con `nemo-action-layout-editor`.

## Struttura

- `actions/` — file `.nemo_action` (nome, icona, tipi di file e selezione richiesti)
- `bin/` — i programmi avviati dalle azioni; ricevono i file selezionati come argomenti, quindi si possono anche usare da terminale (per esempio `bin/pdf-join a.pdf b.pdf`)
  - `merge_dialog.py` — la finestra con lista riordinabile condivisa da **PDF join** e **IMG 2 PDF**
  - `lib.sh` — funzioni comuni agli script bash (dialoghi zenity, controlli sulla selezione)

## Disinstallazione

```bash
cd ~/nemo-scripts
./uninstall.sh
```

La disinstallazione rimuove solo i collegamenti creati da questo installer (che puntano a questa cartella); i file sorgenti in `~/nemo-scripts` restano al loro posto.

## Dipendenze

- `zenity` per le finestre di dialogo
- `poppler-utils` (`pdfunite` e `pdftoppm`)
- `ghostscript` (`gs`)
- `python3` con Pillow (`python3-pil` e `python3-pil.imagetk` sui sistemi Debian/Ubuntu)
- `python3-tk` per le finestre di **PDF join**, **IMG 2 PDF** e **Bulk rename** (sui sistemi Debian/Ubuntu)

Su Debian/Ubuntu, se necessario:

```bash
sudo apt install zenity poppler-utils ghostscript python3-pil python3-pil.imagetk python3-tk
```
