from grade_management.grade import Grade
from grade_management.student import Student
from grade_management.course import Course


student = Student(
    student_id="S001",
    first_name="Max",
    last_name="Mustermann",
    email="max@test.de"
)

course = Course(
    course_id="C001",
    name="Mathematik"
)

grade = Grade(
    student=student,
    course=course,
    score=90,
    date="2026-07-20"
)

print(grade)