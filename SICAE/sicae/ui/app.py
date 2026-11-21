"""Ventana principal y navegación de SICAE."""
import tkinter as tk
import traceback
from ..database import initialize_database
from .helpers import BG, NAVY, NAVY_LIGHT, WHITE, MUTED, configure_style, show_error
from .dashboard import DashboardPage
from .students import StudentsPage
from .courses import CoursesPage
from .grades import GradesPage
from .attendance import AttendancePage
from .reports import ReportsPage

NAV_ITEMS = (("Inicio", "⌂"), ("Estudiantes", "♙"), ("Asignaturas", "▤"),
             ("Calificaciones", "✓"), ("Asistencia", "◷"), ("Reportes", "▥"))


class SicaeApp(tk.Tk):
    """Aplicación principal de escritorio."""
    def __init__(self):
        super().__init__()
        initialize_database()
        self.title("SICAE | Gestión académica")
        self.geometry("1180x760")
        self.minsize(980, 650)
        self.configure(bg=BG)
        configure_style(self)
        self.pages = {}
        self.factories = {
            "Inicio": lambda parent: DashboardPage(parent, lambda: self.show_page("Estudiantes")),
            "Estudiantes": StudentsPage, "Asignaturas": CoursesPage,
            "Calificaciones": GradesPage, "Asistencia": AttendancePage, "Reportes": ReportsPage,
        }
        self._build_sidebar()
        self._build_content()
        self.show_page("Inicio")

    def report_callback_exception(self, exc_type, exc_value, exc_traceback):
        """Muestra cualquier error inesperado en una ventana en lugar de cerrar el programa."""
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        show_error(self, exc_value)

    def _build_sidebar(self):
        """Construye la barra lateral con marca y navegación."""
        self.sidebar = tk.Frame(self, bg=NAVY, width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        brand = tk.Frame(self.sidebar, bg=NAVY, padx=20, pady=24)
        brand.pack(fill="x")
        tk.Label(brand, text="SICAE", bg=NAVY, fg=WHITE, font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(brand, text="GESTIÓN ACADÉMICA", bg=NAVY, fg="#AFC0D8",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(2, 0))
        tk.Frame(self.sidebar, bg="#34445C", height=1).pack(fill="x", padx=16, pady=(0, 14))
        self.nav_buttons = {name: self._nav_button(name, symbol) for name, symbol in NAV_ITEMS}
        tk.Label(self.sidebar, text="Versión 1.0 · Proyecto académico", bg=NAVY, fg="#91A2BA",
                 font=("Segoe UI", 8), wraplength=190, justify="left").pack(side="bottom", anchor="w", padx=20, pady=20)

    def _nav_button(self, name, symbol):
        """Crea un botón de navegación de la barra lateral."""
        button = tk.Button(self.sidebar, text=f"  {symbol}     {name}", anchor="w",
                           command=lambda: self.show_page(name), bg=NAVY, fg="#D8E2F0",
                           activebackground=NAVY_LIGHT, activeforeground=WHITE, relief="flat", bd=0,
                           font=("Segoe UI", 10, "bold"), padx=18, pady=13, cursor="hand2")
        button.pack(fill="x", padx=10, pady=2)
        return button

    def _build_content(self):
        """Construye el encabezado y el área donde se muestran las pantallas."""
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)
        header = tk.Frame(self.content, bg=WHITE, height=58)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="Panel del docente", bg=WHITE, fg=NAVY,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=28)
        tk.Label(header, text="SICAE  /  Control académico", bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="right", padx=28)
        self.page_area = tk.Frame(self.content, bg=BG, padx=28, pady=24)
        self.page_area.pack(fill="both", expand=True)

    def show_page(self, name):
        """Muestra la pantalla seleccionada y actualiza sus datos."""
        for page in self.pages.values():
            page.pack_forget()
        for key, button in self.nav_buttons.items():
            button.configure(bg=NAVY_LIGHT if key == name else NAVY)
        if name not in self.pages:
            self.pages[name] = self.factories[name](self.page_area)
        page = self.pages[name]
        page.pack(fill="both", expand=True)
        page.refresh()
