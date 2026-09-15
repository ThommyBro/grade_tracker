"""Tests für die GradeStore-Abstraktion (Phase 4).

Beide Implementierungen (InMemoryGradeStore, SqliteGradeStore) werden über
denselben parametrisierten Fixture gegen dieselben Erwartungen getestet —
das stellt sicher, dass sie sich identisch verhalten.
"""

import pytest

from grade_management.student import Student
from grade_management.course import Course
from grade_management.enrollment import Enrollment
from exceptions import (
    CourseNotFoundError,
    DuplicateEntryError,
    GradeNotFoundError,
    StudentNotFoundError,
)
from storage.base import GradeStore
from storage.memory_store import MemoryGradeStore
from storage.sqlite_store import GradeDataBase



@pytest.fixture(params=["memory", "sqlite"])
def store(request):
    if request.param == "memory":
        yield MemoryGradeStore()
    else:
        s = GradeDataBase(":memory:")
        yield s
        s.close()


def test_grade_store_is_abstract():
    with pytest.raises(TypeError):
        GradeStore()


def test_add_and_get_student(store):
    store.add_student(Student("s1", "Anna", "Müller", "anna@example.com"))
    student = store.get_student("s1")
    assert student.full_name == "Anna Müller"


def test_add_duplicate_student_raises(store):
    store.add_student(Student("s1", "Anna", "Müller", "anna@example.com"))
    with pytest.raises(DuplicateEntryError):
        store.add_student(Student("s1", "X", "Y", "x@y.com"))


def test_get_missing_student_raises(store):
    with pytest.raises(StudentNotFoundError):
        store.get_student("unknown")


def test_get_students(store):
    store.add_student(Student("s1", "Anna", "Müller", "anna@example.com"))
    store.add_student(Student("s2", "Ben", "Schmidt", "ben@example.com"))
    ids = {s.student_id for s in store.get_all_students()}
    assert ids == {"s1", "s2"}


def test_add_and_get_course(store):
    store.add_course(Course("c1", "Mathematik", "Summer 26", max_grade=20, passing_grade=10))
    course = store.get_course("c1")
    assert course.name == "Mathematik"
    assert course.max_grade == 20


def test_add_duplicate_course_raises(store):
    store.add_course(Course("c1", "Mathematik", "Summer 26"))
    with pytest.raises(DuplicateEntryError):
        store.add_course(Course("c1", "Andere Mathematik", "Winter 25"))


def test_get_missing_course_raises(store):
    with pytest.raises(CourseNotFoundError):
        store.get_course("unknown")


def test_add_grade_unknown_student_raises(store):
    store.add_course(Course("c1", "Mathematik", "Summer 26"))
    with pytest.raises(StudentNotFoundError):
        store.add_grade("unknown", "c1", 80, "2024-01-15")


def test_add_grade_unknown_course_raises(store):
    store.add_student(Student("s1", "Anna", "Müller", "anna@example.com"))
    with pytest.raises(CourseNotFoundError):
        store.add_grade("s1", "unknown", 80, "2024-01-15")


def test_add_and_get_grades(store):
    store.add_student(Student("s1", "Anna", "Müller", "anna@example.com"))
    store.add_course(Course("c1", "Mathematik","Summer 26"))
    store.add_grade("s1", "c1", 80, "2024-01-15", notes="Klausur 1")

    student_grades = store.get_student_grades("s1")
    course_grades = store.get_course_grades("c1")

    assert len(student_grades) == 1
    assert len(course_grades) == 1
    assert student_grades[0].score == 80
    assert student_grades[0].notes == "Klausur 1"


def test_get_student_grades_unknown_student_raises(store):
    with pytest.raises(StudentNotFoundError):
        store.get_student_grades("unknown")


def test_get_course_grades_unknown_course_raises(store):
    with pytest.raises(CourseNotFoundError):
        store.get_course_grades("unknown")


def test_get_all_grades(store):
    store.add_student(Student("s1", "Anna", "Müller", "anna@example.com"))
    store.add_course(Course("c1", "Mathematik","Summer 26"))
    store.add_grade("s1", "c1", 80, "2024-01-15")
    store.add_grade("s1", "c1", 90, "2024-01-16")
    assert len(store.get_all_grades()) == 2


