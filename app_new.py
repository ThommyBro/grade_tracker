import sys
import os
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path


from gradebook_new import GradeBook
from grade_management.course import Course
from grade_management.student import Student
from reports.csv_report import CsvReportGenerator
from reports.text_report import TextReportGenerator
from storage.sqlite_store import GradeDataBase

from exceptions import *

import gradio as gr
#import matplotlib
import matplotlib.pyplot as plt



# ---------------------------------------------------------------------- #
# Ein einzelnes, geteiltes GradeBook für die ganze App (SQLite-Datei neben
# dem Paket, überlebt also Neustarts). Für einen reinen In-Memory-Demo-Modus
# einfach GradeBook() ohne store= verwenden.
# ---------------------------------------------------------------------- #
# Ermittelt den genauen Ordner, in dem diese app_new.py liegt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "grades_new.db")
#DB_PATH = Path(__file__).resolve().parent / "grades_new.db"
MEMORY = ":memory:"
_GRADEBOOK: GradeBook | None = None


def get_gradebook() -> GradeBook:
    global _GRADEBOOK
    if _GRADEBOOK is None:
        _GRADEBOOK = GradeBook(store=GradeDataBase(str(DB_PATH)))
    return _GRADEBOOK


TEXT_GEN = TextReportGenerator()
CSV_GEN = CsvReportGenerator()
LETTERS = ("A", "B", "C", "D", "F")



# ======================================================================== #
#       Tables
# Use get_all_... functions
# ======================================================================== #
def _students_table_data(book: GradeBook) -> list[list]:
    rows = []
    for s in sorted(book.store.get_all_students(), key=lambda s: s.student_id):
        grades = book.get_student_grades(s.student_id)
        avg = f"{book.student_average(s.student_id):.1f}" if grades else "–"
        rows.append([s.student_id, s.first_name, s.last_name, s.email, avg])
    return rows


def _courses_table_data(book: GradeBook) -> list[list]:
    rows = []
    for c in sorted(book.store.get_all_courses(), key=lambda c: c.course_id):
        grades = book.get_course_grades(c.course_id)
        avg = f"{book.course_average(c.course_id):.1f}" if grades else "–"
        pass_rate = f"{book.course_pass_rate(c.course_id):.1f}%" if grades else "–"
        rows.append([c.course_id, c.name, c.max_grade, c.passing_grade, avg, pass_rate])
    return rows


def _grades_table_data(book: GradeBook, limit: int = 50) -> list[list]:
    grades = sorted(book.store.get_all_grades(), key=lambda g: g.date, reverse=True)[:limit]
    return [
        [
            g.grade_id,
            g.date,
            g.student.full_name,
            g.course.name,
            g.score,
            g.letter_grade,
            "passed" if g.is_passing else "failed",
            g.notes,
        ]
        for g in grades
    ]


def _enrolled_students_table(book: GradeBook, course_id: str) -> list[list]:
    """Studierende, die in einem Kurs mindestens eine Note haben ("eingeschrieben")."""
    try:
        grades = book.get_course_grades(course_id)
    except CourseNotFoundError:
        return []
    rows = sorted(grades, key=lambda g: g.student.full_name)
    return [
        [g.student.full_name, g.score, g.letter_grade, "bestanden" if g.is_passing else "nicht bestanden"]
        for g in rows
    ]


def _top_students_table(book: GradeBook) -> list[list]:
    return [[s.full_name, f"{avg:.1f}%"] for s, avg in book.top_students(n=10)]


def _at_risk_table(book: GradeBook) -> list[list]:
    return [
        [s.full_name, f"{book.student_average(s.student_id):.1f}%"]
        for s in book.students_at_risk()
    ]


def _dashboard_summary_md(book: GradeBook) -> str:
    return (
        "### Overview\n\n"
        f"- **Students:** {len(book.students)}\n"
        f"- **Courses:** {len(book.courses)}\n"
        f"- **Grades:** {len(book.grades)}\n"
    )


def _grade_distribution_figure(book: GradeBook):
    counts = Counter(g.letter_grade for g in book.store.get_all_grades())
    values = [counts.get(letter, 0) for letter in LETTERS]

    fig, ax = plt.subplots(figsize=(5, 3.2))
    colors = ["#2e7d32", "#66bb6a", "#fdd835", "#fb8c00", "#e53935"]
    bars = ax.bar(LETTERS, values, color=colors)
    ax.set_ylabel("Grade Count")
    ax.set_title("Grade Distribution")
    ax.set_ylim(0, max(values + [1]) + 1)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            str(value),
            ha="center",
            va="bottom",
        )
    fig.tight_layout()
    return fig


