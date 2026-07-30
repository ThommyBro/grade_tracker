import sqlite3
import pytest

from grade_db.student_repository import StudentRepository
from grade_db.course_repository import CourseRepository
from grade_db.grade_repository import GradeRepository
from grade_db.statistics_repository import StatisticsRepository
from grade_store.sqlite_store import SqliteGradeStore
from grade_management.gradebook import GradeBook
from grade_management.student import Student
from grade_management.course import Course
from grade_management.grade import Grade


@pytest.fixture
def store():

    conn = sqlite3.connect(":memory:")

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )


    student_repo = StudentRepository(conn)
    course_repo = CourseRepository(conn)
    grade_repo = GradeRepository(conn)
    statistics_repo = StatisticsRepository(conn)
    gbook = GradeBook()


    student_repo.create_table()
    course_repo.create_table()
    grade_repo.create_table()


    return SqliteGradeStore(
        student_repo,
        course_repo,
        grade_repo,
        statistics_repo,
        gbook
    )


@pytest.fixture
def student():

    return Student(
        student_id="99999",
        first_name="Max",
        last_name="Mustermann",
        email="max@test.de"
    )


@pytest.fixture
def course():

    return Course(
        course_id="PY101",
        name="Python"
    )

@pytest.fixture
def grade(student, course):

    return Grade(
        student=student,
        course=course,
        score=95,
        date="2026-07-30",
        notes="Good work"
    )