def test_in_memory_store_returns_defensive_copies():
    """InMemoryGradeStore darf keine internen Listen/Dicts direkt herausgeben."""
    store = MemoryGradeStore()
    store.add_student(Student("s1", "Anna", "Müller", "anna@example.com"))
    store.add_course(Course("c1", "Mathematik","Summer 26"))
    store.add_grade("s1", "c1", 80, "2024-01-15")

    grades = store.get_student_grades("s1")
    grades.clear()
    assert len(store.get_student_grades("s1")) == 1

    students = store.get_all_students()
    students.clear()
    assert len(store.get_all_students()) == 1


# ------------------------------------------------------------------ #
# Neue CRUD-Tests: update_student, delete_student (kaskadierend),
# update_course, delete_course (kaskadierend), get/update/delete_grade.
# Laufen dank des "store"-Fixtures wieder gegen BEIDE Implementierungen.
# ------------------------------------------------------------------ #
@pytest.fixture
def seeded_store(store):
    """Ein Store mit 2 Studierenden, 2 Kursen und 4 Noten (für CRUD-Tests)."""
    store.add_student(Student("s1", "Anna", "Müller", "anna@example.com"))
    store.add_student(Student("s2", "Ben", "Schmidt", "ben@example.com"))
    store.add_course(Course("c1", "Mathematik","Summer 26"))
    store.add_course(Course("c2", "Physik", "Summer 25", max_grade=20, passing_grade=10))
    store.add_grade("s1", "c1", 90, "2024-01-15")
    store.add_grade("s1", "c2", 15, "2024-01-16")
    store.add_grade("s2", "c1", 40, "2024-01-15")
    store.add_grade("s2", "c2", 8, "2024-01-16")
    return store


def test_update_student_changes_fields(seeded_store):
    seeded_store.update_student(Student("s1", "Anna", "Neumann", "neu@example.com"))
    updated = seeded_store.get_student("s1")
    assert updated.last_name == "Neumann"
    assert updated.email == "neu@example.com"


def test_update_student_unknown_id_raises(seeded_store):
    with pytest.raises(StudentNotFoundError):
        seeded_store.update_student(Student("unknown", "X", "Y", "x@y.com"))


def test_delete_student_cascades_to_grades(seeded_store):
    assert len(seeded_store.get_all_grades()) == 4
    seeded_store.delete_student("s1")
    with pytest.raises(StudentNotFoundError):
        seeded_store.get_student("s1")
    # Beide Noten von s1 (c1 und c2) müssen mit weg sein, s2s Noten bleiben.
    remaining = seeded_store.get_all_grades()
    assert len(remaining) == 2
    assert all(g.student.student_id == "s2" for g in remaining)


def test_delete_student_unknown_id_raises(seeded_store):
    with pytest.raises(StudentNotFoundError):
        seeded_store.delete_student("unknown")


def test_update_course_changes_fields(seeded_store):
    seeded_store.update_course(Course("c1", "Mathematik","Summer 26", max_grade=100, passing_grade=45))
    updated = seeded_store.get_course("c1")
    assert updated.passing_grade == 45


def test_update_course_unknown_id_raises(seeded_store):
    with pytest.raises(CourseNotFoundError):
        seeded_store.update_course(Course("unknown", "X", "Summer 26"))


def test_delete_course_cascades_to_grades(seeded_store):
    seeded_store.delete_course("c1")
    with pytest.raises(CourseNotFoundError):
        seeded_store.get_course("c1")
    remaining = seeded_store.get_all_grades()
    assert len(remaining) == 2
    assert all(g.course.course_id == "c2" for g in remaining)


def test_delete_course_unknown_id_raises(seeded_store):
    with pytest.raises(CourseNotFoundError):
        seeded_store.delete_course("unknown")


def test_get_grade_by_id(seeded_store):
    grade = seeded_store.get_student_grades("s1")[0]
    fetched = seeded_store.get_grade(grade.grade_id)
    assert fetched.grade_id == grade.grade_id
    assert fetched.score == grade.score


def test_get_grade_unknown_id_raises(seeded_store):
    with pytest.raises(GradeNotFoundError):
        seeded_store.get_grade("does-not-exist")


def test_update_grade_changes_score_date_notes(seeded_store):
    grade = seeded_store.get_student_grades("s1")[0]
    updated = seeded_store.update_grade(grade.grade_id, score=77, date="2024-02-01", notes="Nachschreiber")
    assert updated.grade_id == grade.grade_id  # ID bleibt gleich
    assert updated.score == 77
    assert updated.notes == "Nachschreiber"
    # Student/Kurs bleiben unverändert:
    assert updated.student.student_id == grade.student.student_id
    assert updated.course.course_id == grade.course.course_id


