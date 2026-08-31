"""Menschenlesbare Text-Reports."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from reports.base import ReportGenerator

if TYPE_CHECKING:
    from gradebook_new import GradeBook

_LETTERS = ("A", "B", "C", "D", "F")


class TextReportGenerator(ReportGenerator):
    """3 Methods for the reports in a formated TXT format."""

    def generate_student_report(self, student_id: str, gradebook: "GradeBook") -> str:
        student = gradebook.students[student_id]
        grades = gradebook.get_student_grades(student_id)
        

        lines = [f"Grade report: {student.full_name} ({student.student_id})", "=" * 56]
        if not grades:
            lines.append("No grades recorded.")
            return "\n".join(lines)

        lines.append(f"{'Course':<30}{'Score':<25}{'Grade':<20}{'Status':<20}")
        lines.append("-" * 83)
        for g in grades:
            status = "passed" if g.is_passing else "failed"
            score = f"{g.score:.1f}/{g.course.max_grade:.0f}"
            
            lines.append(f"{g.course.name:<30}{score:<25}{g.letter_grade:<20}{status:<20}")
        lines.append("-" * 83)
        lines.append(f"Mean: {gradebook.student_average(student_id):.1f}%")
        return "\n".join(lines)

    def generate_course_report(self, course_id: str, gradebook: "GradeBook") -> str:
        course = gradebook.courses[course_id]
        grades = gradebook.get_course_grades(course_id)

        lines = [f"Course report: {course.name} ({course.course_id})", "=" * 56]
        if not grades:
            lines.append("No grades recorded.")
            return "\n".join(lines)

        lines.append(f"{'Studend':<30}{'Score':>15}{'Grade':>10}")
        lines.append("-" * 56)
        for g in grades:
            points = f"{g.score:.1f}/{course.max_grade:.0f}"
            lines.append(f"{g.student.full_name:<30}{points:>15}{g.letter_grade:>10}")
        lines.append("-" * 56)
        lines.append(f"Course Average: {gradebook.course_average(course_id):.2f}")
        lines.append(f"Passing Rate:      {gradebook.course_pass_rate(course_id):.1f}%")

        distribution = Counter(g.letter_grade for g in grades)
        dist_str = "   ".join(f"{letter}: {distribution.get(letter, 0)}" for letter in _LETTERS)
        lines.append(f"Grade distribution:     {dist_str}")
        return "\n".join(lines)

    def generate_summary_report(self, gradebook: "GradeBook") -> str:
        lines = ["Overview", "=" * 56]
        lines.append(f"{'Students:':15} {len(gradebook.students)}")
        lines.append(f"{'Courses:':15}  {len(gradebook.courses)}")
        lines.append(f"{'Grades:':15}   {len(gradebook.grades)}")
        lines.append("")
            #print(f"{product:<{width}} -> {location}")
        lines.append("Top Students:")
        top = gradebook.top_students()
        if not top:
            lines.append("  (No Data)")
        for student, avg in top:
            lines.append(f"  {student.full_name:30}     {avg:>10.1f}%")

        lines.append("")
        lines.append("Students at risk (< 60 %):")
        at_risk = gradebook.students_at_risk()
        if not at_risk:
            lines.append("  (no)")
        for student, avg in at_risk:
            lines.append(f"  {student.full_name:30}    {avg:>10.1f}")

        return "\n".join(lines)
