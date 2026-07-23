import gradio as gr
from grade_management.student import Student



# =============================================
# UI
# =============================================


def build_student_tab(store):
    
    # state definition
    student_state = gr.State(value=[])
    mode_state = gr.State(value="empty")
    


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
                gr.Markdown("### Student List"),
                student_table = gr.Dataframe(
                    headers=[
                        "ID",
                        "Student"
                    ],
                    
                    value=load_student_table(store),
                    datatype=["str", "str",],
                    interactive=True,
                    wrap=True,
                    show_row_numbers=False,
                    #select_mode="row"
                )


            # Right hand side - Student details
            with gr.Column(scale=1):
                student_title = gr.Markdown(
                    "### Student Details"
                )
                student_id_box = gr.Textbox(
                    label="Student ID",
                    interactive=False,
                )
                student_first_name_box = gr.Textbox(
                    label="First Name",
                    interactive=False
                )
                student_last_name_box = gr.Textbox(
                    label="Last Name",
                    interactive=False
                )
                student_email_box = gr.Textbox(
                    label="Email",
                    interactive=False
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
            "student_title": student_title,
            "student_table": student_table,

            "student_state": student_state,
            "mode_state": mode_state,

            "add_button": add_button,
            "save_button": save_button,
            "delete_button": delete_button,
            "cancel_button": cancel_button,

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


def empty_student_view():
    return {
        "title": "### Student Details",
        "student_id": "",
        "first_name": "",
        "last_name": "",
        "email": "",
        "courses": "",
        "average": "",
        "student_state": {},
        "mode_state": "empty",
        "save_button": gr.update(
            value="💾 Save Changes",
            interactive=False
        ),
        "delete_button": gr.update(
            value="🗑 Delete",
            visible=False
        ),
        "cancel_button": gr.update(
            visible=False
        ),
    }


def create_student_view():
    return {
        "title": "### New Student",
        "student_id": gr.update(
            value="",
            interactive=True
        ),

        "first_name": gr.update(
            value="",
            interactive=True
        ),
        "last_name": gr.update(
            value="",
            interactive=True
        ),
        "email": gr.update(
            value="",
            interactive=True
        ),
        "courses": "",
        "average": "",
        "student_state": {},
        "mode_state": "create",
        "save_button": gr.update(
            value="➕ Create Student",
            interactive=False
        ),
        "delete_button": gr.update(
            visible=False
        ),
        "cancel_button": gr.update(
            visible=True
        ),
    }


def view_to_output(view):
    """
    Convert student view dictionary into Gradio output tuple.
    Order must match event outputs!
    """
    return (
        view["title"],                  # 1
        view["student_id"],             # 2
        view["first_name"],             # 3
        view["last_name"],              # 4
        view["email"],                  # 5
        view["courses"],                # 6
        view["average"],                # 7
        view["student_state"],          # 8
        view["mode_state"],             # 9
        view["save_button"],            # 10
        view["delete_button"],          # 11
        view["cancel_button"],          # 12
    )


def render_student_details(
    mode,
    student=None,
    store=None,
):
    """
    Build student detail view depending on current mode.
    """

    if mode == "empty":
        view = empty_student_view()

    elif mode == "create":
        view = create_student_view()

    elif mode == "edit":
        # Safety fallback:
        # No student selected -> show empty state
        if student is None:
            view = empty_student_view()

        else:
           view = populate_student_view(student, store)
    else:
        # Unknown mode -> safe fallback
        view = empty_student_view()
    
    return view_to_output(view)



def build_student_state(student):
    return {
        "student_id": student.student_id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "email": student.email,
    }

def format_courses(courses):
    return "\n".join(
        course["name"]
        for course in courses
    )

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


def check_student_changes(
    mode_state,
    original_student,
    first_name,
    last_name,
    email,
):
    """
    Enable save/create button only if data changed.
    """
    print(
        "CHECK CHANGES:",
        mode_state,
        first_name,
        last_name,
        email
    )

    # Empty view
    if mode_state == "empty":
        return gr.update(interactive=False)
    
    # Create mode
    if mode_state == "create":
        changed = any([
            first_name.strip(),
            last_name.strip(),
            email.strip()
        ])
        return gr.update(interactive=changed)

    # Edit mode
    if mode_state == "edit":
        if not original_student:
            return gr.update(interactive=False)

        changed = (
            first_name != original_student["first_name"]
            or
            last_name != original_student["last_name"]
            or
            email != original_student["email"]
        )
        return gr.update(interactive=changed)
    # Empty state
    return gr.update(interactive=False)



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

def select_student_from_table(table, evt: gr.SelectData, store):
    # print("TABLE:")
    # print(table)

    # print("EVENT:")
    # print(evt)

    # print("EVENT INDEX:")
    # print(evt.index)
    if evt is None:
        return render_student_details(
            mode="empty",
            student=None,
            store=store,
        )
    
    row = evt.index[0]

    student_id = table.iloc[row]["ID"]

    student = store.get_student(student_id)

    return render_student_details(
        mode="edit",
        student=student,
        store=store
    )


        
def create_student(
    student_id,
    first_name,
    last_name,
    email,
    store,
):
    """
    Create a new student and switch to edit mode afterwards.
    """
    print("CREATE STUDENT DEBUG")
    print(student_id, first_name, last_name, email)
    try:
        student = Student(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        store.add_student(student)
        print("AFTER ADD:")
        print(store.get_all_students())
        gr.Info(
            "Student created successfully"
        )

        return (
            refresh_student_table(store),
            *render_student_details(
                "edit",
                student,
                store
            )
        )
    except Exception as e:
        gr.Warning(
            f"Student could not be created: {e}"
        )
        # wieder Create View anzeigen
        return (
            refresh_student_table(store),
            *render_student_details(
                "create",
                None,
                store
            )
        )






def save_student(
    mode_state,
    student_state,
    student_id,
    first_name,
    last_name,
    email,
    store,
):
    """
    Decide whether to create or update a student.
    """
    print("SAVE DEBUG")
    print("MODE:", mode_state)
    print("STATE:", student_state)
    print("ID:", student_id)
    print("NAME:", first_name, last_name)
    if mode_state == "create":
        return create_student(
            student_id,
            first_name,
            last_name,
            email,
            store,
        )

    elif mode_state == "edit":
        return update_student(
            student_state,
            first_name,
            last_name,
            email,
            store,
        )

    else:
        gr.Warning("No action available")

        return (
            refresh_student_table(store),
            *render_student_details(
                "empty",
                None,
                store
            )
        )



def update_student(
    student_state,
    first_name,
    last_name,
    email,
    store,
):
    """
    Update an existing student.
    """
    # print("UPDATE DEBUG")
    # print(student_state)
    # print(first_name, last_name, email)
    try:

        student = Student(
            student_id=student_state["student_id"],
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        store.update_student(student)
        gr.Info("Student updated successfully")

        return (
                refresh_student_table(store),
                *render_student_details("edit", student, store,)
            )

    except Exception as e:

        gr.Warning(
                    f"Student could not be updated: {e}"
                )

        # show old data
        old_student = Student(
            student_id=student_state["student_id"],
            first_name=student_state["first_name"],
            last_name=student_state["last_name"],
            email=student_state["email"],
        )

        return (
                refresh_student_table(store),
                *render_student_details("edit", old_student, store, )
            )


def delete_student(student_state, store):
    """
    Delete selected student and reset the detail view.
    """
    if not student_state:
        gr.Warning(
            "Please select a student first"
        )
        return (
            refresh_student_table(store),
            *render_student_details(
                "empty",
                None,
                store
            )
        )
    try:
        student_id = student_state["student_id"]
        store.delete_student(student_id)
        gr.Info(
            "Student deleted successfully"
        )

        return (
            refresh_student_table(store),
            *render_student_details(
                "empty",
                None,
                store
            )
        )

    except Exception as e:
        gr.Warning(
            f"Delete failed: {e}"
        )
        return (
            refresh_student_table(store),
            *render_student_details(
                "edit",
                Student(
                    student_id=student_state["student_id"],
                    first_name=student_state["first_name"],
                    last_name=student_state["last_name"],
                    email=student_state["email"],
                ),
                store
            )
        )
    



def populate_student_view(student: Student, store):
    """
    Build the complete student detail view for an existing student.

    This function is the single source of truth for displaying a student
    inside the detail card.

    It is used after:
        - selecting a student from the table
        - creating a student
        - updating a student
        - reloading a student from the database

    Parameters
    ----------
    student:
        Student object that should be displayed.

    store:
        GradeStore implementation used to load additional information
        (courses and average grade).

    Returns
    -------
    dict
        View dictionary that is later converted into Gradio outputs by
        view_to_output().
    """

    # ------------------------------------------------------------------
    # Load additional information
    # ------------------------------------------------------------------

    courses = store.get_student_courses(student.student_id)

    average = store.get_student_average(student.student_id)

    # ------------------------------------------------------------------
    # Format course list for textbox
    # ------------------------------------------------------------------

    if courses:
        course_text = "\n".join(
            course["name"]
            for course in courses
        )
    else:
        course_text = ""

    # ------------------------------------------------------------------
    # Store original values.
    #
    # These values are later used by check_student_changes()
    # to determine whether the Save button should become active.
    # ------------------------------------------------------------------

    student_state = {
        "student_id": student.student_id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "email": student.email,
    }

    # ------------------------------------------------------------------
    # Return complete view definition
    # ------------------------------------------------------------------

    return {

        # --------------------------------------------------------------
        # Header
        # --------------------------------------------------------------

        "title": "### Student Details",

        # --------------------------------------------------------------
        # Student information
        # --------------------------------------------------------------


        # original - no editing possible
        # "student_id": student.student_id,
        # "first_name": student.first_name,
        # "last_name": student.last_name,
        # "email": student.email,

        # v1 for editing
        "student_id": gr.update(
            value=student.student_id,
            interactive=False
        ),

        "first_name": gr.update(
            value=student.first_name,
            interactive=True
        ),

        "last_name": gr.update(
            value=student.last_name,
            interactive=True
        ),

        "email": gr.update(
            value=student.email,
            interactive=True
        ),

        # --------------------------------------------------------------
        # Read-only statistics
        # --------------------------------------------------------------

        "courses": course_text,
        "average": average,

        # --------------------------------------------------------------
        # UI state
        # --------------------------------------------------------------

        "student_state": student_state,
        "mode_state": "edit",

        # --------------------------------------------------------------
        # Buttons
        # --------------------------------------------------------------

        "save_button": gr.update(
            value="💾 Save Changes",
            interactive=False,
        ),

        "delete_button": gr.update(
            value="🗑 Delete",
            visible=True,
        ),

        "cancel_button": gr.update(
            value="❌ Cancel",
            visible=True,
        ),
    }