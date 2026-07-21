import sqlite3
import pytest

# import repos
from grade_db.student_repository import StudentRepository
from grade_db.course_repository import CourseRepository
from grade_db.grade_repository import GradeRepository 

# import stores
from grade_store.grade_store import GradeStore
from grade_store.in_memory_store import InMemoryGradeStore
from grade_store.sqlite_store import SqliteGradeStore

# import sample data und function
from sample_data import SampleData, create_test_data





# --- Create Factory Functions --- #

def create_memory_store() -> GradeStore:
    """Returns in-memory implementation of GradeStore"""
    return InMemoryGradeStore()

def create_sqlite_store() -> GradeStore:
    """Returns tmp SQLite implementation of GradeStore"""

    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")

    student_repo = StudentRepository(con)
    course_repo = CourseRepository(con)
    grade_repo = GradeRepository(con)

    student_repo.create_table()
    course_repo.create_table()
    grade_repo.create_table()

    return SqliteGradeStore(
                    student_repo,
                    course_repo,
                    grade_repo,
                )


def populate_store(store: GradeStore, data: SampleData,) -> None:
    """Fill in sample data. Does not depend Storage method!"""

    for student in data.students.values():
        store.add_student(student)

    for course in data.courses.values():
        store.add_course(course)

    for grade in data.grades:
        store.record_grade(grade)


# --- Define Tests --- #

def run_store_tests(store: GradeStore, expected: SampleData) -> None:

    # --- Check data in Storage --- #
    assert len(store.get_all_students()) == len(expected.students)
    assert len(store.get_all_courses()) == len(expected.courses)
    assert len(store.get_all_grades()) == len(expected.grades)

    # --- Single object Tests --- #

    # --- students ---
    student = store.get_student("12345")
    assert student is not None
    assert student.first_name == "t"
    assert student.last_name == "b"
    assert student.email == "some.student@mit.com"

    print(type(store))
    print(student)
    print(store.get_all_students())

   
    # ---  courses --- #
    course = store.get_course("101")
    assert course is not None
    assert course.name == "QM1"

    grades = store.get_student_grades("12345")
    assert len(grades) == 2
    assert grades[0].course.course_id == "101"
    assert grades[1].course.course_id == "102"
    

    # ---  Grades --- #
    grade = grades[0]
    grade.score = 75.0
    store.update_grade(grade)
    updated_grade = store.get_student_grades("12345")[0]
    assert updated_grade.score == 75.0

    # Check Grades delete
    grades = store.get_student_grades("12345")
    assert len(grades) == 2
    grade_to_delete = grades[0]
    store.delete_grade(grade_to_delete)
    grades = store.get_student_grades("12345")
    assert len(grades) == 1
    assert grades[0].course.course_id == "102"





# --- RUN --- #
def test_in_memory_store():

    data = create_test_data()
    print("Testing InMemoryStore...")

    store = create_memory_store()

    populate_store(store, data)

    run_store_tests(store, data)

    print("Passed")


def test_sqllite_store():

    data = create_test_data()
    print("Testing SqliteStore...")

    store = create_sqlite_store()

    populate_store(store, data)

    run_store_tests(store, data)

    print("Passed")

