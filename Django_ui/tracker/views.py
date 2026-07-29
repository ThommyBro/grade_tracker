from django.shortcuts import render

# Create your views here.
# Here starts my stuff

from django.http import HttpResponse
import sys
import os

from grade_store.sqlite_store import SqliteGradeStore
from grade_db.student_repository import StudentRepository
from grade_db.course_repository import CourseRepository
from grade_db.grade_repository import GradeRepository
from grade_db.statistics_repository import StatisticsRepository

from grade_management.gradebook import GradeBook

import sqlite3

def get_store():


    print("CURRENT PATH:")
    print(os.getcwd())

    db_path = "grade.db"

    print("DATABASE:")
    print(os.path.abspath(db_path))

    con = sqlite3.connect(db_path)

    student_repo = StudentRepository(con)
    course_repo = CourseRepository(con)
    grade_repo = GradeRepository(con)
    stats_repo = StatisticsRepository(con)
    gradebook = GradeBook()

    return SqliteGradeStore(
        student_repo,
        course_repo,
        grade_repo,
        stats_repo,
        gradebook
    )


def student_list(request):
    """Get all students."""

    store = get_store()
    students = store.get_all_students()

    print("NUMBER OF STUDENTS:", len(students))
    print("STUDENTS:", students)

    return render(
        request,
        "tracker/student_list.html",
        {
            "students": students
        }
    )


def student_detail(request, student_id):

    store = get_store()
    student = store.get_student(student_id)

    return render(
        request,
        "tracker/partials/student_detail.html",
        {
            "student": student
        }
    )


def clear_student_detail(request):
    print("CLEAR VIEW WURDE AUFGERUFEN")
    return HttpResponse(" ")


def course_list(request):
    """Get all courses."""

    store = get_store()
    courses = store.get_all_courses()

    print("NUMBER OF COURSES:", len(courses))
    print("COURSES:", courses)

    return render(
        request,
        "tracker/course_list.html",
        {
            "courses": courses
        }
    )


def student_test(request):
    """Test for student details"""
    return HttpResponse("""
        <div class="card shadow mt-3">
            <div class="card-body">
                <h4>HTMX funktioniert 🎉</h4>
                <p>Dieser Inhalt wurde dynamisch nachgeladen.</p>
            </div>
        </div>
    """)
   



def home(request):
    return HttpResponse("Welcome to the real world!")