"""GradeBook: zentrale Fassade für Studierende, Kurse und Noten.

Seit Phase 4 delegiert GradeBook die eigentliche Speicherung an ein
GradeStore (Strategy-Pattern, siehe store.py) und implementiert selbst nur
noch Statistik, Suche und (De-)Serialisierung darauf aufbauend.

Standardmäßig wird ein InMemoryGradeStore verwendet — das bisherige,
dict-basierte Verhalten bleibt also unverändert:

    book = GradeBook()

Für SQLite-Persistenz kann stattdessen ein SqliteGradeStore übergeben
werden, ohne dass sich an der restlichen Nutzung von GradeBook etwas
ändert:

    book = GradeBook(store=SqliteGradeStore("noten.db"))
"""

from __future__ import annotations

import re

from grade_management.course import Course
from grade_management.grade import Grade
from grade_management.student import Student
from storage.base import GradeStore
from storage.memory_store import MemoryGradeStore


class GradeBook:
    def __init__(self, store: GradeStore | None = None) -> None:
        self.store: GradeStore = store if store is not None else MemoryGradeStore()

    # ------------------------------------------------------------------ #
    # Rückwärtskompatible dict/list-Ansichten auf den Store.
    # (Bequemer Zugriff wie zuvor, z. B. book.students["s1"] oder
    #  len(book.grades); intern wird alles über self.store abgewickelt.)
    # ------------------------------------------------------------------ #
    @property
    def students(self) -> dict[str, Student]:
        return {s.student_id: s for s in self.store.get_all_students()}

    @property
    def courses(self) -> dict[str, Course]:
        return {c.course_id: c for c in self.store.get_all_courses()}

    @property
    def grades(self) -> list[Grade]:
        return self.store.get_all_grades()

    # ------------------------------------------------------------------ #
    # CRUD actions via store interface
    # ------------------------------------------------------------------ #
    def add_student(self, student: Student) -> None:
        self.store.add_student(student)

    def add_course(self, course: Course) -> None:
        self.store.add_course(course)

    def add_grade(self, student_id: str, course_id: str, score: float, date: str, notes: str = "",) -> Grade:
        return self.store.add_grade(student_id, course_id, score, date, notes)

    def get_student(self, student_id: str) -> Student:
        return self.store.get_student(student_id)

    def get_course(self, course_id: str) -> Course:
        return self.store.get_course(course_id)

    def get_student_grades(self, student_id: str) -> list[Grade]:
        return self.store.get_student_grades(student_id)

    def get_course_grades(self, course_id: str) -> list[Grade]:
        return self.store.get_course_grades(course_id)

    def get_grade(self, grade_id: str) -> Grade:
        return self.store.get_grade(grade_id)

   
    def update_student(self, student: Student) -> None:
        """Updates a student, but student_id stays the same."""
        self.store.update_student(student)

    def delete_student(self, student_id: str) -> None:
        """Deletes a student and its corresponding grades."""
        self.store.delete_student(student_id)

    def update_course(self, course: Course) -> None:
        """Updates Course but checks scores beforehand."""
        for grade in self.get_course_grades(course.course_id):
            if not (0 <= grade.score <= course.max_grade):
                raise ValueError(
                    f"Course '{course.course_id}' can not be updated: "
                    f"Grade with score={grade.score} would be illegal with "
                    f"max_grade={course.max_grade}. Please "
                    f"update or delete corresponging grades."
                )
        self.store.update_course(course)

    def delete_course(self, course_id: str) -> None:
        """Deletes a Course and every Grade in it."""
        self.store.delete_course(course_id)

    def update_grade(self, grade_id: str, score: float, date: str, notes: str = "") -> Grade:
        return self.store.update_grade(grade_id, score, date, notes)

    def delete_grade(self, grade_id: str) -> None:
        self.store.delete_grade(grade_id)

    # ------------------------------------------------------------------ #
    # Statistics — Data from Store but logic is Python
    # ------------------------------------------------------------------ #
    def student_average(self, student_id: str) -> float:
        grades = self.get_student_grades(student_id)
        if not grades:
            return 0.0
        return sum(g.percentage for g in grades) / len(grades)

    def course_average(self, course_id: str) -> float:
        grades = self.get_course_grades(course_id)
        if not grades:
            return 0.0
        return sum(g.score for g in grades) / len(grades)

    def course_pass_rate(self, course_id: str) -> float:
        grades = self.get_course_grades(course_id)
        if not grades:
            return 0.0
        passing = sum(1 for g in grades if g.is_passing)
        return passing / len(grades) * 100

    def top_students(self, n: int = 5) -> list[tuple[Student, float]]:
        averages = [
            (student, self.student_average(student.student_id))
            for student in self.store.get_all_students()
            if self.get_student_grades(student.student_id)
        ]
        averages.sort(key=lambda pair: pair[1], reverse=True)
        return averages[:n]


    # def students_at_risk(self, threshold: float = 60.0) -> list[Student]:
    #     return [
    #         student
    #         for student in self.store.get_all_students()
    #         if self.get_student_grades(student.student_id)
    #         and self.student_average(student.student_id) < threshold
    #     ]
    def students_at_risk(self, threshold: float = 60.0) -> list[tuple[Student, float]]:
        averages = [
                    (student, self.student_average(student.student_id))
                    for student in self.store.get_all_students()
                    if self.get_student_grades(student.student_id)
                    and self.student_average(student.student_id) < threshold
                ]
        averages.sort(key=lambda pair: pair[1], reverse=True)
        return averages[:]

    # ------------------------------------------------------------------ #
    # Searching
    # ------------------------------------------------------------------ #
    def search_students(self, query: str) -> list[Student]:
        pattern = re.compile(query, re.IGNORECASE)
        return [s for s in self.store.get_all_students()
            if pattern.search(s.full_name) or pattern.search(s.email)
        ]

    def search_courses(self, query: str) -> list[Course]:
        pattern = re.compile(query, re.IGNORECASE)
        return [c for c in self.store.get_all_courses() if pattern.search(c.name)]


    # ------------------------------------------------------------------ #
    # (De-)Serialisierung — Grundlage für JSON-Persistenz (persistence.py)
    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict:
        return {
            "students": [
                {
                    "student_id": s.student_id,
                    "first_name": s.first_name,
                    "last_name": s.last_name,
                    "email": s.email,
                }
                for s in self.store.get_all_students()
            ],
            "courses": [
                {
                    "course_id": c.course_id,
                    "name": c.name,
                    "max_grade": c.max_grade,
                    "passing_grade": c.passing_grade,
                }
                for c in self.store.get_all_courses()
            ],
            "grades": [
                {
                    "grade_id": g.grade_id,
                    "student_id": g.student.student_id,
                    "course_id": g.course.course_id,
                    "score": g.score,
                    "date": g.date,
                    "notes": g.notes,
                }
                for g in self.store.get_all_grades()
            ],
        }

    @classmethod
    def from_dict(cls, data: dict, store: GradeStore | None = None) -> "GradeBook":
        """Baut ein GradeBook aus einem dict auf (siehe to_dict).

        Optional kann ein Store übergeben werden (z. B. SqliteGradeStore),
        in den importiert werden soll — Standard ist ein frischer
        InMemoryGradeStore.
        """
        book = cls(store=store)
        for s in data.get("students", []):
            book.add_student(Student(**s))
        for c in data.get("courses", []):
            book.add_course(Course(**c))
        for g in data.get("grades", []):
            grade_data = dict(g)
            grade_data.pop("grade_id", None)
            book.add_grade(**grade_data)
        return book



 
    
    