def _row_index_from_event(evt: "gr.SelectData") -> int | None:
    idx = evt.index
    if isinstance(idx, (list, tuple)):
        return idx[0] if idx else None
    return idx


def _to_rows(table_value) -> list[list]:
    """
    Gets sure to have always ordinary lists. Easier handling for ids.
    """
    if table_value is None:
        return []

    if hasattr(table_value, "values") and hasattr(table_value, "columns"):
        # if pandas Dataframe -> list[List]
        return table_value.values.tolist()

    if isinstance(table_value, dict) and "data" in table_value:
        # if dict, use "data" entry
        return table_value["data"]

    # if list, just use it
    return list(table_value)


def full_refresh():
    """
    Refreshes all tables, dropdowns, boards etc. automatically
    """
    book = get_gradebook()
    s_choices = [(f"{s.full_name} ({s.student_id})", s.student_id) for s in book.store.get_all_students()]
    c_choices = [(f"{c.name} ({c.course_id})", c.course_id) for c in book.store.get_all_courses()]
    return (
        _students_table_data(book),
        gr.Dropdown(choices=s_choices),
        gr.Dropdown(choices=s_choices),
        gr.Dropdown(choices=s_choices),
        _courses_table_data(book),
        gr.Dropdown(choices=c_choices),
        gr.Dropdown(choices=c_choices),
        gr.Dropdown(choices=c_choices),
        _grades_table_data(book),
        _dashboard_summary_md(book),
        _top_students_table(book),
        _at_risk_table(book),
        _grade_distribution_figure(book),
    )


# ======================================================================== #
# Button Handler: Student CRUD Actions
# ======================================================================== #
def add_student_handler(student_id, first_name, last_name, email):
    book = get_gradebook()
    try:
        book.add_student(
            Student(
                (student_id or "").strip(),
                (first_name or "").strip(),
                (last_name or "").strip(),
                (email or "").strip(),
            )
        )
        msg = f"✅ '{first_name} {last_name}' ({student_id}) was added."
        gr.Info(msg)
        full_refresh()
        # Empty form for a next student
        return  "", "", "", ""
    except (ValueError, DuplicateEntryError) as exc:
        # Error message, also leaves form as is
        gr.Info(f"❌ Error: {exc}")
        return student_id, first_name, last_name, email


def filter_students_handler(query):
    book = get_gradebook()
    if not query or not query.strip():
        return _students_table_data(book)
    rows = []
    for s in sorted(book.search_students(query.strip()), key=lambda s: s.student_id):
        grades = book.get_student_grades(s.student_id)
        avg = f"{book.student_average(s.student_id):.1f}" if grades else "–"
        rows.append([s.student_id, s.first_name, s.last_name, s.email, avg])
    return rows


def on_student_row_select(evt: gr.SelectData, current_table):
    rows = _to_rows(current_table)
    row_idx = _row_index_from_event(evt)
    if not rows or row_idx is None or row_idx >= len(rows):
        return gr.Group(visible=False), "", "", "", "", gr.Group(visible=False)

    student_id = str(rows[row_idx][0])  # Spalte 0 = student_id (str(), falls Gradio/pandas daraus eine Zahl gemacht hat)
    book = get_gradebook()
    try:
        s = book.store.get_student(student_id)
    except StudentNotFoundError:
        return gr.Group(visible=False), "", "", "", "", gr.Group(visible=False)

    return (
        gr.Group(visible=True),   # check: Panel "einfliegen" lassen
        s.student_id,              # why NONE?
        s.first_name,
        s.last_name,
        s.email,
        gr.Group(visible=False),  # eine evtl. offene Lösch-Bestätigung von vorher wieder einklappen
    )


def save_student_handler(student_id, first_name, last_name, email):
    """Saves changes on updates."""
    if not student_id:
        return "❌ No Student selected.", gr.Group(visible=True)
    book = get_gradebook()
    try:
        updated = Student(
            student_id, (first_name or "").strip(), (last_name or "").strip(), (email or "").strip()
        )
        book.update_student(updated)
        gr.Info(f"✅ '{updated.full_name}' was updated.")
        return f"gr.Group(visible=False)"
    
    except (ValueError, StudentNotFoundError) as exc:
        return f"❌ Error: {exc}", gr.Group(visible=True)


def request_delete_student_handler(student_id):
    """First Click. Asks for confirmation."""
    if not student_id:
        return gr.Group(visible=False), ""
    book = get_gradebook()
    try:
        # Count number of grades for this student
        n = len(book.get_student_grades(student_id))
    except StudentNotFoundError:
        return gr.Group(visible=False), "❌ Student doesn't exist."

    if n:
        warning = (
            f"⚠️ **Attention:** This student got **{n} grades** recorded. "
            f"If you delete this student all grades will be also deleted."
            f"Continue?"
        )
    else:
        warning = "No grades are recorded. Do you really want to delete this student?"
    return gr.Group(visible=True), warning


