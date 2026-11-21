"""Pantalla de administración de estudiantes."""
import tkinter as tk
from tkinter import ttk, messagebox
from .helpers import (BG, page_title, make_tree, clear_tree, selected_id,
                      show_info, attempt)
from .dialogs import FormDialog
from .. import services

STUDENT_FIELDS = [
    ("first_name", "Nombre", "entry"), ("last_name", "Apellido", "entry"),
    ("code", "Matrícula", "entry"), ("email", "Correo electrónico", "entry"),
]


class StudentsPage(tk.Frame):
    """Permite buscar, crear, editar y eliminar estudiantes."""
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.selected_id = None
        page_title(self, "Estudiantes", "Registra y administra la información de tus estudiantes.").pack(fill="x", pady=(0, 18))
        self._build_toolbar()
        wrapper, self.tree = make_tree(self, ("id", "code", "name", "email"),
                                       ("ID", "Matrícula", "Nombre completo", "Correo"), (55, 130, 260, 250))
        wrapper.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", lambda event: self._select())

    def _build_toolbar(self):
        """Construye la barra de búsqueda y acciones."""
        toolbar = tk.Frame(self, bg=BG)
        toolbar.pack(fill="x", pady=(0, 12))
        self.search = tk.StringVar()
        entry = ttk.Entry(toolbar, textvariable=self.search, width=28)
        entry.pack(side="left")
        entry.bind("<Return>", lambda event: self.refresh())
        ttk.Button(toolbar, text="Buscar", command=self.refresh).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Limpiar", command=self._clear_search).pack(side="left")
        ttk.Button(toolbar, text="+ Nuevo estudiante", style="Accent.TButton", command=self.add).pack(side="right")
        ttk.Button(toolbar, text="Eliminar", command=self.delete).pack(side="right", padx=6)
        ttk.Button(toolbar, text="Editar", command=self.edit).pack(side="right")

    def _clear_search(self):
        self.search.set("")
        self.refresh()

    def _select(self):
        self.selected_id = selected_id(self.tree)

    def refresh(self):
        """Recarga la tabla según el texto de búsqueda."""
        clear_tree(self.tree)
        self.selected_id = None
        for student in services.list_students(self.search.get()):
            self.tree.insert("", "end", values=(student.id, student.student_code,
                                                student.full_name, student.email))

    def add(self):
        """Abre el formulario para un estudiante nuevo."""
        self._form("Nuevo estudiante", None, {})

    def edit(self):
        """Abre el formulario con los datos del estudiante seleccionado."""
        if not self.selected_id:
            return show_info(self, "Selecciona un estudiante de la tabla.")
        student = services.get_student(self.selected_id)
        if not student:
            return self.refresh()
        self._form("Editar estudiante", student.id, {
            "first_name": student.first_name, "last_name": student.last_name,
            "code": student.student_code, "email": student.email})

    def _form(self, title, student_id, initial):
        """Muestra el formulario y guarda el resultado."""
        dialog = FormDialog(self, title, STUDENT_FIELDS, initial)
        self.wait_window(dialog)
        data = dialog.result
        if data and attempt(self, services.save_student, student_id, data["first_name"],
                            data["last_name"], data["code"], data["email"]):
            self.refresh()
            show_info(self, "Estudiante guardado correctamente.")

    def delete(self):
        """Elimina al estudiante seleccionado tras confirmar."""
        if not self.selected_id:
            return show_info(self, "Selecciona un estudiante de la tabla.")
        if messagebox.askyesno("Confirmar eliminación",
                               "Se eliminarán también sus notas y asistencias. ¿Continuar?", parent=self):
            if attempt(self, services.delete_student, self.selected_id):
                self.refresh()
