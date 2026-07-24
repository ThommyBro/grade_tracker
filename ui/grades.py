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
            grade.id,
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


def get_grade(self, grade_id: int) -> Grade | None:
    """
    Helper for grade IDs.
    Used in select_grade_from_table
    """
    grades = self.get_all_with_details()

    for grade in grades:
        if grade.id == grade_id:
            return grade

    return None


def select_grade_from_table(table, evt: gr.SelectData, store):

    row = evt.index[0]
    grade_id = table.iloc[row]["ID"]
    grade = store.get_grade(grade_id)

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
            value=f"{grade.student.first_name} {grade.student.last_name}",
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


def create_grade_view():
    """
    View for creating a new Grade.
    """
    return {
        "title": "### New Grade",

        "student": gr.update(
            value = "",
            interactive=True
        ),
        "course": gr.update(
            value="",
            interactive=True
        ),
        "score": gr.update(
            value=100,
            interactive=True
        ),
        "date": gr.update(
            value = 50,
            interactive = True
        ),
        "notes": gr.update(
            value = 50,
            interactive = True
        ),

        "cgradestate": {},
        "mode_state": "create",

        "save_button": gr.update(
            value="➕ Create Course",
            interactive=False
        ),

        "delete_button": gr.update(
            visible=False
        ),

        "cancel_button": gr.update(
            visible=True
        ),
    }


def grade_view_to_output(view):
    """
    Convert view dictionary into Gradio output tuple.
    Order must match event outputs.
    """
    return (
        view["title"],
        view["student"],
        view["course"],
        view["score"],
        view["date"],
        view["notes"],

        view["grade_state"],
        view["mode_state"],

        view["save_button"],
        view["delete_button"],
        view["cancel_button"],
    )

# ============================================================
# Build Tab
# ============================================================

def build_grade_tab(store):
    
    # state definition
    grade_state = gr.State(value={})
    mode_state = gr.State(value="empty")
    
    with gr.Tab("Grade"):
        # Header row
        with gr.Row():
            with gr.Column(scale = 5):
                gr.Markdown(
                    """
                    ## Grades
    
                    """
                )
            with gr.Column(scale= 1, min_width=120):
                add_button = gr.Button(
                    "➕ Add Grade",
                    variant="primary"
                )

        # Main content
        with gr.Row():

            # Left hand side - student list
            with gr.Column(scale=1):
                gr.Markdown("### Grade List"),
                grade_table = gr.Dataframe(
                    headers=[
                        "ID",
                        "Student",
                        "Course",
                        "Score",
                        "Date"
                    ],
                    
                    value=load_grade_table(store),
                    datatype=["str", "str","str","number","str"],
                    interactive=True,
                    wrap=True,
                    show_row_numbers=False,
                    #select_mode="row"
                )


            # Right hand side - Course details
            with gr.Column(scale=1):
                grade_title = gr.Markdown(
                    "### Grade Details"
                )
                student_box = gr.Textbox(
                    label="Student",
                    interactive=False,
                )
                course_name_box = gr.Textbox(
                    label="Course",
                    interactive=False
                )
                score_box = gr.Textbox(
                    label="Score",
                    interactive=False
                )
                date_box = gr.Textbox(
                    label="Date",
                    interactive=False
                )
                notes_box = gr.Textbox(
                    label="Notes",
                    interactive=False
                )
                

                with gr.Row():
                    save_button = gr.Button(
                        "💾 Save Changes",
                        variant="primary",
                        interactive=False
                    )
                    delete_button = gr.Button(
                        "🗑 Delete",
                        variant="stop",
                        visible=True,
                    )
                    cancel_button = gr.Button(
                        "❌ Cancel",
                        variant="secondary",
                        visible=False
                    )
                    status_message = gr.Markdown()

        return {
            "grade_title": grade_title,
            "grade_table": grade_table,

            "grade_state": grade_state,
            "mode_state": mode_state,

            "add_button": add_button,
            "save_button": save_button,
            "delete_button": delete_button,
            "cancel_button": cancel_button,

            "student_box" : student_box,
            "course_name_box": course_name_box,
            "score_box": score_box,
            "date_box": date_box,
            "notes_box": notes_box,

            "status_message": status_message,
        }
    