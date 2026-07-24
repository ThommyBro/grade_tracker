import gradio as gr

from grade_management.student import Student
from grade_management.course import Course
from grade_management.grade import Grade




# ============================================================
# Table handling
# ============================================================

def load_grade_table(store):
    """
    Load grades from store and prepare dataframe rows.
    """
    grades = store.get_all_grades()

    rows = [
        [
            f"{grade.student.first_name} {grade.student.last_name}",
            grade.course.name,
            grade.score,
            grade.date
        ]
        for grade in grades
    ]
    return rows



def refresh_grade_table(store):
    """Reload grade table."""
    return load_grade_table(store)


def select_grade_from_table(table, evt: gr.SelectData, store):
    """
    Select grade from table row.
    """
    row = evt.index[0]
    grades = store.get_all_grades()
    grade = grades[row]

    return render_grade_details(
        "edit",
        grade,
        store,
    )

def render_grade_details(mode, grade=None, store=None,):
    """
    Build grade view depending on view mode.
    """
    if mode == "empty":
        view = empty_grade_view()
    elif mode == "create":
        view = create_grade_view()
    elif mode == "edit":
        if grade is None:
            view = empty_grade_view()
        else:
            view = populate_grade_view(grade, store)
    else:
        view = empty_grade_view()

    return grade_view_to_output(view)



def populate_grade_view(grade: Grade, store):

    grade_state = {
        "student_id": grade.student.student_id,
        "course_id": grade.course.course_id,
        "score": grade.score,
        "date": grade.date,
        "notes": grade.notes,
    }

    return {
        "title": "### Grade Details",

        "student": gr.update(
            value=f"{grade.student.first_name} {grade.student.last_name}"
            interactive=False,
        ),

        "course": gr.update(
            value=grade.course.name,
            interactive=False,
        ),

        "score": gr.update(
            value=grade.score,
            interactive=True,
        ),

        "date": gr.update(
            value=grade.date,
            interactive=True,
        ),
        "notes": gr.update(
            value=grade.notes,
            interactive=True,
        ),

        "grade_state": grade_state,
        "mode_state": "edit",

        "save_button": gr.update(
            value="💾 Save Changes",
            interactive=False,
        ),

        "delete_button": gr.update(
            visible=True,
        ),

        "cancel_button": gr.update(
            visible=True,
        ),
    }


def empty_grade_view():
    """
    Empty grade detail card.
    """
    return {
        "title": "### Grade Details",

        
        "student": "",
        "course": "",
        "score": "",
        "date": "",
        "notes":"",

        "grade_state": {},
        "mode_state": "empty",

        "save_button": gr.update(
            value="💾 Save Changes",
            interactive=False
        ),

        "delete_button": gr.update(
            visible=False
        ),

        "cancel_button": gr.update(
            visible=False
        ),
    }



def build_grade_tab():
    ...