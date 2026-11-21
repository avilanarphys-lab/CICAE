"""Pantalla de control de asistencia por asignatura y fecha."""
import tkinter as tk
from datetime import date
from tkinter import ttk
from .helpers import (BG, page_title, make_tree, clear_tree, choice_map, build_course_combo,
                      fill_course_combo, show_error, show_info, attempt, make_modal)
from .dialogs import FormDialog
from .. import services


class AttendancePage(tk.Frame):
    """Registra presentes, ausentes, tardanzas y ausencias justificadas."""
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.course = None
        page_title(self, "Asistencia", "Registra la asistencia de cada asignatura por fecha.").pack(fill="x", pady=(0, 16))
        self._build_filters()
        actions = tk.Frame(self, bg=BG)
        actions.pack(fill="x", pady=(0, 10))
        ttk.Button(actions, text="Registrar / modificar estado", style="Accent.TButton",
                   command=self.register).pack(side="left")
        wrapper, self.tree = make_tree(self, ("id", "code", "student", "status", "note"),
                                       ("ID", "Matrícula", "Estudiante", "Estado", "Observación"),
                                       (45, 120, 240, 130, 250))
        wrapper.pack(fill="both", expand=True)

    def _build_filters(self):
        """Construye los filtros de asignatura y fecha."""
        filters = tk.Frame(self, bg=BG)
        filters.pack(fill="x", pady=(0, 12))
        self.course_var = tk.StringVar()
        self.course_combo = build_course_combo(filters, self.course_var, self.refresh)
        tk.Label(filters, text="Fecha (AAAA-MM-DD)", bg=BG).pack(side="left", padx=(12, 0))
        self.date_var = tk.StringVar(value=date.today().isoformat())
        date_entry = ttk.Entry(filters, textvariable=self.date_var, width=14)
        date_entry.pack(side="left", padx=7)
        date_entry.bind("<Return>", lambda event: self.refresh())
        ttk.Button(filters, text="Consultar", command=self.refresh).pack(side="left")
        ttk.Button(filters, text="Resumen", command=self.summary).pack(side="right")

    def refresh(self):
        """Recarga la asistencia de la asignatura y fecha elegidas."""
        self.course = fill_course_combo(self.course_combo, self.course_var, services.list_courses())
        clear_tree(self.tree)
        if not self.course:
            return
        try:
            records = services.list_attendance(self.course.id, self.date_var.get())
        except ValueError as error:
            return show_error(self, error)
        for record in records:
            self.tree.insert("", "end", values=(record.student_id, record.student_code,
                                                record.student_name, record.status, record.note))

    def register(self):
        """Registra o modifica el estado de asistencia de un estudiante."""
        if not self.course:
            return show_info(self, "Primero crea una asignatura.")
        students = services.enrolled_students(self.course.id)
        if not students:
            return show_info(self, "No hay estudiantes inscritos en esta asignatura.")
        student_map = choice_map(students)
        dialog = FormDialog(self, "Registrar asistencia", [
            ("student", "Estudiante", "combo", list(student_map)),
            ("status", "Estado", "combo", list(services.ATTENDANCE_STATUSES)),
            ("note", "Observación / justificación", "entry")])
        self.wait_window(dialog)
        data = dialog.result
        if data and attempt(self, services.save_attendance, self.course.id, student_map[data["student"]],
                            self.date_var.get(), data["status"], data["note"]):
            self.refresh()

    def summary(self):
        """Abre el resumen acumulado de asistencia."""
        if not self.course:
            return show_info(self, "Selecciona una asignatura.")
        AttendanceSummary(self, services.attendance_summary(self.course.id))


class AttendanceSummary(tk.Toplevel):
    """Muestra estadísticas acumuladas de asistencia."""
    def __init__(self, parent, rows):
        super().__init__(parent)
        self.title("Resumen de asistencia")
        self.geometry("760x480")
        self.configure(bg=BG)
        tk.Label(self, text="Resumen de asistencia", bg=BG, fg="#17243A",
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=20, pady=18)
        wrapper, tree = make_tree(self, ("student", "sessions", "attended", "absent", "justified", "rate"),
                                  ("Estudiante", "Registros", "Presentes/tardanzas", "Ausencias", "Justificadas", "Asistencia (%)"),
                                  (230, 85, 145, 90, 100, 110))
        wrapper.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        for row in rows:
            tree.insert("", "end", values=(row["student"], row["sessions"], row["attended"],
                                           row["absent"], row["justified"], f'{row["rate"]:.1f}%'))
        make_modal(self, parent)
