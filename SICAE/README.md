# SICAE — Sistema de Control Académico de Estudiantes

Aplicación de escritorio en Python que permite a un docente administrar estudiantes, asignaturas, evaluaciones, calificaciones y asistencia, con reportes exportables a CSV.

## Descripción del problema y justificación

Problema: Un docente que lleva el control de sus grupos en cuadernos u hojas sueltas enfrenta errores al calcular promedios, pérdida de información, dificultad para saber cuántas evaluaciones faltan por calificar y poca visibilidad sobre la asistencia de cada estudiante.

Justificación: Un sistema que centralice los datos, calcule automáticamente los promedios ponderados y registre la asistencia por fecha reduce los errores de cálculo, ahorra tiempo y permite consultar el rendimiento de cada estudiante en cualquier momento. Además, los datos quedan guardados de forma permanente y se pueden exportar para compartirlos o archivarlos.

## Funcionalidades

- Registro, búsqueda, edición y eliminación de estudiantes.
- Creación y administración de asignaturas, cada una con su período académico.
- Inscripción y retiro de estudiantes por asignatura.
- Evaluaciones configurables por categoría, período, ponderación y puntuación máxima.
- Registro de notas y cálculo de promedios ponderados.
- Las evaluaciones pendientes no se convierten en cero: el promedio se calcula solo con lo ya calificado y se muestra el porcentaje evaluado.
- Registro de asistencia por asignatura y fecha (Presente, Ausente, Tardanza y Justificada).
- Panel de inicio con indicadores generales.
- Reportes por asignatura y exportación a CSV.
- Validación de todos los datos ingresados, con mensajes claros.
- Persistencia local: los datos permanecen al cerrar y reabrir el programa.

**No incluye:** inicio de sesión de usuarios, varios docentes, acceso desde internet o aplicación móvil, ni impresión de boletines.

## Tecnologías utilizadas

- Python 3
- Tkinter / ttk (interfaz gráfica)
- SQLite (módulo `sqlite3`, base de datos local)
- CSV (módulo `csv`, exportación de reportes)
- Git y GitHub (control de versiones)

No utiliza librerías externas.

## Requisitos previos

- Python 3.10 o superior.
- Tkinter. Viene incluido en el instalador oficial de Python para Windows y macOS. En Linux: `sudo apt install python3-tk`.
- No hay dependencias que instalar (`requirements.txt` solo documenta esto).

## Instalación

1. Clona el repositorio o descárgalo como ZIP y descomprimelo:
   ```bash
   git clone https://github.com/avilanarphys-lab/SICAE.git
   ```
2. Entra a la carpeta del proyecto:
   ```bash
   cd SICAE
   ```
3. Ejecuta el programa:
   ```bash
   python main.py
   ```
   (En Windows también puedes usar `py main.py`; en Linux/macOS, `python3 main.py`.)

La base de datos `data/sicae.db` se crea automáticamente la primera vez.

## Uso y ejemplos

Flujo recomendado:

1. **Estudiantes:** pulsa *+ Nuevo estudiante* y completa nombre, apellido, matrícula y correo (opcional).
2. **Asignaturas:** crea una asignatura, por ejemplo `Programación I`, código `PRG101`, período `Primer trimestre`.
3. **Inscripciones:** selecciona la asignatura, pulsa *Inscribir estudiantes* y agrega a los estudiantes.
4. **Calificaciones:** crea evaluaciones (las ponderaciones de un período no pueden superar 100 %) y registra las notas.
5. **Asistencia:** elige asignatura y fecha (`AAAA-MM-DD`) y registra el estado de cada estudiante.
6. **Reportes:** consulta el rendimiento y pulsa *Exportar CSV*.

**Ejemplo de cálculo.** Una evaluación "Práctica 1" vale 20 % y se califica sobre 20; otra, "Examen parcial", vale 30 % y aún no tiene nota. Si el estudiante saca 18/20 en la práctica:

| Dato | Valor |
|---|---|
| Promedio calculado | 90.00 |
| Evaluaciones completadas | 20 % |

El examen pendiente no cuenta como cero; cuando se califique, el promedio se actualiza.

**Entradas incorrectas.** Si se escribe texto donde va un número, un valor negativo, un campo vacío o una fecha inválida, el sistema muestra un mensaje explicativo y no se cierra. Las calificaciones aceptan punto o coma decimal (`15.5` o `15,5`).

## Estructura de carpetas

```text
SICAE/
├── main.py               # punto de entrada
├── requirements.txt
├── README.md
├── .gitignore
├── data/                 # aquí se crea sicae.db
├── docs/
│   └── capturas/         # capturas de pantalla del README
└── sicae/
    ├── database.py       # esquema SQLite y conexión
    ├── models.py         # clases del dominio (Student, Course, Evaluation, Attendance)
    ├── services.py       # validaciones, reglas de negocio y reportes (sin interfaz)
    └── ui/
        ├── app.py        # ventana principal y navegación
        ├── dashboard.py
        ├── students.py
        ├── courses.py
        ├── grades.py
        ├── attendance.py
        ├── reports.py
        ├── dialogs.py
        └── helpers.py
```

## Capturas de pantalla

<!-- Guarda las capturas en docs/capturas/ con estos nombres. -->

| Inicio | Estudiantes |
|---|---|
| ![Inicio](docs/capturas/inicio.png) | ![Estudiantes](docs/capturas/estudiantes.png) |

| Calificaciones | Asistencia |
|---|---|
| ![Calificaciones](docs/capturas/calificaciones.png) | ![Asistencia](docs/capturas/asistencia.png) |

| Reportes |
|---|
| ![Reportes](docs/capturas/reportes.png) |

## Autor, curso, profesor e institución

- **Autor(es):** [Nombre y apellido de cada integrante del equipo]
- **Curso:** [Nombre de la asignatura]
- **Profesor:** [Nombre del profesor]
- **Institución:** Instituto Tecnológico de Las Américas (ITLA)