def confirm_delete_student_handler(student_id):
    """Second click: Confirmation for delete."""
    book = get_gradebook()
    try:
        book.delete_student(student_id)
        msg = "✅ Student and all corresponding grades are deleted."
        gr.Info(msg)
    except StudentNotFoundError as exc:
        msg = f"❌ Error: {exc}"
    # Close both panels
    return gr.Group(visible=False), gr.Group(visible=False)


def cancel_delete_student_handler():
    return gr.Group(visible=False)


def close_student_panel_handler():
    return gr.Group(visible=False), gr.Group(visible=False)


def view_student_report_handler(student_id):
    if not student_id:
        return "Select a student."
    return TEXT_GEN.generate_student_report(student_id, get_gradebook())



# ======================================================================== #
# Button Handler: Course CRUD Actions
# ======================================================================== #
def add_course_handler(course_id, name, max_grade, passing_grade):
    book = get_gradebook()
    try:
        book.add_course(
            Course((course_id or "").strip(), (name or "").strip(), float(max_grade), float(passing_grade))
        )
        msg = f"✅ Course '{name}' ({course_id}) was added."
        gr.Info(msg)
        return "", "", 100, 50
    except (ValueError, DuplicateEntryError, TypeError) as exc:
        gr.Info(f"❌ Error: {exc}")
        return course_id, name, max_grade, passing_grade


def filter_courses_handler(query):
    book = get_gradebook()
    if not query or not query.strip():
        return _courses_table_data(book)
    rows = []
    for c in sorted(book.search_courses(query.strip()), key=lambda c: c.course_id):
        grades = book.get_course_grades(c.course_id)
        avg = f"{book.course_average(c.course_id):.1f}" if grades else "–"
        pass_rate = f"{book.course_pass_rate(c.course_id):.1f}%" if grades else "–"
        rows.append([c.course_id, c.name, c.max_grade, c.passing_grade, avg, pass_rate])
    return rows


def on_course_row_select(evt: gr.SelectData, current_table):
    rows = _to_rows(current_table)
    row_idx = _row_index_from_event(evt)
    if not rows or row_idx is None or row_idx >= len(rows):
        return gr.Group(visible=False), "", "", 100, 50, gr.Group(visible=False), []

    course_id = str(rows[row_idx][0])  # Spalte 0 = course_id (str(), falls Gradio/pandas daraus eine Zahl gemacht hat)
    book = get_gradebook()
    try:
        c = book.store.get_course(course_id)
    except CourseNotFoundError:
        return gr.Group(visible=False), "", "", 100, 50, gr.Group(visible=False), []

    return (
        gr.Group(visible=True),
        c.course_id,
        c.name,
        c.max_grade,
        c.passing_grade,
        gr.Group(visible=False),
        _enrolled_students_table(book, course_id),
    )


def save_course_handler(course_id, name, max_grade, passing_grade):
    if not course_id:
        return "❌ No Course selected.", gr.Group(visible=True)
    book = get_gradebook()
    try:
        updated = Course(course_id, (name or "").strip(), float(max_grade), float(passing_grade))
        book.update_course(updated) # update course does the real check up
        gr.Info(f"✅ Course '{updated.name}' was updated.")
        return gr.Group(visible=False)
    except (ValueError, CourseNotFoundError, TypeError) as exc:
        return f"❌ Error: {exc}", gr.Group(visible=True)


def request_delete_course_handler(course_id):
    if not course_id:
        return gr.Group(visible=False), ""
    book = get_gradebook()
    try:
        n = len(book.get_course_grades(course_id))
    except CourseNotFoundError:
        return gr.Group(visible=False), "❌ Course doesn't exist."

    if n:
        warning = (
            f"⚠️ **Attention:** There are **{n} grades** recorded for this course. "
            f"If you delete this course all grades will be also deleted"
            f"Continue"
        )
    else:
        warning = "No grades are recorded. Do you really want to delete this course?"
    return gr.Group(visible=True), warning


def confirm_delete_course_handler(course_id):
    book = get_gradebook()
    try:
        book.delete_course(course_id)
        msg = "✅ Course and all corresponding grades were deleted."
        gr.Info(msg)
    except CourseNotFoundError as exc:
        msg = f"❌ Error: {exc}"
    return gr.Group(visible=False), gr.Group(visible=False)


def cancel_delete_course_handler():
    return gr.Group(visible=False)


