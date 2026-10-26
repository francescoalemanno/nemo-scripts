"""Funzioni condivise dalle finestre Python delle azioni Nemo."""

import os
import queue
import shutil
import subprocess
import sys
import threading
from collections.abc import Callable

try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    subprocess.run(["zenity", "--error", "--title=Nemo",
                    "--text=Serve il modulo tkinter di Python 3 (python3-tk)."])
    sys.exit(1)


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
        return
    os.unlink(result)


def selected_files() -> list[str]:
    return [os.path.abspath(path) for path in sys.argv[1:] if path]


def relative_names(files: list[str]) -> list[str]:
    if not files:
        return []
    root = os.path.commonpath([os.path.dirname(path) for path in files])
    return [os.path.relpath(path, root) for path in files]


def check_pdfs(files: list[str], minimum: int = 1) -> str | None:
    if len(files) < minimum:
        return "Seleziona almeno due PDF." if minimum > 1 else "Seleziona prima uno o più PDF in Nemo."
    for path in files:
        if not os.path.isfile(path) or not path.lower().endswith(".pdf"):
            return f"Selezione non valida: '{path}' non è un PDF."
    return None


def human_size(size: int) -> str:
    if size < 1024 * 1024:
        return f"{size / 1024:.0f} KB"
    return f"{size / (1024 * 1024):.1f} MB".replace(".", ",")


def choose_directory(parent: tk.Misc, initial: str) -> str | None:
    """Selettore di cartelle di zenity (più comodo di quello di Tk), se disponibile."""
    if shutil.which("zenity"):
        # zenity apre la cartella genitore di --filename, a meno che non termini con "/".
        process = subprocess.run(
            ["zenity", "--file-selection", "--directory", "--title=Scegli la cartella di destinazione",
             f"--filename={initial.rstrip('/')}/"],
            capture_output=True, text=True)
        path = process.stdout.strip()
        return path if process.returncode == 0 and path else None
    return filedialog.askdirectory(parent=parent, initialdir=initial, mustexist=True) or None


class Cancelled(Exception):
    pass


class Worker:
    """Esegue un lavoro in un thread separato; i messaggi arrivano alla finestra tramite una coda."""

    def __init__(self, root: tk.Misc, on_message: Callable, on_done: Callable[[BaseException | None], None]):
        self.root = root
        self.on_message = on_message
        self.on_done = on_done
        self.queue = queue.Queue()
        self.cancelled = threading.Event()
        self.process = None
        self.thread = None

    def start(self, target: Callable, *args) -> None:
        self.thread = threading.Thread(target=self._run, args=(target, *args), daemon=True)
        self.thread.start()
        self.root.after(100, self._poll)

    def running(self) -> bool:
        return self.thread is not None and self.thread.is_alive()

    def post(self, *message) -> None:
        self.queue.put(("message", message))

    def cancel(self) -> None:
        self.cancelled.set()
        process = self.process
        if process and process.poll() is None:
            process.terminate()

    def check(self) -> None:
        if self.cancelled.is_set():
            raise Cancelled()

    def run(self, args: list[str], on_line: Callable[[str], None] | None = None) -> None:
        """Avvia un comando; solleva RuntimeError con le ultime righe di output se fallisce."""
        self.check()
        tail = []
        self.process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        stdin=subprocess.DEVNULL, text=True, errors="replace")
        try:
            for line in self.process.stdout:
                tail = (tail + [line.rstrip()])[-20:]
                if on_line:
                    on_line(line)
            code = self.process.wait()
        finally:
            self.process = None
        self.check()
        if code != 0:
            raise RuntimeError("\n".join(tail).strip() or f"{args[0]} è terminato con codice {code}.")

    def _run(self, target: Callable, *args) -> None:
        try:
            target(self, *args)
        except BaseException as exc:  # noqa: BLE001 - riportato alla finestra
            self.queue.put(("done", exc))
        else:
            self.queue.put(("done", None))

    def _poll(self) -> None:
        try:
            while True:
                kind, payload = self.queue.get_nowait()
                if kind == "message":
                    self.on_message(*payload)
                else:
                    self.on_done(payload)
                    return
        except queue.Empty:
            pass
        except tk.TclError:
            return
        self.root.after(100, self._poll)