def test_update_grade_validates_score_range(seeded_store):
    grade = seeded_store.get_student_grades("s1")[0]
    with pytest.raises(ValueError):
        seeded_store.update_grade(grade.grade_id, score=99999, date="2024-02-01")
    # Die ungültige Änderung darf NICHT übernommen worden sein:
    assert seeded_store.get_grade(grade.grade_id).score == grade.score


def test_update_grade_unknown_id_raises(seeded_store):
    with pytest.raises(GradeNotFoundError):
        seeded_store.update_grade("does-not-exist", score=50, date="2024-01-15")


def test_delete_grade(seeded_store):
    grade = seeded_store.get_student_grades("s1")[0]
    seeded_store.delete_grade(grade.grade_id)
    with pytest.raises(GradeNotFoundError):
        seeded_store.get_grade(grade.grade_id)
    assert len(seeded_store.get_all_grades()) == 3


def test_delete_grade_unknown_id_raises(seeded_store):
    with pytest.raises(GradeNotFoundError):
        seeded_store.delete_grade("does-not-exist")


def test_add_grade_assigns_unique_ids(seeded_store):
    ids = [g.grade_id for g in seeded_store.get_all_grades()]
    assert len(ids) == len(set(ids))  # alle eindeutig


# =================================================
# Test für Enrollments
# =================================================


# @pytest.fixture
# def enrollment_store():
#     store = MemoryGradeStore()
#     store.add_student(Student("s1", "Anna", "Müller", "anna@example.com"))
#     store.add_course(Course("c1", "Mathematik", "Summer 26"))
#     return store


@pytest.fixture
def enrollment_store(store):
    store.add_student(Student("s1", "Anna", "Müller", "anna@example.com"))
    store.add_student(Student("s2", "Ben", "Schmidt", "ben@example.com"))
    store.add_course(Course("c1", "Mathematik", "Summer 26"))
    store.add_course(Course("c2", "Physik", "Summer 26"))

    return store


def test_add_enrollment(enrollment_store):
    enrollment = enrollment_store.add_enrollment("s1", "c1")
    assert enrollment.student_id == "s1"
    assert enrollment.course_id == "c1"

def test_is_enrolled(enrollment_store):
    assert enrollment_store.is_enrolled("s1", "c1") is False
    enrollment_store.add_enrollment("s1", "c1")
    assert enrollment_store.is_enrolled("s1", "c1") is True


def test_duplicate_enrollment_raises(enrollment_store):
    enrollment_store.add_enrollment("s1", "c1")
    with pytest.raises(DuplicateEntryError):
        enrollment_store.add_enrollment("s1", "c1")


def test_enrollment_unknown_student_raises(enrollment_store):
    with pytest.raises(StudentNotFoundError):
        enrollment_store.add_enrollment("unknown", "c1")


def test_enrollment_unknown_course_raises(enrollment_store):
    with pytest.raises(CourseNotFoundError):
        enrollment_store.add_enrollment("s1", "unknown")


def test_get_student_enrollments(enrollment_store):
    enrollment_store.add_enrollment("s1", "c1")
    enrollment_store.add_enrollment("s1", "c2")

    enrollments = enrollment_store.get_student_enrollments("s1")

    course_ids = {e.course_id for e in enrollments}

    assert course_ids == {"c1", "c2"}


def test_get_course_enrollments(enrollment_store):
    enrollment_store.add_enrollment("s1", "c1")
    enrollment_store.add_enrollment("s2", "c1")

    enrollments = enrollment_store.get_course_enrollments("c1")

    student_ids = {e.student_id for e in enrollments}

    assert student_ids == {"s1", "s2"}


def test_delete_student_cascades_to_enrollments(enrollment_store):
    enrollment_store.add_enrollment("s1", "c1")
    enrollment_store.add_enrollment("s1", "c2")
    enrollment_store.add_enrollment("s2", "c1")

    enrollment_store.delete_student("s1")

    assert enrollment_store.is_enrolled("s1", "c1") is False
    assert enrollment_store.is_enrolled("s1", "c2") is False

    assert enrollment_store.is_enrolled("s2", "c1") is True


def test_delete_course_cascades_to_enrollments(enrollment_store):
    enrollment_store.add_enrollment("s1", "c1")
    enrollment_store.add_enrollment("s2", "c1")
    enrollment_store.add_enrollment("s1", "c2")

    enrollment_store.delete_course("c1")

    assert enrollment_store.is_enrolled("s1", "c1") is False
    assert enrollment_store.is_enrolled("s2", "c1") is False

    assert enrollment_store.is_enrolled("s1", "c2") is True