def close_course_panel_handler():
    return gr.Group(visible=False), gr.Group(visible=False)


def view_course_report_handler(course_id):
    if not course_id:
        return "Select a course."
    return TEXT_GEN.generate_course_report(course_id, get_gradebook())



# ======================================================================== #
# Button Handler: Grade CRUD Action
# ======================================================================== #
def update_course_hint_handler(course_id):
    if not course_id:
        return ""
    book = get_gradebook()
    try:
        c = book.store.get_course(course_id)
    except CourseNotFoundError:
        return ""
    return f"ℹ️ **{c.name}**: max. {c.max_grade:.0f} Score · Passing Grade {c.passing_grade:.0f}"


def record_grade_handler(student_id, course_id, score, grade_date, notes):
    if not student_id or not course_id:
        return "❌ Select a studend and a course.", student_id, score, notes
    book = get_gradebook()
    try:
        grade = book.add_grade(
            student_id, course_id, float(score), (grade_date or "").strip(), (notes or "").strip()
        )
        msg = (
            f"✅ Grade recorded: {grade.student.full_name} – {grade.course.name}: "
            f"{grade.score} ({grade.letter_grade})"
        )
        return msg, None, None, ""
    except (ValueError, StudentNotFoundError, CourseNotFoundError, TypeError) as exc:
        return f"❌ Error: {exc}", student_id, score, notes


def import_csv_handler(file):
    if file is None:
        return "Choose a CSV File first."
    book = get_gradebook()
    path = file.name if hasattr(file, "name") else file
    report = persistence.import_csv(book, path)
    return str(report)


def on_grade_row_select(evt: gr.SelectData, current_table):
    rows = _to_rows(current_table)
    row_idx = _row_index_from_event(evt)
    if not rows or row_idx is None or row_idx >= len(rows):
        return gr.Group(visible=False), "", "", "", 0, "", "", gr.Group(visible=False)

    grade_id = str(rows[row_idx][0])  
    book = get_gradebook()
    try:
        g = book.get_grade(grade_id)
    except GradeNotFoundError:
        return gr.Group(visible=False), "", "", "", 0, "", "", gr.Group(visible=False)

    return (
        gr.Group(visible=True),
        g.grade_id,
        g.student.full_name,   
        g.course.name,          
        g.score,
        g.date,
        g.notes,
        gr.Group(visible=False),
    )


def save_grade_handler(grade_id, score, grade_date, notes):
    if not grade_id:
        return "❌ No grade choosen", gr.Group(visible=True)
    book = get_gradebook()
    try:
        updated = book.update_grade(grade_id, float(score), (grade_date or "").strip(), (notes or "").strip())
        msg = f"✅ Grade was updated: {updated.score} ({updated.letter_grade})."
        gr.Info(msg)
        return gr.Group(visible=False)
    except (ValueError, GradeNotFoundError, TypeError) as exc:
        msg = f"❌ Error: {exc}"
        gr.Info(msg)
        return gr.Group(visible=True)


def request_delete_grade_handler(grade_id):
    if not grade_id:
        return gr.Group(visible=False), ""
    return gr.Group(visible=True), "Really delete this grade?"


def confirm_delete_grade_handler(grade_id):
    book = get_gradebook()
    try:
        book.delete_grade(grade_id)
        msg = "✅ Grade was deleted."
        gr.Info(msg)
    except GradeNotFoundError as exc:
        msg = f"❌ Error: {exc}"
        gr.Info(msg)
    return gr.Group(visible=False), gr.Group(visible=False)


def cancel_delete_grade_handler():
    return gr.Group(visible=False)


def close_grade_panel_handler():
    return gr.Group(visible=False), gr.Group(visible=False)



# ======================================================================== #
# DEMO Data Generator
# ======================================================================== #
def load_demo_data_handler():
    book = get_gradebook()
    demo_students = [
        ("s1", "Anna", "Alpha", "anna@uni.com"),
        ("s2", "Ben", "Beta", "ben@uni.com"),
        ("s3", "Clara", "Gamma", "clara@uni.com"),
        ("s4", "David", "Delta", "david@uni.com"),
    ]
    demo_courses = [
        ("c1", "Category Theory", 100.0, 50.0),
        ("c2", "Python 101", 100.0, 60.0),
        ("c3", "QM 1", 100, 50),
    ]
    demo_grades = [
        ("s1", "c1", 92, "2026-01-15"),
        ("s1", "c2", 17, "2026-01-20"),
        ("s1", "c3", 95, "2026-01-25"),
        ("s2", "c1", 55, "2026-01-15"),
        ("s2", "c2", 8, "2026-01-20"),
        ("s3", "c3", 85, "2026-01-25"),
        ("s3", "c1", 78, "2026-01-15"),
        ("s3", "c2", 12, "2026-01-20"),
        ("s3", "c3", 17, "2026-01-25"),
        ("s4", "c1", 41, "2026-01-15"),
        ("s4", "c2", 6, "2026-01-20"),
        ("s4", "c3", 51, "2026-01-25"),
    ]
    for sid, fn, ln, email in demo_students:
        try:
            book.add_student(Student(sid, fn, ln, email))
        except DuplicateEntryError:
            pass
    for cid, name, max_g, pass_g in demo_courses:
        try:
            book.add_course(Course(cid, name, max_g, pass_g))
        except DuplicateEntryError:
            pass
    for sid, cid, score, grade_date in demo_grades:
        try:
            book.add_grade(sid, cid, score, grade_date)
        except (ValueError, StudentNotFoundError, CourseNotFoundError):
            pass
    return "✅ Demo-Data loaded"

