# Grade Tracker

A small Python application to manage students, courses and grades.

The project was created as a learning project while studying software engineering. 
It demonstrates object-oriented design, persistence with SQLite, repository and store patterns, 
unit testing and a simple Gradio user interface.

---

## Features implemented so far

- Student, Course and Grade management
- SQLite database for persistent storage
- Automatic database initialization with sample data
- Repository pattern for database access
- Store abstraction (InMemory and SQLite implementations)
- Statistical analysis
    - student averages
    - course averages
    - pass rates
    - top students
- JSON import/export
- CSV grade import/export
- Gradio dashboard

---

## Project Structure

```
grade_tracker/
│
├── app.py                  # Gradio application
├── sample_data.py          # Demo data
│
├── grade_management/
│   ├── student.py
│   ├── course.py
│   ├── grade.py
│   └── gradebook.py
│
├── grade_db/
│   ├── student_repository.py
│   ├── course_repository.py
│   ├── grade_repository.py
│
├── grade_store/
│   ├── grade_store.py
│   ├── in_memory_store.py
│   └── sqlite_store.py
│
└── tests/
```

---

## Architecture

The application follows a layered architecture.

```
Gradio UI
      │
      ▼
GradeBook
      │
      ▼
GradeStore
      │
      ▼
Repositories
      │
      ▼
SQLite
```

The UI communicates with the GradeBook.
The GradeBook contains the application logic and statistical methods.
The GradeStore abstracts the storage backend.
Repositories encapsulate all SQL operations.

---

## Technologies

- Python 3.13
- SQLite
- Gradio
- pytest
- dataclasses

---

## Running the project

Run the application

```bash
python app.py
```

On first startup the database is automatically populated with sample data.

---

## Dependencies

The project requires the following Python packages:

| Package | Purpose |
|---------|---------|
| gradio | Web-based graphical user interface |
| pytest | Unit testing framework |

The following modules are part of the Python standard library and do not require installation:

- sqlite3
- dataclasses
- csv
- json
- pathlib
- re
- typing

Install the required packages with:

```bash
pip install gradio pytest
```
