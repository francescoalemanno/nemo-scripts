# Azioni PDF/JPEG per Nemo

Questa cartella contiene azioni per il menu contestuale di Nemo. Ogni azione compare solo quando la selezione è adatta (per esempio **PDF join** solo con almeno due PDF selezionati):

- **PDF join** — unisce almeno due PDF selezionati in un unico documento. Una finestra mostra l'elenco dei PDF: si riordinano trascinando le righe (oppure con Alt+↑/↓) e si sceglie il nome del file, che viene creato nella cartella del primo PDF selezionato.
- **PDF 2 IMG** — converte le pagine di uno o più PDF in immagini. Una finestra permette di scegliere formato (JPEG o PNG), risoluzione in dpi, qualità JPEG, intervallo di pagine e cartella di destinazione (predefinita: quella del primo PDF). Le immagini si chiamano `nome-<pagina>.jpg` e vengono salvate solo se nessuna esiste già; la conversione si può interrompere.
- **IMG 2 PDF** — crea un PDF multipagina dalle immagini selezionate (JPEG, PNG, GIF, BMP, TIFF e WebP). La stessa finestra di **PDF join** mostra le miniature: si riordinano le pagine trascinando le righe (oppure con Alt+↑/↓) e si sceglie il nome del PDF, che viene creato nella cartella della prima immagine selezionata. L'orientamento EXIF delle foto viene rispettato.
- **PDF reduce** — comprime uno o più PDF con Ghostscript. Nella finestra si sceglie tra una **dimensione massima** in KB per ciascun PDF (cerca la risoluzione e la qualità JPEG più alte che rientrano nel limite) e le **impostazioni manuali** (risoluzione delle immagini e qualità JPEG); in entrambi i casi si può convertire in scala di grigi e scegliere il suffisso del nome (predefinito `nome-ridotto.pdf`, accanto all'originale). La tabella mostra per ogni file la dimensione ottenuta. Se il limite non si può raggiungere viene salvato il risultato più piccolo, segnalandolo; se la compressione non rende il file più piccolo dell'originale, non viene creato nulla.
- **Bulk rename** — rinomina i file selezionati mantenendo l’estensione e usando il pattern `{stringa}{progressivo}.{estensione}` (se la stringa è vuota, solo `{progressivo}.{estensione}`). Un unico dialog Python mostra l’anteprima aggiornata mentre si digita; il pulsante di rinomina conferma l’operazione. La numerazione parte da 1 e non vengono sovrascritti elementi già esistenti.
- **Apri Ghostty qui** — apre Ghostty nella cartella corrente dal menu sullo sfondo; **Apri Ghostty in questa cartella** apre la cartella selezionata dal menu contestuale della cartella.

I file di destinazione già presenti non vengono mai sovrascritti.

## Installazione

Il progetto è su GitHub: <https://github.com/francescoalemanno/nemo-scripts>. Da terminale:

```bash
git clone https://github.com/francescoalemanno/nemo-scripts.git ~/nemo-scripts
cd ~/nemo-scripts
./install.sh
```

La cartella clonata va lasciata al suo posto, perché l'installer crea collegamenti che puntano ai suoi file (si può clonare anche altrove, purché si avvii `./install.sh` da lì).

Le azioni (`actions/*.nemo_action`) vengono collegate in `~/.local/share/nemo/actions`, insieme al collegamento `nemo-scripts` → `bin/`: le azioni avviano i programmi con `Exec=<nemo-scripts/…>`, che Nemo risolve rispetto alla propria cartella delle azioni. L'installer rimuove anche i collegamenti in `~/.local/share/nemo/scripts` creati dalle versioni precedenti, quando le funzioni erano script. Se le azioni non compaiono subito, riavvia Nemo con `nemo -q`.

Ordine e sottomenu delle azioni si possono personalizzare con `nemo-action-layout-editor`.

## Struttura

- `actions/` — file `.nemo_action` (nome, icona, tipi di file e selezione richiesti)
- `bin/` — i programmi avviati dalle azioni; ricevono i file selezionati come argomenti, quindi si possono anche usare da terminale (per esempio `bin/pdf-join a.pdf b.pdf`)
  - `merge_dialog.py` — la finestra con lista riordinabile condivisa da **PDF join** e **IMG 2 PDF**
  - `nemo_common.py` — funzioni comuni: lavoro in background interrompibile, salvataggio senza sovrascrivere, selettore di cartelle

## Aggiornamento

```bash
cd ~/nemo-scripts
git pull
./install.sh
```

Rieseguire l'installer collega le azioni nuove e rimuove i collegamenti a quelle eliminate.

## Disinstallazione

```bash
cd ~/nemo-scripts
./uninstall.sh
```

La disinstallazione rimuove solo i collegamenti creati da questo installer (che puntano a questa cartella); i file sorgenti nella cartella clonata restano al loro posto (si possono poi cancellare a mano).

## Dipendenze

- `zenity` (facoltativo) per il selettore di cartelle di **PDF 2 IMG**
- `poppler-utils` (`pdfunite`, `pdftoppm` e `pdfinfo`)
- `ghostscript` (`gs`)
- `python3` con Pillow (`python3-pil` e `python3-pil.imagetk` sui sistemi Debian/Ubuntu)
- `python3-tk` per le finestre di tutte le azioni (sui sistemi Debian/Ubuntu)

Su Debian/Ubuntu, se necessario:

```bash
sudo apt install zenity poppler-utils ghostscript python3-pil python3-pil.imagetk python3-tk
```