# ======================================================================== #
# Reports
# ======================================================================== #
def generate_report_handler(report_type, format_, student_id, course_id):
    book = get_gradebook()
    generator = TEXT_GEN if format_ == "Text" else CSV_GEN
    suffix = "txt" if format_ == "Text" else "csv"

    try:
        if report_type == "Student report":
            if not student_id:
                return "Please choose a student", None
            content = generator.generate_student_report(student_id, book)
            filename = f"student_{student_id}.{suffix}"
        elif report_type == "Course report":
            if not course_id:
                return "Please choose a Course", None
            content = generator.generate_course_report(course_id, book)
            filename = f"course_{course_id}.{suffix}"
        else:
            content = generator.generate_summary_report(book)
            filename = f"summary.{suffix}"
    except (StudentNotFoundError, CourseNotFoundError) as exc:
        return f"❌ Error: {exc}", None

    out_dir = Path(tempfile.gettempdir()) / "grade_tracker_reports"
    out_dir.mkdir(exist_ok=True)
    path = out_dir / filename
    path.write_text(content, encoding="utf-8")
    return content, str(path)


# ======================================================================== #
# UI
# ======================================================================== #
with gr.Blocks(
    title="Grade Tracker",
    theme=gr.Theme.from_hub("KevinGeng/Laronix"),
    #css=CUSTOM_CSS,
) as demo:
    gr.Markdown("# 📚 Grade Tracker", elem_classes=["app-title"])
    gr.Markdown("Dashboard for students, courses and grades.")


# --- Students Tab --- #
    with gr.Tab("👥 Students"):
        with gr.Row():
            with gr.Column(scale=2):
                student_search = gr.Textbox(
                    label="🔍 Search (Name or E-Mail)", placeholder="e.g. Anna or @uni.com"
                )
                students_table = gr.Dataframe(
                    headers=["ID", "Firstname", "Lastname", "E-Mail", "Ø (%)"],
                    interactive=False,
                )
                gr.Markdown("💡 Click a row to edit.", elem_classes=["hint-text"])
            with gr.Column(scale=1):
                gr.Markdown("### Add new student")
                new_student_id = gr.Textbox(label="Studend-ID")
                new_first_name = gr.Textbox(label="Firstname")
                new_last_name = gr.Textbox(label="Lastname")
                new_email = gr.Textbox(label="E-Mail")
                add_student_btn = gr.Button("➕ Add", variant="primary")
                #add_student_status = gr.Textbox(label="Status", interactive=False)


        with gr.Group(visible=False, elem_classes=["slide-panel"]) as edit_student_panel:
            gr.Markdown("### ✏️ Edit Student")
            edit_student_id_display = gr.Textbox(label="ID (not editable)", interactive=False)
            with gr.Row():
                edit_student_first_name = gr.Textbox(label="Firstname")
                edit_student_last_name = gr.Textbox(label="Lastname")
            edit_student_email = gr.Textbox(label="E-Mail")
            with gr.Row():
                save_student_btn = gr.Button("💾 Save", variant="primary")
                delete_student_btn = gr.Button("🗑️ Delete", variant="stop")
                close_student_panel_btn = gr.Button("✖ Close")
            #edit_student_status = gr.Textbox(label="Status", interactive=False)

            with gr.Group(visible=False, elem_classes=["confirm-panel"]) as delete_student_confirm:
                delete_student_warning = gr.Markdown()
                with gr.Row():
                    confirm_delete_student_btn = gr.Button("✅ Yes, delete permanently", variant="stop")
                    cancel_delete_student_btn = gr.Button("Cancel")


        gr.Markdown("### Individual Report")
        with gr.Row():
            with gr.Column(scale=1):
                dd_view_student = gr.Dropdown(label="Students", choices=[])
                view_student_btn = gr.Button("Show Report")
            with gr.Column(scale=2):
                student_report_box = gr.Textbox(label="Report", lines=10, interactive=False)


