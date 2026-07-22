import sqlite3
import gradio as gr
from functools import partial


from grade_management.gradebook import GradeBook

from grade_db.student_repository import StudentRepository
from grade_db.course_repository import CourseRepository
from grade_db.grade_repository import GradeRepository
from grade_db.statistics_repository import StatisticsRepository

from grade_management.student import Student
from grade_management.course import Course
from grade_management.grade import Grade

from ui.header import build_header
from ui.courses import build_course_tab
from ui.students import *
from ui.grades import build_grade_tab
from ui.dashboard import build_dashboard_tab
from ui.statistics import build_statistics_tab

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
    stats_repo = StatisticsRepository(con)

    # Create all tables
    student_repo.create_table()
    course_repo.create_table()
    grade_repo.create_table()

    store = SqliteGradeStore(student_repo, course_repo, grade_repo, stats_repo)

    return store, student_repo, course_repo, grade_repo, stats_repo



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







# =======================================================
#               MAIN()- Function
#  -- Gradio Stuff is in here
# =======================================================

def main():
    # Initializing stuff
    store, student_repo, course_repo, grade_repo, stats_repo = create_sqlite_store()
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
            build_dahsboard_ui = build_dashboard_tab()
            student_ui = build_student_tab(store)
            build_course_ui = build_course_tab()
            build_grade_ui = build_grade_tab()
            build_statistics_ui = build_statistics_tab()


        # Events

        def on_student_select(table, evt: gr.SelectData):
            """Fill details card with student informations."""
            return select_student_from_table(
                table,
                evt,
                store
            )
        

        def check_student_changes(original_student, first_name, last_name, email,):
            """
            Enable save button only if data changed.
            """
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


        def enable_save_button():
            """Enable 'Save' whenever student details are changed."""
            return gr.update(
                interactive=True
            )
        student_ui["student_table"].select(
            fn=on_student_select,
            inputs=[student_ui["student_table"]],
            outputs=[
                student_ui["student_id_box"],
                student_ui["student_first_name_box"],
                student_ui["student_last_name_box"],
                student_ui["student_email_box"],
                student_ui["student_courses_box"],
                student_ui["student_average_box"],
                student_ui["student_state"]
            ]
        )

        # emailaddress is changed
        student_ui["student_email_box"].change(
            fn=enable_save_button,
            outputs=student_ui["save_button"]
        )
        # first name is changed
        student_ui["student_first_name_box"].change(
            fn=enable_save_button,
            outputs=student_ui["save_button"]
        )
        # last name is changed
        student_ui["student_last_name_box"].change(
            fn=enable_save_button,
            outputs=student_ui["save_button"]
        )

        student_ui["save_button"].click(
            fn=partial(
                update_student,
                store=store
            ),
            inputs=[
                student_ui["student_id_box"],
                student_ui["student_first_name_box"],
                student_ui["student_last_name_box"],
                student_ui["student_email_box"],
            ],
            outputs=[
                student_ui["status_message"],
                student_ui["student_table"],
                student_ui["save_button"],
            ]
        )


        # --- Check Changes for Save button
        student_ui["student_email_box"].change(
            fn=check_student_changes,
            inputs=[
                student_ui["student_state"],
                student_ui["student_first_name_box"],
                student_ui["student_last_name_box"],
                student_ui["student_email_box"],
            ],
            outputs=[
                student_ui["save_button"]
            ]
        )

        student_ui["student_first_name_box"].change(
            fn=check_student_changes,
            inputs=[
                student_ui["student_state"],
                student_ui["student_first_name_box"],
                student_ui["student_last_name_box"],
                student_ui["student_email_box"],
            ],
            outputs=[
                student_ui["save_button"]
            ]
        )

        student_ui["student_last_name_box"].change(
            fn=check_student_changes,
            inputs=[
                student_ui["student_state"],
                student_ui["student_first_name_box"],
                student_ui["student_last_name_box"],
                student_ui["student_email_box"],
            ],
            outputs=[
                student_ui["save_button"]
            ]
        )



    # start Gradio App
    app.launch(inbrowser=True)

if __name__ == "__main__":
    main()