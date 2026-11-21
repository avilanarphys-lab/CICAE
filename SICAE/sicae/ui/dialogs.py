"""Ventanas de diálogo reutilizables."""
import tkinter as tk
from tkinter import ttk
from .helpers import BG, make_modal


class FormDialog(tk.Toplevel):
    """Ventana modal sencilla para capturar datos."""
    def __init__(self, parent, title, fields, initial=None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.result = None
        self.values = {}
        body = tk.Frame(self, bg=BG, padx=22, pady=18)
        body.pack(fill="both", expand=True)
        for row, field in enumerate(fields):
            self._add_field(body, row, field, initial or {})
        self._add_buttons(body, len(fields))
        self.bind("<Return>", lambda event: self.submit())
        self.bind("<Escape>", lambda event: self.destroy())
        self._center_on(parent)
        make_modal(self, parent)
        if self.values:
            next(iter(self.values.values())).focus_set()

    def _add_field(self, body, row, field, initial):
        """Agrega una etiqueta y su campo (entrada de texto o combo)."""
        name, label, kind, options = (*field, None)[:4]
        tk.Label(body, text=label, bg=BG, fg="#334155",
                 font=("Segoe UI", 9, "bold")).grid(row=row, column=0, sticky="w", pady=7, padx=(0, 16))
        if kind == "combo":
            widget = ttk.Combobox(body, values=options or [], state="readonly", width=32)
            widget.set(initial.get(name) if initial.get(name) in (options or []) else (options or [""])[0])
        else:
            widget = ttk.Entry(body, width=35)
            widget.insert(0, str(initial.get(name, "")))
        widget.grid(row=row, column=1, sticky="ew", pady=7)
        self.values[name] = widget

    def _add_buttons(self, body, row):
        """Agrega los botones Guardar y Cancelar."""
        buttons = tk.Frame(body, bg=BG)
        buttons.grid(row=row, column=0, columnspan=2, sticky="e", pady=(18, 0))
        ttk.Button(buttons, text="Cancelar", command=self.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(buttons, text="Guardar", style="Accent.TButton", command=self.submit).pack(side="right")

    def _center_on(self, parent):
        """Centra el diálogo sobre la ventana padre."""
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 20)}+{max(y, 20)}")

    def submit(self):
        """Devuelve los valores ingresados y cierra el diálogo."""
        self.result = {name: widget.get().strip() for name, widget in self.values.items()}
        self.destroy()