# ---  Course Tab --- #
    with gr.Tab("📘 Courses"):
        with gr.Row():
            with gr.Column(scale=2):
                course_search = gr.Textbox(label="🔍 Search (Coursename)", placeholder="e.g. Mathematics")
                courses_table = gr.Dataframe(
                    headers=["ID", "Name", "Max. Score", "Passing Score", "Ø", "Passing Quota"],
                    interactive=False,
                )
                gr.Markdown("💡 Click a row to edit.", elem_classes=["hint-text"])
            with gr.Column(scale=1):
                gr.Markdown("### Add new Course")
                new_course_id = gr.Textbox(label="Kurs-ID")
                new_course_name = gr.Textbox(label="Name")
                new_max_grade = gr.Number(label="Max Score", value=100)
                new_passing_grade = gr.Number(label="Passing grade", value=50)
                add_course_btn = gr.Button("➕ Add", variant="primary")
                #add_course_status = gr.Textbox(label="Status", interactive=False)

        with gr.Group(visible=False, elem_classes=["slide-panel"]) as edit_course_panel:
            gr.Markdown("### ✏️ Edit Course")
            edit_course_id_display = gr.Textbox(label="ID (not editable)", interactive=False)
            edit_course_name = gr.Textbox(label="Name")
            with gr.Row():
                edit_course_max_grade = gr.Number(label="Max Score")
                edit_course_passing_grade = gr.Number(label="Passing grade")
            with gr.Row():
                save_course_btn = gr.Button("💾 Save", variant="primary")
                delete_course_btn = gr.Button("🗑️ Delete", variant="stop")
                close_course_panel_btn = gr.Button("✖ Close")
            #edit_course_status = gr.Textbox(label="Status", interactive=False)

            with gr.Group(visible=False, elem_classes=["confirm-panel"]) as delete_course_confirm:
                delete_course_warning = gr.Markdown()
                with gr.Row():
                    confirm_delete_course_btn = gr.Button("✅ Yes, delete permanently", variant="stop")
                    cancel_delete_course_btn = gr.Button("Cancel")

            
            gr.Markdown("#### 👥 Eingeschriebene Studierende")
            enrolled_students_table = gr.Dataframe(
                headers=["Studierende/r", "Punkte", "Note", "Status"], interactive=False
            )

        gr.Markdown("### Course Statistics (Text Report)")
        with gr.Row():
            dd_view_course = gr.Dropdown(label="Course", choices=[])
            view_course_btn = gr.Button("Show Statistics")
        course_report_box = gr.Textbox(label="Report", lines=10, interactive=False)


