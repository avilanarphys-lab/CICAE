"""Pantalla de reportes y exportación CSV."""
import tkinter as tk
from tkinter import ttk, filedialog
from .helpers import (BG, page_title, make_tree, clear_tree, build_course_combo,
                      fill_course_combo, format_average, show_error, show_info)
from .. import services


class ReportsPage(tk.Frame):
    """Consulta estadísticas y exporta un reporte de asignatura."""
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.course = None
        page_title(self, "Reportes", "Consulta el rendimiento y exporta información académica a CSV.").pack(fill="x", pady=(0, 18))
        toolbar = tk.Frame(self, bg=BG)
        toolbar.pack(fill="x", pady=(0, 12))
        self.course_var = tk.StringVar()
        self.combo = build_course_combo(toolbar, self.course_var, self.refresh, width=32)
        ttk.Button(toolbar, text="Exportar CSV", style="Accent.TButton", command=self.export).pack(side="right")
        wrapper, self.tree = make_tree(self, ("student", "average", "coverage", "sessions", "absent", "rate"),
            ("Estudiante", "Promedio", "Evaluaciones completadas", "Clases registradas", "Ausencias", "Asistencia (%)"),
            (220, 100, 160, 130, 90, 110))
        wrapper.pack(fill="both", expand=True)

    def refresh(self):
        """Recarga el reporte de la asignatura seleccionada."""
        self.course = fill_course_combo(self.combo, self.course_var, services.list_courses())
        clear_tree(self.tree)
        if not self.course:
            return
        for row in services.course_report(self.course.id):
            self.tree.insert("", "end", values=(
                row["student"], format_average(row["average"]), f'{row["coverage"]:.1f}%',
                row["sessions"], row["absent"], f'{row["rate"]:.1f}%'))

    def export(self):
        """Exporta el reporte a un archivo CSV elegido por el usuario."""
        if not self.course:
            return show_info(self, "Selecciona una asignatura.")
        destination = filedialog.asksaveasfilename(
            parent=self, title="Guardar reporte", defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv")], initialfile="reporte_academico.csv")
        if not destination:
            return
        try:
            path = services.export_course_report(self.course.id, destination)
            show_info(self, f"Reporte exportado correctamente:\n{path}")
        except Exception as error:
            show_error(self, error)
