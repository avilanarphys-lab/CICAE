"""Pantalla para configurar evaluaciones y registrar calificaciones."""
import tkinter as tk
from tkinter import ttk, messagebox
from .helpers import (BG, page_title, make_tree, clear_tree, selected_id, choice_map,
                      build_course_combo, fill_course_combo, format_average,
                      show_info, attempt, make_modal)
from .dialogs import FormDialog
from .. import services

EVALUATION_FIELDS = [
    ("name", "Nombre", "entry"), ("category", "Categoría (práctica, examen...)", "entry"),
    ("weight", "Ponderación (%)", "entry"), ("max_score", "Puntuación máxima", "entry"),
    ("period", "Período", "entry"),
]


class GradesPage(tk.Frame):
    """Gestiona evaluaciones, notas y promedios ponderados."""
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.course = None
        self.evaluation_id = None
        page_title(self, "Calificaciones", "Configura evaluaciones y registra las notas de cada estudiante.").pack(fill="x", pady=(0, 16))
        self._build_filters()
        self._build_actions()
        wrapper, self.eval_tree = make_tree(self, ("id", "name", "category", "weight", "max", "period"),
                                            ("ID", "Evaluación", "Categoría", "Peso (%)", "Puntaje máx.", "Período"),
                                            (45, 190, 130, 90, 100, 130))
        wrapper.pack(fill="both", expand=True)
        self.eval_tree.bind("<<TreeviewSelect>>", lambda event: self._select())

    def _build_filters(self):
        """Construye los filtros de asignatura y período."""
        filters = tk.Frame(self, bg=BG)
        filters.pack(fill="x", pady=(0, 12))
        self.course_var = tk.StringVar()
        self.course_combo = build_course_combo(filters, self.course_var, self.refresh)
        tk.Label(filters, text="Período", bg=BG).pack(side="left", padx=(12, 0))
        self.period_var = tk.StringVar()
        period_entry = ttk.Entry(filters, textvariable=self.period_var, width=18)
        period_entry.pack(side="left", padx=7)
        period_entry.bind("<Return>", lambda event: self.refresh())
        ttk.Button(filters, text="Actualizar", command=self.refresh).pack(side="left", padx=5)

    def _build_actions(self):
        """Construye los botones de acciones."""
        actions = tk.Frame(self, bg=BG)
        actions.pack(fill="x", pady=(0, 10))
        ttk.Button(actions, text="+ Crear evaluación", style="Accent.TButton", command=self.add_evaluation).pack(side="left")
        ttk.Button(actions, text="Registrar nota", command=self.add_grade).pack(side="left", padx=6)
        ttk.Button(actions, text="Eliminar evaluación", command=self.delete_evaluation).pack(side="left")
        ttk.Button(actions, text="Ver notas y promedios", command=self.show_gradebook).pack(side="right")

    def _select(self):
        self.evaluation_id = selected_id(self.eval_tree)

    def refresh(self):
        """Recarga las evaluaciones de la asignatura y período elegidos."""
        previous = self.course
        self.course = fill_course_combo(self.course_combo, self.course_var, services.list_courses())
        clear_tree(self.eval_tree)
        self.evaluation_id = None
        if not self.course:
            return
        if previous is None or previous.id != self.course.id or not self.period_var.get().strip():
            self.period_var.set(self.course.period)
        for item in services.list_evaluations(self.course.id, self.period_var.get()):
            self.eval_tree.insert("", "end", values=(item.id, item.name, item.category,
                                  f"{item.weight:.2f}", f"{item.max_score:.2f}", item.period))

    def add_evaluation(self):
        """Crea una evaluación nueva en la asignatura seleccionada."""
        if not self.course:
            return show_info(self, "Primero crea una asignatura.")
        dialog = FormDialog(self, "Nueva evaluación", EVALUATION_FIELDS, {"period": self.period_var.get()})
        self.wait_window(dialog)
        if dialog.result and attempt(self, services.save_evaluation, None, self.course.id, **dialog.result):
            self.refresh()

    def delete_evaluation(self):
        """Elimina la evaluación seleccionada tras confirmar."""
        if not self.evaluation_id:
            return show_info(self, "Selecciona una evaluación.")
        if messagebox.askyesno("Confirmar", "Se eliminarán las notas asociadas. ¿Continuar?", parent=self):
            if attempt(self, services.delete_evaluation, self.evaluation_id):
                self.refresh()

    def add_grade(self):
        """Registra la nota de un estudiante en una evaluación."""
        if not self.course:
            return show_info(self, "Selecciona una asignatura.")
        evaluations = services.list_evaluations(self.course.id, self.period_var.get())
        students = services.enrolled_students(self.course.id)
        if not evaluations or not students:
            return show_info(self, "Necesitas evaluaciones y estudiantes inscritos.")
        evaluation_map, student_map = choice_map(evaluations), choice_map(students)
        dialog = FormDialog(self, "Registrar calificación", [
            ("evaluation", "Evaluación", "combo", list(evaluation_map)),
            ("student", "Estudiante", "combo", list(student_map)),
            ("score", "Calificación obtenida", "entry")])
        self.wait_window(dialog)
        data = dialog.result
        if data and attempt(self, services.save_grade, evaluation_map[data["evaluation"]],
                            student_map[data["student"]], data["score"]):
            show_info(self, "Calificación guardada.")

    def show_gradebook(self):
        """Abre el libro de calificaciones del período."""
        if not self.course:
            return show_info(self, "Selecciona una asignatura.")
        period = self.period_var.get().strip()
        _, rows = services.gradebook(self.course.id, period)
        GradebookDialog(self, rows, period)


class GradebookDialog(tk.Toplevel):
    """Muestra promedio calculado y porcentaje de evaluaciones completadas."""
    def __init__(self, parent, rows, period):
        super().__init__(parent)
        self.title("Libro de calificaciones")
        self.geometry("720x480")
        self.configure(bg=BG)
        tk.Label(self, text=f"Libro de calificaciones · {period}", bg=BG, fg="#17243A",
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=20, pady=18)
        wrapper, tree = make_tree(self, ("student", "average", "coverage"),
                                  ("Estudiante", "Promedio sobre 100", "Evaluaciones completadas"), (340, 160, 180))
        wrapper.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        for row in rows:
            tree.insert("", "end", values=(row["student"], format_average(row["average"]),
                                           f'{row["coverage"]:.1f}%'))
        tk.Label(self, text="El promedio se calcula solo con evaluaciones calificadas; las pendientes no se convierten en cero.",
                 bg=BG, fg="#64748B", wraplength=650).pack(anchor="w", padx=20, pady=(0, 18))
        make_modal(self, parent)