# --- Grade Tab --- #
    with gr.Tab("📝 Grades"):
        gr.Markdown("### Add Grade")
        with gr.Row():
            dd_grade_student = gr.Dropdown(label="Students", choices=[])
            dd_grade_course = gr.Dropdown(label="Course", choices=[])
        # Feature: zeigt live die Punktegrenzen des gewählten Kurses an.
        course_limit_hint = gr.Markdown()
        with gr.Row():
            grade_score = gr.Number(label="Grade Score")
            grade_date = gr.Textbox(label="Date (YYYY-MM-DD)", value=date.today().isoformat())
            grade_notes = gr.Textbox(label="Notes (optional)")
        record_grade_btn = gr.Button("✅ Add Grade", variant="primary")
        #record_grade_status = gr.Textbox(label="Status", interactive=False)

        gr.Markdown("### Last recorded Grades")
        grades_table = gr.Dataframe(
            headers=["ID", "Date", "Students", "Course", "Score", "Grade", "Status", "Notes"],
            interactive=False,
        )
        gr.Markdown("💡 Click a row to edit.", elem_classes=["hint-text"])

        with gr.Group(visible=False, elem_classes=["slide-panel"]) as edit_grade_panel:
            gr.Markdown("### ✏️ Edit Grade")
            edit_grade_id_display = gr.Textbox(label="Grade-ID (not editable)", interactive=False)
            with gr.Row():
                edit_grade_student_display = gr.Textbox(label="Students", interactive=False)
                edit_grade_course_display = gr.Textbox(label="Course", interactive=False)
            with gr.Row():
                edit_grade_score = gr.Number(label="Grade Score")
                edit_grade_date = gr.Textbox(label="Date (YYYY-MM-DD)")
            edit_grade_notes = gr.Textbox(label="Notes")
            with gr.Row():
                save_grade_btn = gr.Button("💾 Save", variant="primary")
                delete_grade_btn = gr.Button("🗑️ Delete", variant="stop")
                close_grade_panel_btn = gr.Button("✖ Close")
            #edit_grade_status = gr.Textbox(label="Status", interactive=False)

            with gr.Group(visible=False, elem_classes=["confirm-panel"]) as delete_grade_confirm:
                delete_grade_warning = gr.Markdown()
                with gr.Row():
                    confirm_delete_grade_btn = gr.Button("✅ Yes, delete permanently", variant="stop")
                    cancel_delete_grade_btn = gr.Button("Cancel")

        with gr.Accordion("CSV-Import (student_id,course_id,score,date[,notes])", open=False):
            csv_file = gr.File(label="CSV-File", file_types=[".csv"])
            import_csv_btn = gr.Button("CSV import")
            import_csv_status = gr.Textbox(label="Import-Result", lines=6, interactive=False)


    # --- Reports Tab --- #
    with gr.Tab("📄 Reports"):
        with gr.Row():
            report_type = gr.Radio(
                ["Student Report", "Course Report", "Summary"],
                label="Report Type",
                value="Summary",
            )
            report_format = gr.Radio(["Text", "CSV"], label="Format", value="Text")
        with gr.Row():
            dd_report_student = gr.Dropdown(label="Studients (for student report)", choices=[])
            dd_report_course = gr.Dropdown(label="Course (for Course report)", choices=[])
        generate_report_btn = gr.Button("📄 Generate Report", variant="primary")
        report_output = gr.Textbox(label="Preview", lines=16, interactive=False)
        report_file = gr.File(label="Download")


    # --- Dashboard Tab --- #
    with gr.Tab("📊 Dashboard"):
        demo_data_btn = gr.Button("🧪 Load Demo Data")
        demo_data_status = gr.Textbox(label="Status", interactive=False)
        dash_summary = gr.Markdown()
        with gr.Row():
            dash_top_table = gr.Dataframe(
                headers=["Students", "Mean"], label="🏆 Top Students", interactive=False
            )
            dash_risk_table = gr.Dataframe(
                headers=["Students", "Mean"],
                label="⚠️ Students at Risk(<60%)",
                interactive=False,
            )
        dash_chart = gr.Plot(label="Grade Distritbution")


