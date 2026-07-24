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
from ui.courses import *
from ui.students import *
from ui.grades import *
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
        

        # --- Tabs are build inside UI builders
       
        student_ui = build_student_tab(store)
        course_ui = build_course_tab(store)
        grade_ui = build_grade_tab(store)

         


        # --- select stuff in list part --- #

        def on_student_select(table, evt: gr.SelectData):
            """Fill details card with student informations."""
            return select_student_from_table(
                table,
                evt,
                store
            )

        def on_course_select(table, evt: gr.SelectData):
            """Fill details card with course informations."""
            return select_course_from_table(
                table,
                evt,
                store,
            )
        
        def on_grade_select(table, evt: gr.SelectData):
            """Fill details card with grade informations."""
            return select_grade_from_table(
                table,
                evt,
                store,
            )
      

        


        # maybe useless in the meantime ?
        def enable_save_button():
            """Enable 'Save' whenever student details are changed."""
            return gr.update(
                interactive=True
            )
        

#------------- View ------------------#

# ============================================================
# Students
# ============================================================

        student_ui["student_table"].select(
            fn= on_student_select,
            inputs=[
                student_ui["student_table"]
            ],
            outputs=[
                student_ui["student_title"],
                student_ui["student_id_box"],
                student_ui["student_first_name_box"],
                student_ui["student_last_name_box"],
                student_ui["student_email_box"],
                student_ui["student_courses_box"],
                student_ui["student_average_box"],
                student_ui["student_state"],
                student_ui["mode_state"],
                student_ui["save_button"],
                student_ui["delete_button"],
                student_ui["cancel_button"],
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


  # save and update student
        student_ui["save_button"].click(
            fn=partial(
                save_student,
                store=store
            ),
            inputs=[
                student_ui["mode_state"],
                student_ui["student_state"],
                student_ui["student_id_box"],
                student_ui["student_first_name_box"],
                student_ui["student_last_name_box"],
                student_ui["student_email_box"],
            ],
            outputs=[
                student_ui["student_table"],            # 1
                student_ui["student_title"],            # 2
                student_ui["student_id_box"],           # 3
                student_ui["student_first_name_box"],   # 4
                student_ui["student_last_name_box"],    # 5
                student_ui["student_email_box"],        # 6
                student_ui["student_courses_box"],      # 7
                student_ui["student_average_box"],      # 8
                student_ui["student_state"],            # 9
                student_ui["mode_state"],               # 10
                student_ui["save_button"],              # 11
                student_ui["delete_button"],            # 12
                student_ui["cancel_button"],            # 13
            ]
        )


        # --- Check Changes for Save button
        student_ui["student_email_box"].input(
            fn=check_student_changes,
            inputs=[
                student_ui["mode_state"],
                student_ui["student_state"],
                student_ui["student_first_name_box"],
                student_ui["student_last_name_box"],
                student_ui["student_email_box"],
            ],
            outputs=[
                student_ui["save_button"]
            ]
        )

        student_ui["student_first_name_box"].input(
            fn=check_student_changes,
            inputs=[student_ui["mode_state"],
                student_ui["student_state"],
                student_ui["student_first_name_box"],
                student_ui["student_last_name_box"],
                student_ui["student_email_box"],
            ],
            outputs=[
                student_ui["save_button"]
            ]
        )

        student_ui["student_last_name_box"].input(
            fn=check_student_changes,
            inputs=[
                student_ui["mode_state"],
                student_ui["student_state"],
                student_ui["student_first_name_box"],
                student_ui["student_last_name_box"],
                student_ui["student_email_box"],
            ],
            outputs=[
                student_ui["save_button"]
            ]
        )


    # delete student
        student_ui["delete_button"].click(
            fn=partial(delete_student, store=store),
            inputs=[
                student_ui["student_state"]
            ],
             outputs=[
                student_ui["student_table"],            # 1

                student_ui["student_title"],            # 2

                student_ui["student_id_box"],           # 3
                student_ui["student_first_name_box"],   # 4
                student_ui["student_last_name_box"],    # 5
                student_ui["student_email_box"],        # 6

                student_ui["student_courses_box"],      # 7
                student_ui["student_average_box"],      # 8

                student_ui["student_state"],            # 9
                student_ui["mode_state"],               # 10

                student_ui["save_button"],              # 11
                student_ui["delete_button"],            # 12
                student_ui["cancel_button"],            # 13
            ]
        )

        # add student
        student_ui["add_button"].click(
            fn=lambda: render_student_details(
                "create"
            ),
            outputs=[
                student_ui["student_title"],
                student_ui["student_id_box"],
                student_ui["student_first_name_box"],
                student_ui["student_last_name_box"],
                student_ui["student_email_box"],
                student_ui["student_courses_box"],
                student_ui["student_average_box"],
                student_ui["student_state"],
                student_ui["mode_state"],
                student_ui["save_button"],
                student_ui["delete_button"],
                student_ui["cancel_button"],
            ]
        )

        student_ui["cancel_button"].click(
            fn=lambda: render_student_details(
                "empty"
            ),
            outputs=[
                student_ui["student_title"],
                student_ui["student_id_box"],
                student_ui["student_first_name_box"],
                student_ui["student_last_name_box"],
                student_ui["student_email_box"],
                student_ui["student_courses_box"],
                student_ui["student_average_box"],
                student_ui["student_state"],
                student_ui["mode_state"],
                student_ui["save_button"],
                student_ui["delete_button"],
                student_ui["cancel_button"],
            ]
        )



# ============================================================
# Courses
# ============================================================

        course_ui["course_table"].select(
            fn=on_course_select,
            inputs=[
                course_ui["course_table"]
            ],
            outputs=[
                course_ui["course_title"],
                course_ui["course_id_box"],
                course_ui["course_name_box"],
                course_ui["course_max_grade_box"],
                course_ui["course_passing_grade_box"],
                course_ui["course_state"],
                course_ui["mode_state"],
                course_ui["save_button"],
                course_ui["delete_button"],
                course_ui["cancel_button"],
            ]
        )



    # save and update course
        course_ui["save_button"].click(
            fn=partial(
                save_course,
                store=store
            ),
            inputs=[
                course_ui["mode_state"],
                course_ui["course_state"],
                
                course_ui["course_id_box"],
                course_ui["course_name_box"],
                course_ui["course_max_grade_box"],
                course_ui["course_passing_grade_box"],
            ],
            outputs=[
                course_ui["course_table"],
                course_ui["course_title"],
                course_ui["course_id_box"],
                course_ui["course_name_box"],
                course_ui["course_max_grade_box"],
                course_ui["course_passing_grade_box"],
                course_ui["course_state"],
                course_ui["mode_state"],
                course_ui["save_button"],
                course_ui["delete_button"],
                course_ui["cancel_button"],
            ]
        )


        # --- Check Changes for Save button
        course_ui["course_name_box"].input(
            fn=check_course_changes,
            inputs=[
                course_ui["mode_state"],
                course_ui["course_state"],
                
                course_ui["course_name_box"],
                course_ui["course_max_grade_box"],
                course_ui["course_passing_grade_box"],
            ],
            outputs=[
                course_ui["save_button"]
            ]
        )

        course_ui["course_max_grade_box"].input(
            fn=check_course_changes,
            inputs=[
                course_ui["mode_state"],
                course_ui["course_state"],
                
                course_ui["course_name_box"],
                course_ui["course_max_grade_box"],
                course_ui["course_passing_grade_box"],
            ],
            outputs=[
                course_ui["save_button"]
            ]
        )

        course_ui["course_passing_grade_box"].input(
            fn=check_course_changes,
            inputs=[
                course_ui["mode_state"],
                course_ui["course_state"],
                
                course_ui["course_name_box"],
                course_ui["course_max_grade_box"],
                course_ui["course_passing_grade_box"],
            ],
            outputs=[
                course_ui["save_button"]
            ]
        )


        # delete course
        course_ui["delete_button"].click(
            fn=partial(delete_course, store=store),
            inputs=[
                course_ui["course_state"]
            ],
            outputs=[
                course_ui["course_table"],               # 1

                course_ui["course_title"],               # 2

                course_ui["course_id_box"],
                course_ui["course_name_box"],            # 3
                course_ui["course_max_grade_box"],       # 4
                course_ui["course_passing_grade_box"],  # 5

                course_ui["course_state"],              # 6
                course_ui["mode_state"],                # 7

                
                course_ui["save_button"],              # 8
                course_ui["delete_button"],            # 9
                course_ui["cancel_button"],            # 10
            ]
        )

        # add course
        course_ui["add_button"].click(
            fn=lambda: render_course_details(
                "create"
            ),
            outputs=[
                course_ui["course_title"],               # 2

                course_ui["course_id_box"],
                course_ui["course_name_box"],            # 3
                course_ui["course_max_grade_box"],       # 4
                course_ui["course_passing_grade_box"],  # 5

                course_ui["course_state"],              # 6
                course_ui["mode_state"],                # 7

                course_ui["save_button"],              # 8
                course_ui["delete_button"],            # 9
                course_ui["cancel_button"],            # 10
            ]
        )


        course_ui["cancel_button"].click(
            fn=lambda: render_course_details(
                "empty"
            ),
            outputs=[
                course_ui["course_title"],               # 2
                course_ui["course_id_box"],
                course_ui["course_name_box"],            # 3
                course_ui["course_max_grade_box"],       # 4
                course_ui["course_passing_grade_box"],  # 5

                course_ui["course_state"],              # 6
                course_ui["mode_state"],                # 7

                course_ui["save_button"],              # 8
                course_ui["delete_button"],            # 9
                course_ui["cancel_button"],            # 10
            ]
        )





# ============================================================
# Grades
# ============================================================


        grade_ui["grade_table"].select(
            fn=on_grade_select,
            inputs=[
                grade_ui["grade_table"]
            ],
            outputs=[
                grade_ui["grade_title"],
                grade_ui["student_box"],
                grade_ui["course_name_box"],
                grade_ui["score_box"],
                grade_ui["date_box"],
                grade_ui["notes_box"],
                grade_ui["grade_state"],
                grade_ui["mode_state"],
                grade_ui["save_button"],
                grade_ui["delete_button"],
                grade_ui["cancel_button"],
            ]
        )



    # save and update course
        # grade_ui["save_button"].click(
        #     fn=partial(
        #         save_grade,
        #         store=store
        #     ),
        #     inputs=[
        #         grade_ui["mode_state"],
        #         grade_ui["grade_state"],
                
        #         grade_ui["student_box"],
        #         grade_ui["course_name_box"],
        #         grade_ui["score_box"],
        #         grade_ui["date_box"],
        #         grade_ui["notes_box"],
        #     ],
        #     outputs=[
        #         grade_ui["grade_table"],
        #         grade_ui["grade_title"],
        #         grade_ui["student_box"],
        #         grade_ui["course_name_box"],
        #         grade_ui["score_box"],
        #         grade_ui["date_box"],
        #         grade_ui["notes_box"],
        #         grade_ui["grade_state"],
        #         grade_ui["mode_state"],
        #         grade_ui["save_button"],
        #         grade_ui["delete_button"],
        #         grade_ui["cancel_button"],
        #     ]
        # )


        # --- Check Changes for Save button
        # grade_ui["grade_name_box"].input(
        #     fn=check_course_changes,
        #     inputs=[
        #         grade_ui["mode_state"],
        #         grade_ui["course_state"],
                
        #         grade_ui["course_name_box"],
        #         grade_ui["course_max_grade_box"],
        #         grade_ui["course_passing_grade_box"],
        #     ],
        #     outputs=[
        #         grade_ui["save_button"]
        #     ]
        # )

        # grade_ui["course_max_grade_box"].input(
        #     fn=check_course_changes,
        #     inputs=[
        #         grade_ui["mode_state"],
        #         grade_ui["course_state"],
                
        #         grade_ui["course_name_box"],
        #         grade_ui["course_max_grade_box"],
        #         grade_ui["course_passing_grade_box"],
        #     ],
        #     outputs=[
        #         grade_ui["save_button"]
        #     ]
        # )

        # grade_ui["course_passing_grade_box"].input(
        #     fn=check_course_changes,
        #     inputs=[
        #         grade_ui["mode_state"],
        #         grade_ui["course_state"],
                
        #         grade_ui["course_name_box"],
        #         grade_ui["course_max_grade_box"],
        #         grade_ui["course_passing_grade_box"],
        #     ],
        #     outputs=[
        #         grade_ui["save_button"]
        #     ]
        # )


        # delete course
        # grade_ui["delete_button"].click(
        #     fn=partial(delete_course, store=store),
        #     inputs=[
        #         grade_ui["course_state"]
        #     ],
        #     outputs=[
        #         grade_ui["course_table"],               # 1

        #         grade_ui["course_title"],               # 2

        #         grade_ui["course_id_box"],
        #         grade_ui["course_name_box"],            # 3
        #         grade_ui["course_max_grade_box"],       # 4
        #         grade_ui["course_passing_grade_box"],  # 5

        #         grade_ui["course_state"],              # 6
        #         grade_ui["mode_state"],                # 7

                
        #         grade_ui["save_button"],              # 8
        #         grade_ui["delete_button"],            # 9
        #         grade_ui["cancel_button"],            # 10
        #     ]
        # )

        # # add course
        # grade_ui["add_button"].click(
        #     fn=lambda: render_course_details(
        #         "create"
        #     ),
        #     outputs=[
        #         grade_ui["course_title"],               # 2

        #         grade_ui["course_id_box"],
        #         grade_ui["course_name_box"],            # 3
        #         grade_ui["course_max_grade_box"],       # 4
        #         grade_ui["course_passing_grade_box"],  # 5

        #         grade_ui["course_state"],              # 6
        #         grade_ui["mode_state"],                # 7

        #         grade_ui["save_button"],              # 8
        #         grade_ui["delete_button"],            # 9
        #         grade_ui["cancel_button"],            # 10
        #     ]
        # )


        # grade_ui["cancel_button"].click(
        #     fn=lambda: render_course_details(
        #         "empty"
        #     ),
        #     outputs=[
        #         grade_ui["course_title"],               # 2
        #         grade_ui["course_id_box"],
        #         grade_ui["course_name_box"],            # 3
        #         grade_ui["course_max_grade_box"],       # 4
        #         grade_ui["course_passing_grade_box"],  # 5

        #         grade_ui["course_state"],              # 6
        #         grade_ui["mode_state"],                # 7

        #         grade_ui["save_button"],              # 8
        #         grade_ui["delete_button"],            # 9
        #         grade_ui["cancel_button"],            # 10
        #     ]
        # )






    # start Gradio App
    app.launch(inbrowser=True)

if __name__ == "__main__":
    main()