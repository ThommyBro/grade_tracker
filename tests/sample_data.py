from grade_management.course import Course
from grade_management.student import Student
from grade_management.grade import Grade
from grade_management.gradebook import GradeBook


def create_test_data():
    """
    ...
    """

    # --- create students
    students = {
                "s1": Student("12345","t", "b","some.student@mit.com"),
                "s2": Student("23456","a", "b","ab@sample.com"),
                "s3":  Student("34567","g","z","abc@cba.bac"),
                "s4": Student("45678","Anna", "Alpha", "anna@home.de"),
                "s5": Student("56789","Benno", "Beta", "benno@home.com"),
                "s7": Student("67891","Benno", "der Zweite", "benno.zwei@mail.com"),
                "s6": Student("78912","Celine","Gamma","123@test.com")
            }
    

    # --- create courses
    courses = {
                "c1": Course("101", "QM1"),
                "c2": Course("102", "Python classics"),
                "c3": Course("103","Higher Category Theory", 100.0, 75),
                "c4": Course("104", "QM2", 100, 50)
            }
    

    # ---- create grades
    grades = [
                Grade(students["s1"], courses["c1"], 95, "2026-07-16"),
                Grade(students["s1"], courses["c2"], 88, "2026-07-17"),
                Grade(students["s2"], courses["c1"], 73, "2026-07-16"),
                Grade(students["s3"], courses["c2"], 100, "2026-07-17"),
                Grade(students["s4"], courses["c2"], 50, "2026-07-17"),
                Grade(students["s5"], courses["c4"], 34, "2026-07-17"),
                Grade(students["s6"], courses["c1"], 89, "2026-07-17"),
                Grade(students["s6"], courses["c3"], 75, "2026-07-17"),
                Grade(students["s4"], courses["c4"], 100, "2026-07-17")
            ]
    
    return {
            "students": students,
            "courses": courses,
            "grades": grades,
            }



# ---- Helper functions to fill in the data


def populate_gradebook(gbook: GradeBook, data: dict) -> None:
    """
    Just fills a gradebook with the given data.
    """

    for student in data["students"].values():
        gbook.add_student(student)

    for course in data["courses"].values():
        gbook.add_course(course)

    for grade in data["grades"]:
        gbook.record_grade(
            grade.student,
            grade.course,
            grade.score,
            grade.date,
            grade.notes,
        )

def populate_database(student_repo, course_repo, grade_repo, data: dict) -> None:
    """
    Analog to populate_gradebook function. 
    """

    for student in data["students"].values():
        student_repo.add(student)

    for course in data["courses"].values():
        course_repo.add(course)

    for grade in data["grades"].values():
        grade_repo.add(grade)
