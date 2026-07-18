import sqlite3

from grade_management.student import Student
from grade_management.course import Course
from grade_management.grade import Grade

from grade_db.student_repository import StudentRepository
from grade_db.course_repository import CourseRepository
from grade_db.grade_repository import GradeRepository

# ===============================================
# Only Assertion tests for sqllite_store
# Test that obejcts are correctly build in grade_repo
# ===============================================



def test_grade_join_queries():

    # Create in memomery database for testing
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")

    # Repositories
    student_repo = StudentRepository(con)
    course_repo = CourseRepository(con)
    grade_repo = GradeRepository(con)

    # Create all tables
    student_repo.create_table()
    course_repo.create_table()
    grade_repo.create_table()

    # Test data
    student = Student(
        "12345",
        "Anna",
        "Alpha",
        "anna@test.de"
    )

    course = Course(
        "101",
        "Python"
    )

    grade = Grade(
        student=student,
        course=course,
        score=95,
        date="18.07.2026"
    )


    # Save data
    student_repo.add(student)
    course_repo.add(course)
    grade_repo.add(grade)


    # Test get_all_with_details()
    grades = grade_repo.get_all_with_details()

    assert len(grades) == 1

    result = grades[0]

    assert isinstance(result, Grade)

    assert result.student.student_id == "12345"
    assert result.course.course_id == "101"
    assert result.score == 95


    # Test get_by_student_with_details()

    grades = grade_repo.get_by_student_with_details("12345")

    assert len(grades) == 1

    assert grades[0].student.first_name == "Anna"
    assert grades[0].course.name == "Python"

    con.close()