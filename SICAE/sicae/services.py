"""Reglas de negocio y operaciones de persistencia de SICAE.

Este módulo no imprime ni muestra ventanas: solo valida, calcula y guarda.
Los errores de validación se lanzan como ValueError con un mensaje claro.
"""
import csv
import math
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from .database import connect
from .models import Attendance, Course, Evaluation, Student

ATTENDANCE_STATUSES = ("Presente", "Ausente", "Tardanza", "Justificada")
WEIGHT_TOLERANCE = 0.00001
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
EMPTY_ATTENDANCE = {"sessions": 0, "attended": 0, "absent": 0, "justified": 0, "rate": 0.0}
CSV_HEADER = ["Matrícula", "Estudiante", "Promedio calculado", "Evaluaciones completadas (%)",
              "Sesiones", "Presentes/tardanzas", "Ausencias", "Justificadas", "Asistencia (%)"]


# ---------------------------------------------------------------- validaciones
def _clean(value, label):
    """Devuelve el texto sin espacios sobrantes o falla si queda vacío."""
    text = "" if value is None else str(value).strip()
    if not text:
        raise ValueError(f"El campo {label} es obligatorio.")
    return text


def _clean_email(email):
    """Valida el correo (opcional) y lo devuelve limpio."""
    text = "" if email is None else str(email).strip()
    if text and not EMAIL_PATTERN.match(text):
        raise ValueError("El correo electrónico no tiene un formato válido.")
    return text


def _number(value, label, minimum=0.0, maximum=None):
    """Convierte a número finito dentro del rango; acepta coma o punto decimal."""
    try:
        number = float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError):
        raise ValueError(f"{label} debe ser un número válido.") from None
    if not math.isfinite(number):
        raise ValueError(f"{label} debe ser un número válido.")
    if number < minimum or (maximum is not None and number > maximum):
        if maximum is None:
            raise ValueError(f"{label} debe ser mayor o igual a {minimum:g}.")
        raise ValueError(f"{label} debe estar entre {minimum:g} y {maximum:g}.")
    return number


def normalize_date(value):
    """Valida una fecha AAAA-MM-DD y la devuelve en formato ISO uniforme."""
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise ValueError("La fecha debe tener el formato AAAA-MM-DD.") from None


def attendance_rate(attended, sessions):
    """Porcentaje de asistencia (presentes + tardanzas) sobre los registros."""
    return (attended or 0) / sessions * 100 if sessions else 0.0


# ------------------------------------------------------------ acceso a datos
@contextmanager
def _friendly_errors(duplicate_message):
    """Traduce errores de integridad de SQLite a mensajes comprensibles."""
    try:
        yield
    except sqlite3.IntegrityError:
        raise ValueError(duplicate_message) from None


def _execute_write(sql, params, duplicate_message, missing_message=None):
    """Ejecuta INSERT/UPDATE/DELETE; falla si no existe el registro esperado."""
    with _friendly_errors(duplicate_message):
        with connect() as db:
            cursor = db.execute(sql, params)
            changed = cursor.rowcount
    if missing_message and changed == 0:
        raise ValueError(missing_message)


def _query(model, sql, params=()):
    """Ejecuta un SELECT y devuelve una lista de objetos del modelo."""
    with connect() as db:
        rows = db.execute(sql, params).fetchall()
    return [model.from_row(row) for row in rows]


def _get(model, table, record_id):
    """Busca un registro por ID; devuelve None si no existe."""
    found = _query(model, f"SELECT * FROM {table} WHERE id=?", (record_id,))
    return found[0] if found else None


def _require_enrollment(db, course_id, student_id):
    """Falla si el estudiante no pertenece a la asignatura."""
    enrolled = db.execute("SELECT 1 FROM enrollments WHERE course_id=? AND student_id=?",
                          (course_id, student_id)).fetchone()
    if not enrolled:
        raise ValueError("El estudiante no está inscrito en esta asignatura.")


