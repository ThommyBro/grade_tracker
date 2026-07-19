import sqlite3
import gradio as gr


from grade_management.gradebook import GradeBook

from grade_db.student_repository import StudentRepository
from grade_db.course_repository import CourseRepository
from grade_db.grade_repository import GradeRepository

from grade_store.sqlite_store import SqliteGradeStore

from sample_data import create_test_data, populate_database



# =======================================================
# Functions for creating the complete setup
# and sample data
# =======================================================


def create_sqlite_store():

    # Use database
    con = sqlite3.connect("grade.db")
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


def show_summary(gradebook):
    return (
        f"Students: {len(gradebook.students)}\n"
        f"Courses: {len(gradebook.courses)}\n"
        f"Grades: {len(gradebook.grades)}"
    )


def get_dashboard_stats(gradebook):
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
    theme = gr.themes.Soft(primary_hue="indigo", secondary_hue="neutral", neutral_hue="slate")
    
    

# =======================================================

    # Gradio 
    with gr.Blocks(theme = theme, title= "Grade Tracker") as demo:
        # App logo
        with gr.Group():
            with gr.Row(equal_height=True):
                with gr.Column(scale=0, min_width=80):
                    gr.Image(
                        "images/logo.png",
                        container=False,
                        width=65,
                        interactive=False,
                        #show_download_button=False,
                        show_label=False
                    )

            with gr.Column():

                gr.Markdown("""
                # Grade Tracker

                Academic Management Dashboard
                """)

        # Tabs for better clicking experience
        with gr.Tabs():
            with gr.Tab("👨‍🎓 Students"):
                gr.Markdown("## Student Management")

            with gr.Tab("📚 Courses"):
                gr.Markdown("## Course Management")

            with gr.Tab("📝 Grades"):
                gr.Markdown("## Grade Management")

            with gr.Tab("📊 Statistics"):
                ...

        refresh = gr.Button("🔄 Load Dashboard")

        refresh.click(
                        fn=lambda: get_dashboard_stats(gradebook),
                        #outputs=[students_card, courses_card, grades_card]
                    )
        

        with gr.Accordion("Import / Export", open=False):
            upload = gr.File()
            export = gr.Button("Export")


    # start Gradio App
    demo.launch(inbrowser=True)



if __name__ == "__main__":
    main()