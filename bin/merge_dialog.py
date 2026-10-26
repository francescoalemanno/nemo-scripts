"""Finestra condivisa: crea un PDF da più file, nell'ordine scelto trascinando le righe."""

import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except ImportError:
    subprocess.run(["zenity", "--error", "--title=Nemo",
                    "--text=Serve il modulo tkinter di Python 3 (python3-tk)."])
    sys.exit(1)

THUMBNAIL_SIZE = 56


def publish(result: str, output: str) -> None:
    """Sposta result in output senza mai sovrascrivere un file esistente."""
    try:
        # link() fallisce se la destinazione esiste.
        os.link(result, output)
    except FileExistsError:
        raise
    except OSError:
        # File system senza hard link (es. FAT/exFAT).
        if os.path.lexists(output):
            raise FileExistsError(output)
        os.rename(result, output)


def run(*, title: str, files: list[str], list_label: str, default_name: str,
        check_selection: Callable[[list[str]], str | None],
        create: Callable[[list[str], str], None],
        thumbnail: Callable[[str, int], object] | None = None) -> None:
    """Mostra la finestra; create(percorsi_ordinati, destinazione) scrive il PDF
    oppure solleva RuntimeError con un messaggio per l'utente."""
    # Il PDF viene creato nella cartella del primo file selezionato.
    output_dir = os.path.dirname(files[0]) if files else os.getcwd()
    selection_root = os.path.commonpath([os.path.dirname(path) for path in files]) if files else os.getcwd()

    root = tk.Tk()
    root.title(title)
    root.minsize(560, 380)
    root.geometry("760x520")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    error = check_selection(files)
    if error:
        root.withdraw()
        messagebox.showerror(title, error, parent=root)
        root.destroy()
        sys.exit(1)

    main = ttk.Frame(root, padding=12)
    main.grid(row=0, column=0, sticky="nsew")
    main.columnconfigure(0, weight=1)
    main.rowconfigure(0, weight=1)

    list_frame = ttk.LabelFrame(main, text=f"{list_label} (trascina le righe per riordinare, oppure Alt+↑/↓)",
                                padding=6)
    list_frame.grid(row=0, column=0, sticky="nsew")
    list_frame.columnconfigure(0, weight=1)
    list_frame.rowconfigure(0, weight=1)

    style = ttk.Style(root)
    if thumbnail:
        style.configure("Merge.Treeview", rowheight=THUMBNAIL_SIZE + 8)
    tree = ttk.Treeview(list_frame, columns=("position", "name"), style="Merge.Treeview",
                        show="tree headings" if thumbnail else "headings", selectmode="browse")
    tree.column("#0", width=THUMBNAIL_SIZE + 24, minwidth=THUMBNAIL_SIZE + 24, stretch=False, anchor="center")
    tree.heading("position", text="#")
    tree.heading("name", text="Percorso relativo")
    tree.column("position", width=48, minwidth=40, stretch=False, anchor="e")
    tree.column("name", width=560, anchor="w")
    scroll_y = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll_y.set)
    tree.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")

    # Ogni riga usa l'indice nella selezione originale come identificativo.
    for index, path in enumerate(files):
        tree.insert("", "end", iid=str(index), values=("", os.path.relpath(path, selection_root)))

    name_frame = ttk.Frame(main)
    name_frame.grid(row=1, column=0, sticky="ew", pady=(12, 0))
    name_frame.columnconfigure(1, weight=1)
    ttk.Label(name_frame, text="Nome del file").grid(row=0, column=0, sticky="w", padx=(0, 8))
    name_var = tk.StringVar(value=default_name)
    entry = ttk.Entry(name_frame, textvariable=name_var)
    entry.grid(row=0, column=1, sticky="ew")
    ttk.Label(name_frame, text=".pdf").grid(row=0, column=2, sticky="w", padx=(4, 0))

    status_var = tk.StringVar()
    ttk.Label(main, textvariable=status_var, wraplength=720).grid(row=2, column=0, sticky="w", pady=(10, 0))

    buttons = ttk.Frame(main)
    buttons.grid(row=3, column=0, sticky="e", pady=(12, 0))
    create_button = ttk.Button(buttons, text=f"Crea PDF ({len(files)} file)", state="disabled")
    create_button.pack(side="right", padx=(8, 0))
    ttk.Button(buttons, text="Annulla", command=root.destroy).pack(side="right")

    state = {"output": None, "drag": None}
    thumbnails = {}

    def renumber() -> None:
        for position, item in enumerate(tree.get_children(), start=1):
            tree.set(item, "position", position)

    def update_status(*_args) -> None:
        state["output"] = None
        name = name_var.get().strip()
        if name.lower().endswith(".pdf"):
            name = name[:-4]
        if not name or name in (".", "..") or "/" in name or "\n" in name or "\r" in name:
            status_var.set("Inserisci un nome valido, senza '/' o ritorni a capo.")
            create_button.configure(state="disabled")
            return
        output = os.path.join(output_dir, f"{name}.pdf")
        if os.path.lexists(output):
            status_var.set(f"Esiste già e non verrà sovrascritto: {output}")
            create_button.configure(state="disabled")
            return
        state["output"] = output
        status_var.set(f"Verrà creato: {output}")
        create_button.configure(state="normal")

    def on_press(event) -> None:
        state["drag"] = tree.identify_row(event.y) or None
        if state["drag"]:
            tree.selection_set(state["drag"])
            tree.focus(state["drag"])

    def on_motion(event) -> None:
        item = state["drag"]
        if not item:
            return
        tree.configure(cursor="sb_v_double_arrow")
        # Scorre la lista quando si trascina vicino ai bordi.
        if event.y < 12:
            tree.yview_scroll(-1, "units")
        elif event.y > tree.winfo_height() - 12:
            tree.yview_scroll(1, "units")
        target = tree.identify_row(event.y)
        if target and target != item:
            tree.move(item, "", tree.index(target))
            renumber()

    def on_release(_event) -> None:
        state["drag"] = None
        tree.configure(cursor="")

    def move_selected(offset: int) -> str:
        selected = tree.selection()
        if selected:
            item = selected[0]
            tree.move(item, "", max(0, min(len(files) - 1, tree.index(item) + offset)))
            tree.see(item)
            renumber()
        return "break"

    def load_thumbnail(index: int = 0) -> None:
        # Una miniatura per ciclo, così la finestra resta reattiva.
        if index >= len(files):
            return
        try:
            image = thumbnail(files[index], THUMBNAIL_SIZE)
        except Exception:
            image = None
        if image is not None:
            thumbnails[index] = image
            tree.item(str(index), image=image)
        root.after_idle(load_thumbnail, index + 1)

    def confirm(*_args) -> None:
        output = state["output"]
        if output is None:
            return
        root.configure(cursor="watch")
        create_button.configure(state="disabled")
        status_var.set("Creazione del PDF in corso…")
        root.update_idletasks()
        workdir = None
        try:
            workdir = tempfile.mkdtemp(prefix=".merge-pdf.", dir=output_dir)
            result = os.path.join(workdir, "risultato.pdf")
            create([files[int(item)] for item in tree.get_children()], result)
            if not os.path.isfile(result) or os.path.getsize(result) == 0:
                raise RuntimeError("Il PDF creato è vuoto.")
            publish(result, output)
        except FileExistsError:
            root.configure(cursor="")
            update_status()
            return
        except (OSError, RuntimeError) as exc:
            root.configure(cursor="")
            update_status()
            messagebox.showerror(title, str(exc), parent=root)
            return
        finally:
            if workdir:
                shutil.rmtree(workdir, ignore_errors=True)
        root.configure(cursor="")
        messagebox.showinfo(title, f"PDF creato:\n{output}", parent=root)
        root.destroy()

    tree.bind("<ButtonPress-1>", on_press)
    tree.bind("<B1-Motion>", on_motion)
    tree.bind("<ButtonRelease-1>", on_release)
    root.bind("<Alt-Up>", lambda _event: move_selected(-1))
    root.bind("<Alt-Down>", lambda _event: move_selected(1))
    root.bind("<Return>", confirm)
    root.bind("<Escape>", lambda _event: root.destroy())
    create_button.configure(command=confirm)
    name_var.trace_add("write", update_status)

    renumber()
    tree.selection_set("0")
    update_status()
    entry.focus_set()
    entry.select_range(0, "end")
    if thumbnail:
        root.after(50, load_thumbnail)
    root.mainloop()
