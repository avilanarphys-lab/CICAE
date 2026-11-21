"""Creación y acceso a la base de datos SQLite."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "sicae.db"

SCHEMA = (
    """CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        student_code TEXT NOT NULL UNIQUE,
        email TEXT DEFAULT ''
    )""",
    """CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL UNIQUE,
        period TEXT NOT NULL,
        description TEXT DEFAULT ''
    )""",
    """CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        UNIQUE(student_id, course_id),
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        weight REAL NOT NULL CHECK(weight > 0 AND weight <= 100),
        max_score REAL NOT NULL CHECK(max_score > 0),
        period TEXT NOT NULL,
        FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evaluation_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        score REAL NOT NULL CHECK(score >= 0),
        UNIQUE(evaluation_id, student_id),
        FOREIGN KEY(evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Presente', 'Ausente', 'Tardanza', 'Justificada')),
        note TEXT DEFAULT '',
        UNIQUE(course_id, student_id, date),
        FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
    )""",
)


@contextmanager
def connect():
    """Abre y cierra una conexión SQLite con claves foráneas activadas."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    """Crea las tablas necesarias si todavía no existen."""
    with connect() as connection:
        for statement in SCHEMA:
            connection.execute(statement)
