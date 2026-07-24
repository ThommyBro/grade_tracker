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
    grade_id = int(table.iloc[row]["ID"])
    

    grade = store.get_grade_by_id(grade_id)
    

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
        "id": grade.id,
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
# Change detection
# ============================================================
def check_grade_changes(
    mode_state,
    original_grade,
    score,
    date,
    notes,
):
    """
    Enable save button only when data changed.
    """

    # empty state
    if mode_state == "empty":
        print("Mode: Empty")
        return gr.update(
            interactive=False
        )
    # create mode
    if mode_state == "create":
        return gr.update(
            interactive=True
        )

    # edit mode
    if mode_state == "edit":
        print("Mode: Edit")
        if not original_grade:
            print("Mode: Edit but original")
            return gr.update(
                interactive=False
            )
        
        changed = (
            score!= original_grade["score"]
            or
            date != original_grade["date"]
            or
            notes != original_grade["notes"]

        )
        print("CHANGED:", changed)
        return gr.update(interactive=changed)
    print("No changes")
    return gr.update(interactive=False)


# ============================================================
# CRUD actions
# ============================================================


def create_grade(
    student_id,
    course_id,
    score,
    date,
    notes,
    store,
):
    """
    Create a new grade.
    """
    try:


        student = store.get_student(student_id)
        course = store.get_course(course_id)

        if student is None:
            gr.Warning(
            f"No Student found."
        )

        if course is None:
            gr.Warning(
            f"No Course found"
        )
        
        grade = Grade(
            student = student,
            course = course,
            score = float(score),
            date = date,
            notes = notes
        )
        store.add_grade(grade)
       
        table = refresh_grade_table(store)

        result = render_grade_details("edit", grade, store)

        gr.Info(
            "Grade created successfully"
        )
        return (
                table,
                *render_grade_details(
                        "edit",
                        grade,
                        store
                    )
                )
    except Exception as e:
        gr.Warning(
            f"Grade could not be created: {e}"
        )
        return (
            refresh_grade_table(store),
            *render_grade_details(
                "create",
                None,
                store
            )
        )




def save_grade(
    mode_state,
    grade_state,
    student_id,
    course_id,
    score,
    date,
    notes,
    store,
):
    """
    Decide between create and update.
    """

    student = store.get_student(
        grade_state["student_id"]
        )
    course = store.get_course(
        grade_state["course_id"]
    )

    if student is None:
        gr.Warning(
        f"No Student found."
    )

    if course is None:
        gr.Warning(
        f"No Course found"
    )
        
    if mode_state == "create":
        return create_grade(
                    student,
                    course,
                    score,
                    date,
                    notes,
                    store,
                )
            
    elif mode_state == "edit":
        print("UPDATE WILL BE PERFORMED")
        return update_grade(
            grade_state,
            student_id,
            course_id,
            score,
            date,
            notes,
            store,
        )

    else:
        gr.Warning(
            "No action available"
        )

        return (
            refresh_grade_table(store),
            *render_grade_details(
                "empty",
                None,
                store
            )
        )


def update_grade(grade_state, student_id, course_id, score, date, notes, store,):
    """
    Update existing grade.
    """
    try:

        student = store.get_student(
            grade_state["student_id"]
            )
        
        course = store.get_course(
            grade_state["course_id"]
            )

        if student is None:
            gr.Warning(f"Grade could not be updated. Student missing.")

        if course is None:
            gr.Warning(f"Grade could not be updated. Course missing.")

        grade = Grade(
            id=grade_state["id"],
            student=student,
            course=course,
            score=float(score),
            date=date,
            notes=notes,
        )
        print(f"NEW GRADE: {grade}")
        store.update_grade(grade)

        gr.Info("Grade updated successfully")


        return (
            refresh_grade_table(store),
            *render_grade_details(
                "empty",
                None,
                store
            )
        )

    except Exception as e:
        gr.Warning(f"Grade could not be updated: {e}")

        old_grade = store.get_grade_by_id(
            grade_state["id"]
        )

        return (
            refresh_grade_table(store),
            *render_grade_details(
                "edit",
                old_grade,
                store
            )
        )



def delete_grade(grade_state, store,):
    """
    Delete selected grade.
    """
    print(f"Delete Grade State: {grade_state}")
    if not grade_state:
        gr.Warning(
            "Please select a grade first"
        )
        return (
            refresh_grade_table(store),
            *render_grade_details(
                "empty",
                None,
                store
            )
        )
  
    try:
        # Check dependencies
        grade = store.get_grade_by_id(
                            grade_state["id"]
                            )

        store.delete_grade(grade)
        gr.Info(
            "Course deleted successfully"
        )
        return (
                refresh_grade_table(store),
                *render_grade_details(
                    "edit",
                    grade,
                    store
                )
            )
    
    except Exception as e:
        gr.Warning(f"Delete failed: {e}")
        return (
            refresh_grade_table(store),
            *render_grade_details(
                "edit",
                grade,
                store
            )
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
    