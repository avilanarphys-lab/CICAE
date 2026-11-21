"""Panel de inicio con los indicadores principales."""
import tkinter as tk
from tkinter import ttk
from .helpers import BG, NAVY, MUTED, WHITE
from .. import services

CARDS = (("students", "Estudiantes"), ("courses", "Asignaturas"),
         ("enrollments", "Inscripciones"), ("attendance_rate", "Asistencia"))
WELCOME_BG = "#E8EEFF"


class DashboardPage(tk.Frame):
    """Pantalla de bienvenida con indicadores generales."""
    def __init__(self, parent, on_start):
        super().__init__(parent, bg=BG)
        self.values = {}
        tk.Label(self, text="Resumen general", bg=BG, fg=NAVY,
                 font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(self, text="Indicadores principales de tu gestión académica.",
                 bg=BG, fg=MUTED).pack(anchor="w", pady=(4, 22))
        self._build_cards()
        self._build_welcome(on_start)

    def _build_cards(self):
        """Crea una tarjeta por indicador."""
        cards = tk.Frame(self, bg=BG)
        cards.pack(fill="x")
        for key, title in CARDS:
            card = tk.Frame(cards, bg=WHITE, padx=18, pady=18, highlightbackground="#E2E8F0", highlightthickness=1)
            card.pack(side="left", fill="x", expand=True, padx=(0, 12))
            tk.Label(card, text=title.upper(), bg=WHITE, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w")
            self.values[key] = tk.Label(card, text="0", bg=WHITE, fg=NAVY, font=("Segoe UI", 25, "bold"))
            self.values[key].pack(anchor="w", pady=(8, 0))

    def _build_welcome(self, on_start):
        """Crea el mensaje de bienvenida y el botón de inicio."""
        welcome = tk.Frame(self, bg=WELCOME_BG, padx=22, pady=22)
        welcome.pack(fill="x", pady=24)
        tk.Label(welcome, text="Organiza tu actividad académica desde un solo lugar",
                 bg=WELCOME_BG, fg=NAVY, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(welcome, text="Administra estudiantes, asignaturas, evaluaciones y asistencia. "
                 "La información se guarda localmente en una base de datos SQLite.",
                 bg=WELCOME_BG, fg="#52627A", wraplength=720, justify="left").pack(anchor="w", pady=(8, 0))
        ttk.Button(self, text="Comenzar con estudiantes", style="Accent.TButton",
                   command=on_start).pack(anchor="w")

    def refresh(self):
        """Actualiza los indicadores."""
        stats = services.dashboard_stats()
        for key, label in self.values.items():
            label.configure(text=f"{stats[key]:.1f}%" if key == "attendance_rate" else str(stats[key]))
