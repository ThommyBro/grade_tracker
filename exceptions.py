"""Custon exceptions for GradeTracker"""

from __future__ import annotations


class GradeTrackerError(Exception):
    """Serves as base class for custom exceptions."""


class StudentNotFoundError(GradeTrackerError):
    """Is raised if a studend ID is not found."""

    def __init__(self, student_id: str):
        self.student_id = student_id
        super().__init__(f"Student with ID '{student_id}' not found.")


class CourseNotFoundError(GradeTrackerError):
    """Is raised if a course ID is not found."""

    def __init__(self, course_id: str):
        self.course_id = course_id
        super().__init__(f"Course with ID '{course_id}' not found.")


class DuplicateEntryError(GradeTrackerError):
    """Is raised if an entry with the same ID already exists."""

    def __init__(self, entity: str, entity_id: str):
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} with ID '{entity_id}' already exists.")


class GradeNotFoundError(GradeTrackerError):
    """Is raised if a grade ID is not found."""

    def __init__(self, grade_id: str):
        self.grade_id = grade_id
        super().__init__(f"Note mit ID '{grade_id}' wurde nicht gefunden.")
