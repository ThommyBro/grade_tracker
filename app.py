import sqlite3
import gradio as gr
from functools import partial


from grade_management.gradebook import GradeBook

from grade_db.student_repository import StudentRepository
from grade_db.course_repository import CourseRepository
from grade_db.grade_repository import GradeRepository

from grade_management.student import Student
from grade_management.course import Course
from grade_management.grade import Grade

from grade_store.sqlite_store import SqliteGradeStore

from sample_data import create_test_data, populate_database



# =======================================================
# Functions for creating the complete setup
# and sample data
# =======================================================


def create_sqlite_store():

    # Use database
    con = sqlite3.connect(
                            "grade.db", 
                            check_same_thread=False   # For single user ok
                          )
    con.execute("PRAGMA foreign_keys = ON")

    # Create all repos
    student_repo = StudentRepository(con)
    course_repo = CourseRepository(con)
    grade_repo = GradeRepository(con)

    # Create all tables
    student_repo.create_table()
    course_repo.create_table()
    grade_repo.create_table()

    store = SqliteGradeStore(student_repo, course_repo, grade_repo)

    return store, student_repo, course_repo, grade_repo



def initialize_database(student_repo: StudentRepository, course_repo: CourseRepository, grade_repo: GradeRepository):

    if len(student_repo.get_all()) == 0:
        print("Empty database, loading sample data...")

        data = create_test_data()
        populate_database(student_repo, course_repo, grade_repo, data)

    else:
        print("Database already contains data.")



def load_gradebook(store):

    gradebook = GradeBook()

    students = {}

    for student in store.get_all_students():
        gradebook.add_student(student)
        students[student.student_id] = student


    courses = {}

    for course in store.get_all_courses():
        gradebook.add_course(course)
        courses[course.course_id] = course


    for grade in store.get_all_grades():

        grade.student = students[grade.student.student_id]
        grade.course = courses[grade.course.course_id]

        gradebook.grades.append(grade)


    return gradebook

# ======================================
# Gradio Functions
# ======================================

def build_header():
    with gr.Group():
            with gr.Row(equal_height=True):

                # Logo 
                with gr.Column(scale=0, min_width=100):
                    gr.Image(
                        "images/logo.png",
                        container=False,
                        width=65,
                        height=65,
                        interactive=False,
                        buttons=[],
                        show_label=False
                    )

                # Title
                with gr.Column(scale=4):
                    gr.Markdown(
                        """
                        <div style="padding-top: 3px;">
                            <h1 style="margin-bottom: 0;">
                                Grade Tracker
                            </h1>
                            <p style="margin-top: 0; color: gray;">
                                Academic Management Dashboard
                            </p>
                        </div>
                        """
                    )

                # Version Display
                with gr.Column(scale=1, min_width=150):
                    gr.Markdown(
                        """
                        <div style="text-align:right">
                        v0.785
                        </div>
                        """
                    )


def build_student_tab():
    with gr.Tab("Students"):

        gr.Markdown(
            """
            ## Student Management

            Add, view and manage students.
            """
        )

        with gr.Row():
            # Add student form
            with gr.Column(scale=1):
                gr.Markdown("### Add Student")

                student_id = gr.Textbox(
                    label = "Student ID",
                    placeholder = "Enter a Student ID (e.g. 31415)"
                )

                first_name = gr.Textbox(
                    label="First Name",
                    placeholder="Enter first name"
                )

                last_name = gr.Textbox(
                    label="Last Name",
                    placeholder="Enter last name"
                )

                email = gr.Textbox(
                    label="Email",
                    placeholder="student@example.com"
                )

                # --- Add Student Button --- #
                add_button = gr.Button(
                    "Add Student",
                    variant = "primary",
                    interactive = False
                )

                status_message = gr. Markdown(label= "Status")

            # Student overview
            with gr.Column(scale=2):

                gr.Markdown("### Student Overview")
                student_table = gr.Dataframe(
                    headers=[
                        "ID",
                        "First Name",
                        "Last Name",
                        "Email"
                    ],
                    datatype=["str", "str", "str", "str"],
                    interactive=False,
                    wrap=True
                )

        # return dict for better handling later on
        return {
            "student_id": student_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "add_button": add_button,
            "status_message": status_message,
            "student_table": student_table
        }



# --- Student Helper Functions --- # 


def refresh_student_table(store):
    """
    Load all students from the store (in-memory or SQL) and
    prepare data for Gradio dataframe.
    """

    students = store.get_all_students()

    student_data = []

    for student in students:
        student_data.append(
            [
                student.student_id,
                student.first_name,
                student.last_name,
                student.email
            ]
        )

    return student_data


