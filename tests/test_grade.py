from grade_management.student import Student
from grade_management.course import Course
from grade_management.grade import Grade
from grade_db.grade_repository import GradeRecord

def test_grade_to_record():
    """
    Test for: Get a Grade object and convert it GradeRecord, so Db can use it
    Method that is testes is ' from_grade' in grade_repository.
    """
    student = Student(
        student_id="S001",
        first_name="Max",
        last_name="Mustermann",
        email="max@test.de"
    )

    course = Course(
        course_id="C001",
        name="Math"
    )

    grade = Grade(
        student=student,
        course=course,
        score=90,
        date="2026-07-20",
        notes="great exam",
        
    )

    record = GradeRecord.from_grade(grade)

    
    assert record.student_id == "S001"
    assert record.course_id == "C001"
    assert record.score == 90
    assert record.date == "2026-07-20"
    assert record.notes == "great exam"