# ----------------------------------------------------------------- estudiantes
def _escape_like(text):
    """Evita que % y _ escritos por el usuario actúen como comodines."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def list_students(search=""):
    """Devuelve estudiantes, filtrando por nombre, apellido o matrícula."""
    term = f"%{_escape_like((search or '').strip())}%"
    return _query(Student,
                  """SELECT * FROM students
                     WHERE first_name LIKE ? ESCAPE '\\' OR last_name LIKE ? ESCAPE '\\'
                        OR student_code LIKE ? ESCAPE '\\'
                     ORDER BY last_name, first_name""", (term, term, term))


def get_student(student_id):
    """Busca un estudiante por ID."""
    return _get(Student, "students", student_id)


def save_student(student_id, first_name, last_name, code, email):
    """Crea o actualiza un estudiante."""
    values = (_clean(first_name, "nombre"), _clean(last_name, "apellido"),
              _clean(code, "matrícula"), _clean_email(email))
    duplicate = "Ya existe un estudiante con esa matrícula."
    if student_id:
        _execute_write("UPDATE students SET first_name=?, last_name=?, student_code=?, email=? WHERE id=?",
                       (*values, student_id), duplicate, "El estudiante no existe.")
    else:
        _execute_write("INSERT INTO students(first_name,last_name,student_code,email) VALUES(?,?,?,?)",
                       values, duplicate)


def delete_student(student_id):
    """Elimina un estudiante y sus registros relacionados."""
    _execute_write("DELETE FROM students WHERE id=?", (student_id,), "", "El estudiante no existe.")


# ------------------------------------------------------------------ asignaturas
def list_courses():
    """Devuelve todas las asignaturas."""
    return _query(Course, "SELECT * FROM courses ORDER BY name")


def get_course(course_id):
    """Busca una asignatura por ID."""
    return _get(Course, "courses", course_id)


def save_course(course_id, name, code, period, description):
    """Crea o actualiza una asignatura."""
    values = (_clean(name, "nombre de asignatura"), _clean(code, "código"),
              _clean(period, "período"), str(description or "").strip())
    duplicate = "Ya existe una asignatura con ese código."
    if course_id:
        _execute_write("UPDATE courses SET name=?,code=?,period=?,description=? WHERE id=?",
                       (*values, course_id), duplicate, "La asignatura no existe.")
    else:
        _execute_write("INSERT INTO courses(name,code,period,description) VALUES(?,?,?,?)",
                       values, duplicate)


def delete_course(course_id):
    """Elimina una asignatura y sus datos asociados."""
    _execute_write("DELETE FROM courses WHERE id=?", (course_id,), "", "La asignatura no existe.")


# ---------------------------------------------------------------- inscripciones
def enroll_student(student_id, course_id):
    """Inscribe un estudiante en una asignatura (si ya estaba, no hace nada)."""
    _execute_write("INSERT OR IGNORE INTO enrollments(student_id,course_id) VALUES(?,?)",
                   (student_id, course_id), "El estudiante o la asignatura ya no existe.")


def remove_enrollment(student_id, course_id):
    """Retira un estudiante de una asignatura."""
    _execute_write("DELETE FROM enrollments WHERE student_id=? AND course_id=?",
                   (student_id, course_id), "",
                   "El estudiante no está inscrito en esta asignatura.")


def enrolled_students(course_id):
    """Lista los estudiantes inscritos en una asignatura."""
    return _query(Student,
                  """SELECT s.* FROM students s JOIN enrollments e ON e.student_id=s.id
                     WHERE e.course_id=? ORDER BY s.last_name, s.first_name""", (course_id,))


# ------------------------------------------------------------------ evaluaciones
def list_evaluations(course_id, period=None):
    """Lista evaluaciones de una asignatura, opcionalmente de un solo período."""
    sql, params = "SELECT * FROM evaluations WHERE course_id=?", [course_id]
    if period is not None:
        sql += " AND period=?"
        params.append(period.strip())
    return _query(Evaluation, sql + " ORDER BY period, name", params)


def _validated_evaluation(course_id, name, category, weight, max_score, period):
    """Limpia y valida los datos de una evaluación."""
    return (course_id, _clean(name, "nombre de evaluación"), _clean(category, "categoría"),
            _number(weight, "Ponderación", 0.01, 100),
            _number(max_score, "Puntuación máxima", 0.01), _clean(period, "período"))


def _check_evaluation_rules(db, values, evaluation_id):
    """Verifica el límite de 100 % del período y que el nombre no se repita."""
    course_id, name, _, weight, _, period = values
    scope = (course_id, period, evaluation_id or 0)
    total = db.execute("""SELECT COALESCE(SUM(weight),0) FROM evaluations
                          WHERE course_id=? AND period=? AND id<>?""", scope).fetchone()[0]
    if total + weight > 100 + WEIGHT_TOLERANCE:
        raise ValueError(f"La ponderación total del período sería {total + weight:.2f}%. No puede superar 100%.")
    repeated = db.execute("""SELECT 1 FROM evaluations WHERE course_id=? AND period=? AND id<>?
                             AND lower(name)=lower(?)""", (*scope, name)).fetchone()
    if repeated:
        raise ValueError("Ya existe una evaluación con ese nombre en el período.")


def save_evaluation(evaluation_id, course_id, name, category, weight, max_score, period):
    """Crea o actualiza una evaluación y valida su ponderación."""
    values = _validated_evaluation(course_id, name, category, weight, max_score, period)
    with _friendly_errors("La asignatura seleccionada ya no existe."):
        with connect() as db:
            _check_evaluation_rules(db, values, evaluation_id)
            if not evaluation_id:
                db.execute("""INSERT INTO evaluations(course_id,name,category,weight,max_score,period)
                              VALUES(?,?,?,?,?,?)""", values)
                return
            cursor = db.execute("""UPDATE evaluations SET course_id=?,name=?,category=?,weight=?,
                                   max_score=?,period=? WHERE id=?""", (*values, evaluation_id))
            if cursor.rowcount == 0:
                raise ValueError("La evaluación no existe.")


def delete_evaluation(evaluation_id):
    """Elimina una evaluación y sus notas."""
    _execute_write("DELETE FROM evaluations WHERE id=?", (evaluation_id,), "", "La evaluación no existe.")


# ----------------------------------------------------------------- calificaciones
def save_grade(evaluation_id, student_id, score):
    """Guarda la nota de un estudiante para una evaluación."""
    with connect() as db:
        evaluation = db.execute("SELECT * FROM evaluations WHERE id=?", (evaluation_id,)).fetchone()
        if not evaluation:
            raise ValueError("La evaluación seleccionada ya no existe.")
        score = _number(score, "Calificación", 0, evaluation["max_score"])
        _require_enrollment(db, evaluation["course_id"], student_id)
        db.execute("""INSERT INTO grades(evaluation_id,student_id,score) VALUES(?,?,?)
                      ON CONFLICT(evaluation_id,student_id) DO UPDATE SET score=excluded.score""",
                   (evaluation_id, student_id, score))


def _weighted_totals(course_id, period):
    """Suma, por estudiante, los puntos ponderados ganados y el peso ya calificado."""
    with connect() as db:
        rows = db.execute("""SELECT g.student_id, g.score, e.weight, e.max_score
                             FROM grades g JOIN evaluations e ON e.id=g.evaluation_id
                             WHERE e.course_id=? AND e.period=?""", (course_id, period)).fetchall()
    totals = {}
    for row in rows:
        earned, completed = totals.get(row["student_id"], (0.0, 0.0))
        totals[row["student_id"]] = (earned + row["score"] / row["max_score"] * row["weight"],
                                     completed + row["weight"])
    return totals


def gradebook(course_id, period):
    """Calcula promedios ponderados sin convertir notas pendientes en cero."""
    period = period.strip()
    totals = _weighted_totals(course_id, period)
    rows = []
    for student in enrolled_students(course_id):
        earned, completed = totals.get(student.id, (0.0, 0.0))
        rows.append({
            "student_id": student.id,
            "code": student.student_code,
            "student": f"{student.last_name}, {student.first_name}",
            "average": earned / completed * 100 if completed else None,
            "coverage": completed,
        })
    return list_evaluations(course_id, period), rows


# -------------------------------------------------------------------- asistencia
def list_attendance(course_id, date):
    """Devuelve la asistencia registrada en una fecha."""
    return _query(Attendance,
                  """SELECT a.*, s.first_name || ' ' || s.last_name student_name, s.student_code
                     FROM attendance a JOIN students s ON s.id=a.student_id
                     WHERE a.course_id=? AND a.date=? ORDER BY s.last_name, s.first_name""",
                  (course_id, normalize_date(date)))


def save_attendance(course_id, student_id, date, status, note=""):
    """Registra o actualiza la asistencia diaria."""
    if status not in ATTENDANCE_STATUSES:
        raise ValueError("Estado de asistencia no válido.")
    day = normalize_date(date)
    with connect() as db:
        _require_enrollment(db, course_id, student_id)
        db.execute("""INSERT INTO attendance(course_id,student_id,date,status,note) VALUES(?,?,?,?,?)
                      ON CONFLICT(course_id,student_id,date)
                      DO UPDATE SET status=excluded.status, note=excluded.note""",
                   (course_id, student_id, day, status, str(note or "").strip()))


def attendance_summary(course_id):
    """Calcula estadísticas de asistencia por estudiante, incluido el porcentaje."""
    with connect() as db:
        rows = db.execute(
            """SELECT s.id, s.student_code, s.first_name || ' ' || s.last_name student,
               COUNT(a.id) sessions,
               COALESCE(SUM(a.status IN ('Presente','Tardanza')), 0) attended,
               COALESCE(SUM(a.status='Ausente'), 0) absent,
               COALESCE(SUM(a.status='Justificada'), 0) justified
               FROM enrollments e JOIN students s ON s.id=e.student_id
               LEFT JOIN attendance a ON a.student_id=s.id AND a.course_id=e.course_id
               WHERE e.course_id=? GROUP BY s.id ORDER BY s.last_name, s.first_name""",
            (course_id,)).fetchall()
    return [{**dict(row), "rate": attendance_rate(row["attended"], row["sessions"])} for row in rows]


# ---------------------------------------------------------------------- reportes
def dashboard_stats():
    """Devuelve los indicadores principales del panel."""
    with connect() as db:
        stats = {table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                 for table in ("students", "courses", "enrollments")}
        attendance = db.execute(
            """SELECT COUNT(*) total,
               COALESCE(SUM(status IN ('Presente','Tardanza')), 0) attended FROM attendance"""
        ).fetchone()
    stats["attendance_rate"] = attendance_rate(attendance["attended"], attendance["total"])
    return stats


def course_report(course_id):
    """Combina promedio y asistencia de cada estudiante de una asignatura."""
    course = get_course(course_id)
    if not course:
        raise ValueError("La asignatura seleccionada no existe.")
    _, grades = gradebook(course_id, course.period)
    attendance = {row["id"]: row for row in attendance_summary(course_id)}
    return [{**grade, **{key: attendance.get(grade["student_id"], EMPTY_ATTENDANCE)[key]
                         for key in EMPTY_ATTENDANCE}} for grade in grades]


def _csv_row(item):
    """Convierte una fila del reporte en la lista de columnas del CSV."""
    average = "" if item["average"] is None else round(item["average"], 2)
    return [item["code"], item["student"], average, round(item["coverage"], 2),
            item["sessions"], item["attended"], item["absent"], item["justified"],
            round(item["rate"], 2)]


def export_course_report(course_id, destination):
    """Exporta un reporte de notas y asistencia a CSV."""
    report = course_report(course_id)
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as output:
        writer = csv.writer(output)
        writer.writerow(CSV_HEADER)
        writer.writerows(_csv_row(item) for item in report)
    return path