# --- Wiring: Button Click to corresponding functions --- #

    ALL_REFRESH_OUTPUTS = [
        students_table, dd_view_student, dd_grade_student, dd_report_student,
        courses_table, dd_view_course, dd_grade_course, dd_report_course,
        grades_table,
        dash_summary, dash_top_table, dash_risk_table, dash_chart,
    ]


    # ---- Students ---- #
    add_student_btn.click(
        add_student_handler,
        inputs=[new_student_id, new_first_name, new_last_name, new_email],
        outputs=[#add_student_status, 
            new_student_id, new_first_name, new_last_name, new_email],
    ).then(full_refresh, outputs=ALL_REFRESH_OUTPUTS)

    student_search.change(filter_students_handler, inputs=[student_search], outputs=[students_table])

    students_table.select(
        on_student_row_select,
        inputs=[students_table],
        outputs=[
            edit_student_panel, edit_student_id_display, edit_student_first_name,
            edit_student_last_name, edit_student_email, delete_student_confirm,
        ],
    )


    student_search.change(filter_students_handler, inputs=[student_search], outputs=[students_table])

    students_table.select(
        on_student_row_select,
        inputs=[students_table],
        outputs=[
            edit_student_panel, edit_student_id_display, edit_student_first_name,
            edit_student_last_name, edit_student_email, delete_student_confirm,
        ],
    )

    save_student_btn.click(
        save_student_handler,
        inputs=[edit_student_id_display, edit_student_first_name, edit_student_last_name, edit_student_email],
        outputs=[#edit_student_status, 
            edit_student_panel],
    ).then(full_refresh, outputs=ALL_REFRESH_OUTPUTS)

    delete_student_btn.click(
        request_delete_student_handler,
        inputs=[edit_student_id_display],
        outputs=[delete_student_confirm, delete_student_warning],
    )
    confirm_delete_student_btn.click(
        confirm_delete_student_handler,
        inputs=[edit_student_id_display],
        outputs=[#edit_student_status, 
            delete_student_confirm, edit_student_panel],
    ).then(full_refresh, outputs=ALL_REFRESH_OUTPUTS)
    cancel_delete_student_btn.click(cancel_delete_student_handler, outputs=[delete_student_confirm])
    close_student_panel_btn.click(
        close_student_panel_handler, outputs=[edit_student_panel, delete_student_confirm]
    )

    view_student_btn.click(view_student_report_handler, inputs=[dd_view_student], outputs=[student_report_box])

    # ---- Courses ---- #
    add_course_btn.click(
        add_course_handler,
        inputs=[new_course_id, new_course_name, new_max_grade, new_passing_grade],
        outputs=[#add_course_status, 
            new_course_id, new_course_name, new_max_grade, new_passing_grade],
    ).then(full_refresh, outputs=ALL_REFRESH_OUTPUTS)

    course_search.change(filter_courses_handler, inputs=[course_search], outputs=[courses_table])

    courses_table.select(
        on_course_row_select,
        inputs=[courses_table],
        outputs=[
            edit_course_panel, edit_course_id_display, edit_course_name,
            edit_course_max_grade, edit_course_passing_grade, delete_course_confirm,
            enrolled_students_table,
        ],
    )

    save_course_btn.click(
        save_course_handler,
        inputs=[edit_course_id_display, edit_course_name, edit_course_max_grade, edit_course_passing_grade],
        outputs=[#edit_course_status, 
            edit_course_panel],
    ).then(full_refresh, outputs=ALL_REFRESH_OUTPUTS)

    delete_course_btn.click(
        request_delete_course_handler,
        inputs=[edit_course_id_display],
        outputs=[delete_course_confirm, delete_course_warning],
    )
    confirm_delete_course_btn.click(
        confirm_delete_course_handler,
        inputs=[edit_course_id_display],
        outputs=[#edit_course_status,
                 delete_course_confirm, edit_course_panel],
    ).then(full_refresh, outputs=ALL_REFRESH_OUTPUTS)
    cancel_delete_course_btn.click(cancel_delete_course_handler, outputs=[delete_course_confirm])
    close_course_panel_btn.click(
        close_course_panel_handler, outputs=[edit_course_panel, delete_course_confirm]
    )

    view_course_btn.click(view_course_report_handler, inputs=[dd_view_course], outputs=[course_report_box])

    # ---- Grades ---- #
    dd_grade_course.change(update_course_hint_handler, inputs=[dd_grade_course], outputs=[course_limit_hint])

    record_grade_btn.click(
        record_grade_handler,
        inputs=[dd_grade_student, dd_grade_course, grade_score, grade_date, grade_notes],
        outputs=[#record_grade_status, 
                 dd_grade_student, grade_score, grade_notes],
    ).then(full_refresh, outputs=ALL_REFRESH_OUTPUTS)

    import_csv_btn.click(
        import_csv_handler, inputs=[csv_file], outputs=[import_csv_status]
    ).then(full_refresh, outputs=ALL_REFRESH_OUTPUTS)

    grades_table.select(
        on_grade_row_select,
        inputs=[grades_table],
        outputs=[
            edit_grade_panel, edit_grade_id_display, edit_grade_student_display,
            edit_grade_course_display, edit_grade_score, edit_grade_date,
            edit_grade_notes, delete_grade_confirm,
        ],
    )

    save_grade_btn.click(
        save_grade_handler,
        inputs=[edit_grade_id_display, edit_grade_score, edit_grade_date, edit_grade_notes],
        outputs=[#edit_grade_status, 
                 edit_grade_panel],
    ).then(full_refresh, outputs=ALL_REFRESH_OUTPUTS)

    delete_grade_btn.click(
        request_delete_grade_handler,
        inputs=[edit_grade_id_display],
        outputs=[delete_grade_confirm, delete_grade_warning],
    )
    confirm_delete_grade_btn.click(
        confirm_delete_grade_handler,
        inputs=[edit_grade_id_display],
        outputs=[#edit_grade_status, 
                 delete_grade_confirm, edit_grade_panel],
    ).then(full_refresh, outputs=ALL_REFRESH_OUTPUTS)
    cancel_delete_grade_btn.click(cancel_delete_grade_handler, outputs=[delete_grade_confirm])
    close_grade_panel_btn.click(
        close_grade_panel_handler, outputs=[edit_grade_panel, delete_grade_confirm]
    )

    # ---- Reports ---- #
    generate_report_btn.click(
        generate_report_handler,
        inputs=[report_type, report_format, dd_report_student, dd_report_course],
        outputs=[report_output, report_file],
    )

    # ---- Dashboard & Demo-Data ---- #
    demo_data_btn.click(
        load_demo_data_handler, outputs=[demo_data_status]
    ).then(full_refresh, outputs=ALL_REFRESH_OUTPUTS)

    # Refresh on first load
    demo.load(full_refresh, outputs=ALL_REFRESH_OUTPUTS)




if __name__ == "__main__":
    #demo.launch()
    demo.launch(server_name="127.0.0.1", server_port=7860)

