import gradio as gr
from grade_management.student import Student



# =============================================
# UI
# =============================================


def build_student_tab(store):
    
    student_state = gr.State(value=[])

    with gr.Tab("Students"):
        # Header row
        with gr.Row():
            with gr.Column(scale = 5):
                gr.Markdown(
                    """
                    ## Students
                    Manage students and their academic information.
                    """
                )
            with gr.Column(scale= 1, min_width=120):
                add_button = gr.Button(
                    "➕ Add Student",
                    variant="primary"
                )

        # Main content
        with gr.Row():

            # Left hand side - student list
            with gr.Column(scale=1):
                gr.Markdown(
                    "### Student List"
                )
                student_table = gr.Dataframe(
                    headers=[
                        "ID",
                        "Student"
                    ],
                    
                    value=load_student_table(store),
                    datatype=["str", "str",],
                    interactive=False,
                    wrap=True,
                )


            # Right hand side - Student details
            with gr.Column(scale=1):
                gr.Markdown(
                    "### Student Details"
                )
                student_id_box = gr.Textbox(
                    label="Student ID",
                    interactive=False,
                )
                student_first_name_box = gr.Textbox(
                    label="First Name",
                    interactive=True
                )
                student_last_name_box = gr.Textbox(
                    label="Last Name",
                    interactive=True
                )
                student_email_box = gr.Textbox(
                    label="Email",
                    interactive=True
                )
                student_courses_box = gr.Textbox(
                    label="Courses",
                    lines=5,
                    interactive=False
                )
                student_average_box = gr.Textbox(
                    label="Average Grade",
                    interactive=False
                )

                with gr.Row():

                    # edit_button = gr.Button(
                    #     "✏ Edit"
                    # )
                    save_button = gr.Button(
                        "💾 Save Changes",
                        variant="primary",
                        interactive=False
                    )
                    delete_button = gr.Button(
                        "🗑 Delete",
                        variant="stop"
                    )
                    status_message = gr.Markdown()

        return {
            "student_table": student_table,

            "student_state": student_state,

            "add_button": add_button,
            "save_button": save_button,
            "delete_button": delete_button,

            "student_id_box" : student_id_box,
            "student_first_name_box": student_first_name_box,
            "student_last_name_box": student_last_name_box,
            "student_email_box": student_email_box,
            "student_courses_box": student_courses_box,
            "student_average_box": student_average_box,

            "status_message": status_message,
        }
    


# =============================================
# Helper
# =============================================

def load_student_table(store):
    """
    Load students from store and prepare dataframe data.
    """

    students = store.get_all_students()

    rows = [
            [
                student.student_id,
                f"{student.first_name} {student.last_name}"
            ]
            for student in students
        ]
    return rows


def refresh_student_table(store):
    """Reload students for dataframe."""
    return load_student_table(store)


def clear_student_details():
    """
    Clear student detail view after delete.
    """
    return (
        "",
        "",
        "",
        "",
        "",
        "",
        {},
        gr.update(interactive=False),
    )



# =============================================
# Events
# =============================================

def select_student_from_table(table, evt, store):

    row = evt.index[0]

    student_id = table.iloc[row, 0]

    student = store.get_student(student_id)

    courses = store.get_student_courses(student_id)
    average = store.get_student_average(student_id)

    course_text = "\n".join(
        course["name"]
        for course in courses
    )

    student_state = {
        "student_id": student.student_id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "email": student.email,
    }
    #print(student_state)
    return (
        student_state ["student_id"],
        student_state ["first_name"],
        student_state ["last_name"],
        student_state ["email"],
        course_text,
        average,
        student_state ,
    )




def update_student(student_id, first_name, last_name,email, store):
    """
    Save changed student data.
    """

    try:
        student = Student(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        store.update_student(student)

        return (
            gr.Info("Student updated successfully"),
            refresh_student_table(store),
            gr.update(interactive=False),
             {
                "student_id": student.student_id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
            },
        )

    except Exception as e:
        return (
            gr.Error("Student could not be updated"),
            refresh_student_table(store),
            gr.update(interactive=True),
        )


def delete_student(student_state, store):

    if not student_state:
        gr.Warning("Please select a student first")

        return (
            "",
            refresh_student_table(store),
            {}
        )

    try:
        student_id = student_state["student_id"]
        store.delete_student(student_id)
        gr.Info("Student deleted successfully")

        return (
            refresh_student_table(store), 
            *clear_student_details(),
        )

    except Exception as e:
        gr.Error(f"Delete failed: {e}")
        return (
            "",
            refresh_student_table(store), 
            *clear_student_details(),
        )
    



