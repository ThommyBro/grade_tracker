
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from exceptions import CourseNotFoundError, StudentNotFoundError
from gradebook_new import GradeBook

_ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class ImportReport:

    imported: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.imported + self.skipped

    def __str__(self) -> str:
        lines = [f"Imported: {self.imported}, Skipped: {self.skipped}"]
        lines.extend(f"  - {err}" for err in self.errors)
        return "\n".join(lines)


# ---------------------------------------------------------------------- #
# JSON: Save/Load complete GradeBook 
# ---------------------------------------------------------------------- #
def save_json(gradebook: GradeBook, path: str | Path) -> None:
    path = Path(path)
    path.write_text(
        json.dumps(gradebook.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_json(path: str | Path) -> GradeBook:
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return GradeBook.from_dict(data)


# ---------------------------------------------------------------------- #
# CSV: Noten importieren/exportieren
# Format: student_id,course_id,score,date[,notes]
# ---------------------------------------------------------------------- #
def import_csv(gradebook: GradeBook, path: str | Path) -> ImportReport:
    """Importes Grades from a CSV-File.

    Invalid lines will be skipped.
    """
    path = Path(path)
    report = ImportReport()
    lines = path.read_text(encoding="utf-8").splitlines()

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.lower().startswith("student_id"):
            continue  # Leerzeilen und Kopfzeile überspringen

        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 4:
            report.skipped += 1
            report.errors.append(f"Line {line_number}: to few fields ('{raw_line}')")
            continue

        student_id, course_id, score_str, date, *rest = parts
        notes = rest[0] if rest else ""

        try:
            score = float(score_str)
        except ValueError:
            report.skipped += 1
            report.errors.append(f"Line {line_number}: invalid score '{score_str}'")
            continue

        if not _ISO_DATE_PATTERN.match(date):
            report.skipped += 1
            report.errors.append(f"Line {line_number}: invalid Date '{date}'")
            continue

        try:
            gradebook.add_grade(student_id, course_id, score, date, notes)
        except (StudentNotFoundError, CourseNotFoundError, ValueError) as exc:
            report.skipped += 1
            report.errors.append(f"Zeile {line_number}: {exc}")
            continue

        report.imported += 1

    return report


def export_csv(gradebook: GradeBook, path: str | Path) -> None:
    path = Path(path)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "course_id", "score", "date", "notes"])
        for g in gradebook.grades:
            writer.writerow(
                [g.student.student_id, g.course.course_id, g.score, g.date, g.notes]
            )
