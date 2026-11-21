"""Componentes y utilidades visuales compartidas."""
import tkinter as tk
from tkinter import ttk, messagebox

BG = "#F3F6FB"
NAVY = "#17243A"
NAVY_LIGHT = "#243650"
ACCENT = "#4F7CFF"
TEXT = "#1E293B"
MUTED = "#64748B"
WHITE = "#FFFFFF"
BORDER = "#E2E8F0"


def configure_style(root):
    """Configura el tema visual global."""
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", font=("Segoe UI", 10))
    style.configure("Treeview", background=WHITE, foreground=TEXT, fieldbackground=WHITE,
                    rowheight=32, borderwidth=0)
    style.configure("Treeview.Heading", background="#EAF0F8", foreground=NAVY,
                    font=("Segoe UI", 9, "bold"), relief="flat", padding=9)
    style.map("Treeview", background=[("selected", "#DCE7FF")],
              foreground=[("selected", NAVY)])
    style.configure("TCombobox", padding=7)
    style.configure("TEntry", padding=7)
    style.configure("TButton", padding=(12, 8), font=("Segoe UI", 9, "bold"))
    style.configure("Accent.TButton", background=ACCENT, foreground=WHITE)
    style.map("Accent.TButton", background=[("active", "#3867EB")])


def page_title(parent, title, subtitle):
    """Crea el encabezado de una pantalla."""
    frame = tk.Frame(parent, bg=BG)
    tk.Label(frame, text=title, bg=BG, fg=NAVY,
             font=("Segoe UI", 21, "bold")).pack(anchor="w")
    tk.Label(frame, text=subtitle, bg=BG, fg=MUTED,
             font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))
    return frame


def make_tree(parent, columns, headings, widths=None):
    """Crea una tabla Treeview con encabezados y scroll vertical."""
    wrapper = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
    tree = ttk.Treeview(wrapper, columns=columns, show="headings")
    for index, column in enumerate(columns):
        tree.heading(column, text=headings[index])
        tree.column(column, width=widths[index] if widths else 140, anchor="w")
    scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return wrapper, tree


def clear_tree(tree):
    """Vacía todos los registros visibles de una tabla."""
    for item in tree.get_children():
        tree.delete(item)


def selected_id(tree):
    """Devuelve el ID (primera columna) de la fila seleccionada, o None."""
    selected = tree.selection()
    return int(tree.item(selected[0], "values")[0]) if selected else None


def choice_map(items):
    """Crea el diccionario {texto mostrado: id} para un combo desplegable."""
    return {item.choice_label: item.id for item in items}


def build_course_combo(parent, variable, on_change, width=28):
    """Crea la etiqueta y el combo de asignaturas usados en varias pantallas."""
    tk.Label(parent, text="Asignatura", bg=BG).pack(side="left")
    combo = ttk.Combobox(parent, textvariable=variable, state="readonly", width=width)
    combo.pack(side="left", padx=7)
    combo.bind("<<ComboboxSelected>>", lambda event: on_change())
    return combo


def fill_course_combo(combo, variable, courses):
    """Carga las asignaturas en el combo y devuelve la seleccionada (o None)."""
    labels = {course.choice_label: course for course in courses}
    combo["values"] = list(labels)
    if variable.get() not in labels:
        variable.set(next(iter(labels), ""))
    return labels.get(variable.get())


def format_average(value):
    """Texto de un promedio; 'Pendiente' si aún no hay notas."""
    return "Pendiente" if value is None else f"{value:.2f}"


def make_modal(window, parent):
    """Convierte una ventana en modal respecto a su ventana padre."""
    window.transient(parent)
    try:
        window.wait_visibility()
        window.grab_set()
    except tk.TclError:
        pass


def show_error(parent, error):
    """Muestra errores de validación de forma uniforme."""
    messagebox.showerror("No se pudo completar la operación", str(error), parent=parent)


def show_info(parent, message):
    """Muestra una confirmación informativa."""
    messagebox.showinfo("SICAE", message, parent=parent)


def attempt(parent, action, *args, **kwargs):
    """Ejecuta una acción; si falla muestra el error y devuelve False."""
    try:
        action(*args, **kwargs)
        return True
    except Exception as error:
        show_error(parent, error)
        return False
