import gradio as gr
from grade_management.course import Course


# ============================================================
# Table handling
# ============================================================

def load_course_table(store):
    """
    Load courses from store and prepare dataframe rows.
    """
    courses = store.get_all_courses()

    rows = [
        [
            course.course_id,
            course.name
        ]
        for course in courses
    ]
    return rows



def refresh_course_table(store):
    """Reload course table."""
    return load_course_table(store)


# ============================================================
# Views
# ============================================================

def empty_course_view():
    """
    Empty course detail card.
    """
    return {
        "title": "### Course Details",

        "course_id": "",
        "name": "",
        "max_grade": "",
        "passing_grade": "",

        "course_state": {},
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



def create_course_view():
    """
    View for creating a new Course.
    """
    return {
        "title": "### New Course",

        "course_id": "",
        "name": "",
        "max_grade": 100,
        "passing_grade": 50,

        "course_state": {},
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


def populate_course_view(course):
    """
    Populate detail card with selected course Details
    """
    return {
        "title": "### Course Details",

        "course_id": course.course_id,
        "name": course.name,
        "max_grade": course.max_grade,
        "passing_grade": course.passing_grade,

        "course_state": {
            "course_id": course.course_id,
            "name": course.name,
            "max_grade": course.max_grade,
            "passing_grade": course.passing_grade,
        },

        "mode_state": "edit",

        "save_button": gr.update(
            value="💾 Save Changes",
            interactive=False
        ),

        "delete_button": gr.update(
            visible=True
        ),

        "cancel_button": gr.update(
            visible=True
        ),
    }


def course_view_to_output(view):
    """
    Convert view dictionary into Gradio output tuple.
    Order must match event outputs.
    """
    return (
        view["title"],
        view["course_id"],
        view["name"],
        view["max_grade"],
        view["passing_grade"],

        view["course_state"],
        view["mode_state"],

        view["save_button"],
        view["delete_button"],
        view["cancel_button"],
    )

def render_course_details(mode, course=None, store=None,):
    """
    Build course view depending on view mode.
    """
    if mode == "empty":
        view = empty_course_view()
    elif mode == "create":
        view = create_course_view()
    elif mode == "edit":
        if course is None:
            view = empty_course_view()
        else:
            view = populate_course_view(course)
    else:
        view = empty_course_view()

    return course_view_to_output(view)


# ============================================================
# Change detection
# ============================================================

def check_course_changes(
    mode_state,
    original_course,
    name,
    max_grade,
    passing_grade,
):
    """
    Enable save button only when data changed.
    """

    # empty state
    if mode_state == "empty":

        return gr.update(
            interactive=False
        )


    # create mode
    if mode_state == "create":

        changed = any(
            [
                name.strip(),
                max_grade,
                passing_grade
            ]
        )

        return gr.update(
            interactive=changed
        )


    # edit mode
    if mode_state == "edit":

        if not original_course:

            return gr.update(
                interactive=False
            )


        changed = (

            name != original_course["name"]

            or

            max_grade != original_course["max_grade"]

            or

            passing_grade != original_course["passing_grade"]

        )


        return gr.update(
            interactive=changed
        )


    return gr.update(
        interactive=False
    )



# ============================================================
# CRUD actions
# ============================================================

def save_course(
    mode_state,
    course_state,
    course_id,
    name,
    max_grade,
    passing_grade,
    store,
):
    """
    Decide between create and update.
    """

    if mode_state == "create":

        return create_course(
            course_id,
            name,
            max_grade,
            passing_grade,
            store,
        )


    elif mode_state == "edit":

        return update_course(
            course_state,
            name,
            max_grade,
            passing_grade,
            store,
        )


    else:

        gr.Warning(
            "No action available"
        )

        return (
            refresh_course_table(store),
            *render_course_details(
                "empty",
                None,
                store
            )
        )



def create_course(
    course_id,
    name,
    max_grade,
    passing_grade,
    store,
):
    """
    Create a new course.
    """
    try:
        course = Course(
            course_id=course_id,
            name=name,
            max_grade=max_grade,
            passing_grade=passing_grade,
        )
        store.add_course(course)
        gr.Info(
            "Course created successfully"
        )
        return (
            refresh_course_table(store),
            *render_course_details(
                "edit",
                course,
                store
            )
        )
    except Exception as e:
        gr.Warning(
            f"Course could not be created: {e}"
        )
        return (
            refresh_course_table(store),
            *render_course_details(
                "create",
                None,
                store
            )
        )



def update_course(course_state, name, max_grade, passing_grade, store,):
    """
    Update existing course.
    """
    try:
        course = Course(
            course_id=course_state["course_id"],
            name=name,
            max_grade=max_grade,
            passing_grade=passing_grade,
        )
        store.update_course(course)
        gr.Info(
            "Course updated successfully"
        )
        return (
            refresh_course_table(store),
            *render_course_details(
                "edit",
                course,
                store
            )
        )
    except Exception as e:
        gr.Warning(
            f"Course could not be updated: {e}"
        )
        old_course = Course(
            course_id=course_state["course_id"],
            name=course_state["name"],
            max_grade=course_state["max_grade"],
            passing_grade=course_state["passing_grade"],
        )
        return (
            refresh_course_table(store),
            *render_course_details(
                "edit",
                old_course,
                store
            )

        )



def delete_course(course_state, store,):
    """
    Delete selected course.
    """
    if not course_state:
        gr.Warning(
            "Please select a course first"
        )
        return (
            refresh_course_table(store),
            *render_course_details(
                "empty",
                None,
                store
            )
        )
    try:
        course_id = course_state["course_id"]
        store.delete_course(
            course_id
        )
        gr.Info(
            "Course deleted successfully"
        )
        return (
            refresh_course_table(store),
            *render_course_details(
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
            refresh_course_table(store),
            *render_course_details(
                "empty",
                None,
                store
            )
        )
    


# ============================================================
# Build Tab
# ============================================================

def build_course_tab(store):
    
    # state definition
    course_state = gr.State(value=[])
    mode_state = gr.State(value="empty")
    


    with gr.Tab("Courses"):
        # Header row
        with gr.Row():
            with gr.Column(scale = 5):
                gr.Markdown(
                    """
                    ## Courses
    
                    """
                )
            with gr.Column(scale= 1, min_width=120):
                add_button = gr.Button(
                    "➕ Add Course",
                    variant="primary"
                )

        # Main content
        with gr.Row():

            # Left hand side - student list
            with gr.Column(scale=1):
                gr.Markdown("### Course List"),
                course_table = gr.Dataframe(
                    headers=[
                        "ID",
                        "Course"
                    ],
                    
                    value=load_course_table(store),
                    datatype=["str", "str",],
                    interactive=True,
                    wrap=True,
                    show_row_numbers=False,
                    #select_mode="row"
                )


            # Right hand side - Course details
            with gr.Column(scale=1):
                course_title = gr.Markdown(
                    "### Course Details"
                )
                course_id_box = gr.Textbox(
                    label="Course ID",
                    interactive=False,
                )
                course_name_box = gr.Textbox(
                    label="Name",
                    interactive=False
                )
                course_max_grade_box = gr.Textbox(
                    label="Max grade",
                    interactive=False
                )
                course_passing_grade_box = gr.Textbox(
                    label="Passing grade",
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
            "course_title": course_title,
            "course_table": course_table,

            "course_state": course_state,
            "mode_state": mode_state,

            "add_button": add_button,
            "save_button": save_button,
            "delete_button": delete_button,
            "cancel_button": cancel_button,

            "course_id_box" : course_id_box,
            "course_name_box": course_name_box,
            "course_max_grade_box": course_max_grade_box,
            "course_passing_grade_box": course_passing_grade_box,

            "status_message": status_message,
        }