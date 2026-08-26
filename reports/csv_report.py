

from __future__ import annotations

import csv
import io
from typing import TYPE_CHECKING

from reports.base import ReportGenerator

if TYPE_CHECKING:
    from gradebook_new import GradeBook


class CsvReportGenerator(ReportGenerator):
    """3 Methods for all Reports from the Baseclass in CSV format."""

    def generate_student_report(self, student_id: str, gradebook: GradeBook) -> str:
        grades = gradebook.get_student_grades(student_id)
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            ["grade_id", "course_id", "course_name", "score", "max_grade", "letter_grade", "passing"]
        )
        for g in grades:
            writer.writerow(
                [
                    g.grade_id,
                    g.course.course_id,
                    g.course.name,
                    g.score,
                    g.course.max_grade,
                    g.letter_grade,
                    g.is_passing,
                ]
            )
        return buf.getvalue()

    def generate_course_report(self, course_id: str, gradebook: GradeBook) -> str:
        grades = gradebook.get_course_grades(course_id)
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["grade_id", "student_id", "student_name", "score", "letter_grade", "passing"])
        for g in grades:
            writer.writerow(
                [g.grade_id, g.student.student_id, g.student.full_name, g.score, g.letter_grade, g.is_passing]
            )
        return buf.getvalue()

    def generate_summary_report(self, gradebook: GradeBook) -> str:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["metric", "value"])
        writer.writerow(["students", len(gradebook.students)])
        writer.writerow(["courses", len(gradebook.courses)])
        writer.writerow(["grades", len(gradebook.grades)])
        writer.writerow([])
        writer.writerow(["Top Students", "average_pct"])
        for student, avg in gradebook.top_students():
            writer.writerow([student.full_name, f"{avg:.1f}"])
        writer.writerow([])
        writer.writerow(["Students at risk"])
        for student, avg in gradebook.students_at_risk():
            writer.writerow([student.full_name, f"{avg:.1f}"])
        return buf.getvalue()
