"""Pantalla de asignaturas e inscripción de estudiantes."""
import tkinter as tk
from tkinter import ttk, messagebox
from .helpers import (BG, page_title, make_tree, clear_tree, selected_id, choice_map,
                      show_info, attempt, make_modal)
from .dialogs import FormDialog
from .. import services

COURSE_FIELDS = [
    ("name", "Nombre", "entry"), ("code", "Código", "entry"),
    ("period", "Período académico", "entry"), ("description", "Descripción", "entry"),
]


class CoursesPage(tk.Frame):
    """Administra asignaturas e inscripciones."""
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.selected_id = None
        page_title(self, "Asignaturas", "Crea materias y administra qué estudiantes pertenecen a cada una.").pack(fill="x", pady=(0, 18))
        toolbar = tk.Frame(self, bg=BG)
        toolbar.pack(fill="x", pady=(0, 12))
        ttk.Button(toolbar, text="+ Nueva asignatura", style="Accent.TButton", command=self.add).pack(side="left")
        ttk.Button(toolbar, text="Editar", command=self.edit).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Eliminar", command=self.delete).pack(side="left")
        ttk.Button(toolbar, text="Inscribir estudiantes", command=self.manage_enrollments).pack(side="right")
        wrapper, self.tree = make_tree(self, ("id", "code", "name", "period", "description"),
                                       ("ID", "Código", "Asignatura", "Período", "Descripción"), (50, 110, 210, 150, 300))
        wrapper.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", lambda event: self._select())

    def _select(self):
        self.selected_id = selected_id(self.tree)

    def refresh(self):
        """Recarga la tabla de asignaturas."""
        clear_tree(self.tree)
        self.selected_id = None
        for course in services.list_courses():
            self.tree.insert("", "end", values=(course.id, course.code, course.name,
                                                course.period, course.description))

    def add(self):
        """Abre el formulario para una asignatura nueva."""
        self._form(None, {})

    def edit(self):
        """Abre el formulario con los datos de la asignatura seleccionada."""
        if not self.selected_id:
            return show_info(self, "Selecciona una asignatura.")
        course = services.get_course(self.selected_id)
        if not course:
            return self.refresh()
        self._form(course.id, {"name": course.name, "code": course.code,
                               "period": course.period, "description": course.description})

    def _form(self, course_id, initial):
        """Muestra el formulario y guarda el resultado."""
        dialog = FormDialog(self, "Asignatura", COURSE_FIELDS, initial)
        self.wait_window(dialog)
        if dialog.result and attempt(self, services.save_course, course_id, **dialog.result):
            self.refresh()

    def delete(self):
        """Elimina la asignatura seleccionada tras confirmar."""
        if not self.selected_id:
            return show_info(self, "Selecciona una asignatura.")
        if messagebox.askyesno("Confirmar", "Se eliminarán sus inscripciones, notas y asistencias. ¿Continuar?", parent=self):
            if attempt(self, services.delete_course, self.selected_id):
                self.refresh()

    def manage_enrollments(self):
        """Abre la ventana de inscripciones de la asignatura seleccionada."""
        if not self.selected_id:
            return show_info(self, "Selecciona primero una asignatura.")
        EnrollmentDialog(self, self.selected_id)


class EnrollmentDialog(tk.Toplevel):
    """Permite inscribir o retirar estudiantes de una asignatura."""
    def __init__(self, parent, course_id):
        super().__init__(parent)
        self.course_id = course_id
        self.title("Inscripciones")
        self.geometry("650x470")
        self.configure(bg=BG)
        tk.Label(self, text="Inscribir estudiantes", bg=BG, fg="#17243A",
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=20, pady=18)
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=20)
        self.student_var = tk.StringVar()
        self.student_map = choice_map(services.list_students())
        ttk.Combobox(top, textvariable=self.student_var, values=list(self.student_map),
                     state="readonly", width=42).pack(side="left")
        ttk.Button(top, text="Inscribir", style="Accent.TButton", command=self.enroll).pack(side="left", padx=8)
        wrapper, self.tree = make_tree(self, ("id", "code", "student"), ("ID", "Matrícula", "Estudiante"), (55, 130, 300))
        wrapper.pack(fill="both", expand=True, padx=20, pady=16)
        ttk.Button(self, text="Retirar seleccionado", command=self.remove).pack(anchor="e", padx=20, pady=(0, 18))
        self.refresh()
        make_modal(self, parent)

    def refresh(self):
        """Recarga la lista de estudiantes inscritos."""
        clear_tree(self.tree)
        for student in services.enrolled_students(self.course_id):
            self.tree.insert("", "end", values=(student.id, student.student_code, student.full_name))

    def enroll(self):
        """Inscribe al estudiante elegido en el combo."""
        student_id = self.student_map.get(self.student_var.get())
        if not student_id:
            return show_info(self, "Selecciona un estudiante.")
        if attempt(self, services.enroll_student, student_id, self.course_id):
            self.refresh()

    def remove(self):
        """Retira al estudiante seleccionado de la tabla."""
        student_id = selected_id(self.tree)
        if not student_id:
            return show_info(self, "Selecciona una inscripción.")
        if attempt(self, services.remove_enrollment, student_id, self.course_id):
            self.refresh()