def student_form_response(student_id, first_name, last_name, email, message, store):
    """
    Return all UI updates for the student form.
    """
    return (
        student_id,
        first_name,
        last_name,
        email,
        message,
        refresh_student_table(store),
    )


def validate_student_input(student_id, first_name, last_name, email):
    """
    Enable 'Add Student' - button only if all required fields are filled.
    """
    is_valid = all( # all == UND
        [
            student_id.strip(),
            first_name.strip(),
            last_name.strip(),
            email.strip(),
        ]
    )
    return gr.update(interactive=is_valid)


def add_student(student_id, first_name, last_name, email, store):
    """
    Add new student and return updated UI values for student table.
    """
    SUCCESS_MESSAGE = "✅ Student added successfully"


    if not student_id.strip():
        return student_form_response(
            student_id,
            first_name,
            last_name,
            email,
            "⚠ Student ID is required.",
            store,
        )
    #...
    try:
        student = Student(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        store.add_student(student)

        return student_form_response(
            "",
            "",
            "",
            "",
            SUCCESS_MESSAGE,
            store,
        )

    except Exception as e:
        return student_form_response(
            student_id,
            first_name,
            last_name,
            email,
            f"❌ {e}",
            store,
        )



def show_summary(gradebook: GradeBook):
    return (
        f"Students: {len(gradebook.students)}\n"
        f"Courses: {len(gradebook.courses)}\n"
        f"Grades: {len(gradebook.grades)}"
    )


def get_dashboard_stats(gradebook: GradeBook):
    return (
        f"### 👨‍🎓 Students\n{len(gradebook.students)}",
        f"### 📚 Courses\n{len(gradebook.courses)}",
        f"### 📝 Grades\n{len(gradebook.grades)}",
    )



# =======================================================
# main- Function
#  -- Gradio Stuff is in here
# =======================================================

def main():
    # Initializing stuff
    store, student_repo, course_repo, grade_repo = create_sqlite_store()
    initialize_database(student_repo, course_repo, grade_repo)

    gradebook = load_gradebook(store)

    

    # Settings for Gradio
    # Some Theme tests, use it in next block
    theme = gr.themes.Ocean()
    
    

# =======================================================

    # Gradio 
    with gr.Blocks(theme = theme, title= "Grade Tracker") as app:
        
        # Show Header
        build_header()
        

        # --- Tabs for better clicking experience
        with gr.Tabs():
            
            # All Students
            student_ui = build_student_tab()

            student_ui["add_button"].click(
                                        fn=partial(add_student, store=store),
                                        inputs=[
                                            student_ui["student_id"],
                                            student_ui["first_name"],
                                            student_ui["last_name"],
                                            student_ui["email"]
                                        ],
                                        outputs=[
                                            student_ui["student_id"],
                                            student_ui["first_name"],
                                            student_ui["last_name"],
                                            student_ui["email"],
                                            student_ui["status_message"],
                                            student_ui["student_table"]
                                        ]
                                    )

            # Check fields for new Stundent in the UI
            # if everything is filled 'Add' Button gets active
            for component in [
                            student_ui["student_id"],
                            student_ui["first_name"],
                            student_ui["last_name"],
                            student_ui["email"],
                        ]:
                            component.change(
                                fn=validate_student_input,
                                inputs=[
                                    student_ui["student_id"],
                                    student_ui["first_name"],
                                    student_ui["last_name"],
                                    student_ui["email"],
                                ],
                                outputs=student_ui["add_button"],
                            )


            app.load(
                    fn=partial(refresh_student_table, store),
                    inputs= None,
                    outputs= student_ui["student_table"]
            )

            # All Courses
            with gr.Tab("📚 Courses"):
                gr.Markdown("## Course Management")
                with gr.Group():
                    gr.Markdown("### Add new Courses ")
                    #
                    #
                with gr.Group():
                    gr.Markdown("### Listed Courses")
                    #

            # All Grades
            with gr.Tab("📝 Grades"):
                gr.Markdown("## Grade Management")
                with gr.Group():
                    gr.Markdown("### Add Grades")
                    #
                    #

                with gr.Group():
                    gr.Markdown("### Listed Grades")
                    #

            # All Statistics        
            with gr.Tab("📊 Statistics"):
                ...


        # --- Buttons
        refresh = gr.Button("🔄 Load Dashboard")

        refresh.click(
                        fn = lambda: get_dashboard_stats(gradebook),
                        #outputs=[students_card, courses_card, grades_card]
                    )
        

        with gr.Accordion("Import / Export", open=False):
            upload = gr.File()
            export = gr.Button("Export")


    # start Gradio App
    app.launch(inbrowser=True)



if __name__ == "__main__":
    main()