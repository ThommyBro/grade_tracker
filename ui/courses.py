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


def select_course_from_table( table, evt: gr.SelectData, store,):
    row = evt.index[0]
    course_id = table.iloc[row]["ID"]
    course = store.get_course(course_id)

    return render_course_details(
        "edit",
        course,
        store,
    )


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
        "course_name": "",
        "course_max_grade": "",
        "course_passing_grade": "",

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

        "course_id": gr.update(
            value = "",
            interactive=True
        ),
        "course_name": gr.update(
            value="",
            interactive=True
        ),
        "course_max_grade": gr.update(
            value=100,
            interactive=True
        ),
        "course_passing_grade": gr.update(
            value = 50,
            interactive = True
        ),

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

# first draft
# def populate_course_view(course):
#     """
#     Populate detail card with selected course Details
#     """
#     return {
#         "title": "### Course Details",

#         "course_id": course.course_id,
#         "course_name": course.name,
#         "course_max_grade": course.max_grade,
#         "course_passing_grade": course.passing_grade,

#         "course_state": {
#             "course_id": course.course_id,
#             "course_name": course.name,
#             "course_max_grade": course.max_grade,
#             "course_passing_grade": course.passing_grade,
#         },

#         "mode_state": "edit",

#         "save_button": gr.update(
#             value="💾 Save Changes",
#             interactive=False
#         ),

#         "delete_button": gr.update(
#             visible=True
#         ),

#         "cancel_button": gr.update(
#             visible=True
#         ),
#     }


def course_view_to_output(view):
    """
    Convert view dictionary into Gradio output tuple.
    Order must match event outputs.
    """
    return (
        view["title"],
        view["course_id"],
        view["course_name"],
        view["course_max_grade"],
        view["course_passing_grade"],

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
            view = populate_course_view(course, store)
    else:
        view = empty_course_view()

    return course_view_to_output(view)


# ============================================================
# Change detection
# ============================================================

def check_course_changes(
    mode_state,
    original_course,
    course_name,
    course_max_grade,
    course_passing_grade,
):
    """
    Enable save button only when data changed.
    """

    print("CHECK COURSE")
    print(mode_state)
    print(original_course)
    print(course_name)
    print(course_max_grade)
    print(course_passing_grade)
    # empty state
    if mode_state == "empty":
        print("Mode: Empty")
        return gr.update(
            interactive=False
        )
    # create mode
    if mode_state == "create":
    #     print("Mode: Create")
    #     changed = any(
    #         [
    #             course_name.strip(),
    #             course_max_grade,
    #             course_passing_grade
    #         ]
    #     )

        return gr.update(
            interactive=True
        )

    # edit mode
    if mode_state == "edit":
        print("Mode: Edit")
        if not original_course:
            print("Mode: Edit but original")
            return gr.update(
                interactive=False
            )
        print("COMPARE:")
        print(course_name, original_course["course_name"])
        print(course_max_grade, original_course["course_max_grade"])
        print(course_passing_grade, original_course["course_passing_grade"])
        changed = (
            course_name != original_course["course_name"]
            or
            course_max_grade != original_course["course_max_grade"]
            or
            course_passing_grade != original_course["course_passing_grade"]

        )
        print("CHANGED:", changed)
        return gr.update(interactive=changed)
    print("No changes")
    return gr.update(interactive=False)



# ============================================================
# CRUD actions
# ============================================================

def save_course(
    mode_state,
    course_state,
    course_id,
    course_name,
    course_max_grade,
    course_passing_grade,
    store,
):
    """
    Decide between create and update.
    """
    if mode_state == "create":
        return create_course(
                    course_id,
                    course_name,
                    course_max_grade,
                    course_passing_grade,
                    store,
                )
            
    elif mode_state == "edit":
        return update_course(
            course_state,
            course_name,
            course_max_grade,
            course_passing_grade,
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
    course_name,
    course_max_grade,
    course_passing_grade,
    store,
):
    """
    Create a new course.
    """
    try:
        course = Course(
            course_id=course_id,
            name=str(course_name),
            max_grade=float(course_max_grade),
            passing_grade=float(course_passing_grade),
        )
        store.add_course(course)
       
        table = refresh_course_table(store)

        result = render_course_details("edit", course, store)

        print(f"DETAIL OUTPUT LENGTH: {len(result)}")
        print("RETURN TABLE")
        print(table)

        gr.Info(
            "Course created successfully"
        )
        return (
                table,
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
            name=str(name),
            max_grade=float(max_grade),
            passing_grade=float(passing_grade),
        )
        store.update_course(course)
        gr.Info(
            "Course updated successfully"
        )
        return (
            refresh_course_table(store),
            *render_course_details(
                "empty",
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
            name=course_state["course_name"],
            max_grade=course_state["course_max_grade"],
            passing_grade=course_state["course_passing_grade"],
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
    print(f"Delete Course State: {course_state}")
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
    course = Course(
                    course_id=course_state["course_id"],
                    name=course_state["course_name"],
                    max_grade=course_state["course_max_grade"],
                    passing_grade=course_state["course_passing_grade"],
                )
    try:
        # Check dependencies
        grades = store.get_course_grades(course.course_id)

        if grades:
            gr.Warning(
                "Course cannot be deleted because grades exist."
            )

            return (
                refresh_course_table(store),
                *render_course_details(
                    "edit",
                    course,
                    store
                )
            )
       
        store.delete_course(course) 
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
        gr.Warning(f"Delete failed: {e}")
        return (
            refresh_course_table(store),
            *render_course_details(
                "edit",
                course,
                store
            )
        )
    


# ============================================================
# Build Tab
# ============================================================

def build_course_tab(store):
    
    # state definition
    course_state = gr.State(value={})
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
    




def populate_course_view(course: Course, store):

    course_state = {
        "course_id": course.course_id,
        "course_name": course.name,
        "course_max_grade": course.max_grade,
        "course_passing_grade": course.passing_grade,
    }
    return {
        "title": "### Course Details",

        "course_id": gr.update(
            value=course.course_id,
            interactive=False,
        ),

        "course_name": gr.update(
            value=course.name,
            interactive=True,
        ),

        "course_max_grade": gr.update(
            value=course.max_grade,
            interactive=True,
        ),

        "course_passing_grade": gr.update(
            value=course.passing_grade,
            interactive=True,
        ),

        "course_state": course_state,
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