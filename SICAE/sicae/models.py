"""Modelos principales del dominio académico."""
from dataclasses import dataclass, fields


class _FromRow:
    """Mixin que construye un modelo a partir de una fila de SQLite."""

    @classmethod
    def from_row(cls, row):
        """Crea la instancia con las columnas que el modelo declara."""
        available = row.keys()
        return cls(**{item.name: row[item.name] for item in fields(cls)
                      if item.name in available})


@dataclass
class Student(_FromRow):
    """Representa a un estudiante."""
    id: int
    first_name: str
    last_name: str
    student_code: str
    email: str = ""

    @property
    def full_name(self):
        """Nombre completo en formato 'Nombre Apellido'."""
        return f"{self.first_name} {self.last_name}"

    @property
    def choice_label(self):
        """Texto único para mostrar al estudiante en listas desplegables."""
        return f"{self.student_code} · {self.full_name}"


@dataclass
class Course(_FromRow):
    """Representa una asignatura administrada por el docente."""
    id: int
    name: str
    code: str
    period: str
    description: str = ""

    @property
    def choice_label(self):
        """Texto único para mostrar la asignatura en listas desplegables."""
        return f"{self.id} · {self.name}"


@dataclass
class Evaluation(_FromRow):
    """Representa una actividad evaluativa."""
    id: int
    course_id: int
    name: str
    category: str
    weight: float
    max_score: float
    period: str

    @property
    def choice_label(self):
        """Texto único para mostrar la evaluación en listas desplegables."""
        return f"{self.id} · {self.name} · máx. {self.max_score:g}"


@dataclass
class Attendance(_FromRow):
    """Representa la asistencia de un estudiante en una fecha."""
    id: int
    course_id: int
    student_id: int
    date: str
    status: str
    note: str = ""
    student_name: str = ""
    student_code: str = ""
