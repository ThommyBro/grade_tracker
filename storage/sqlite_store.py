import sqlite3
from pathlib import Path
import threading

from grade_management.course import Course
from grade_management.student import Student
from grade_management.grade import Grade
from exceptions import (StudentNotFoundError, CourseNotFoundError, GradeNotFoundError, DuplicateEntryError )


#Should move to app.py
DB_PATH = Path(__file__).parent.parent / "GradeTracker.db"    # creates GradeTracker.db in the same folder as this file (if it not exists)

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS students(
    student_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses(
    course_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    max_grade REAL NOT NULL DEFAULT 100.0,
    passing_grade REAL NOT NULL DEFAULT 50.0
);

CREATE TABLE IF NOT EXISTS grades(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    score REAL NOT NULL,
    date TEXT NOT NULL,
    notes TEXT DEFAULT NULL,
FOREIGN KEY (student_id) REFERENCES students(student_id),
FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
"""



class GradeDataBase:
    
    def __init__(self, path: str | Path = ":memory:"):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(DB_SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()


    @staticmethod
    def _grade_row_id(grade_id: str) -> int:
        """Wandelt eine grade_id (str, z. B. "3") in die interne SQLite-Zeilen-ID (int) um.

        Wir fangen hier absichtlich Fehler ab (z. B. falls grade_id gar
        keine Zahl ist) und werfen stattdessen einheitlich
        GradeNotFoundError – so müssen sich Aufrufer nicht auch noch um
        ValueError/TypeError kümmern, sondern immer nur um EINEN
        Fehlertyp, wenn eine grade_id ungültig ist.
        """
        try:
            return int(grade_id)
        except (TypeError, ValueError):
            raise GradeNotFoundError(grade_id) from None
    # =============================================== #
    #           Students 
    # =============================================== #

    def add_student(self, student: Student) -> None:
        try:
            self.conn.execute(
                "INSERT INTO students (student_id, first_name, last_name, email) "
                "VALUES (?, ?, ?, ?)",
                (student.student_id, student.first_name, student.last_name, student.email),
            )
            self.conn.commit()
        except sqlite3.IntegrityError as exc:
            raise DuplicateEntryError("Student", student.student_id) from exc


    def get_student(self, student_id: str) -> Student:
        row = self.conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
        if row is None:
            raise StudentNotFoundError(student_id)
        return self._row_to_student(row)


    def get_all_students(self) -> list[Student]:
        rows = self.conn.execute("SELECT * FROM students").fetchall()
        return [self._row_to_student(r) for r in rows]


    @staticmethod
    def _row_to_student(row: sqlite3.Row) -> Student:
        return Student(row["student_id"], row["first_name"], row["last_name"], row["email"])


    def update_student(self, student: Student) -> None:
            """Updates student database entry if it exists."""
            with self.conn:
                cursor = self.conn.execute(
                    """
                    UPDATE students 
                    SET 
                        first_name = ? ,
                        last_name = ? ,
                        email = ? 
                    WHERE student_id = ?
                    """,
                    (student.first_name, student.last_name, student.email, student.student_id),
                )
                if cursor.rowcount == 0:
                    raise StudentNotFoundError(student.student_id)

    def delete_student(self, student_id: str) -> None:
            """Deletes one Student from the database."""
            with self.conn:
                self.conn.execute("DELETE FROM grades WHERE student_id = ?",(student_id,)) # Delete Grades first
                cursor = self.conn.execute("DELETE FROM students WHERE student_id = ?",(student_id,),)
                if cursor.rowcount == 0:
                    raise StudentNotFoundError(student_id)


    # =============================================== #
    #           Courses 
    # =============================================== #

    def add_course(self, course: Course) -> None:
        try:
            self.conn.execute(
                "INSERT INTO courses (course_id, name, max_grade, passing_grade) "
                "VALUES (?, ?, ?, ?)",
                (course.course_id, course.name, course.max_grade, course.passing_grade),
            )
            self.conn.commit()
        except sqlite3.IntegrityError as exc:
            raise DuplicateEntryError("Course", course.course_id) from exc

    def get_course(self, course_id: str) -> Course:
        row = self.conn.execute(
            "SELECT * FROM courses WHERE course_id = ?", (course_id,)
        ).fetchone()
        if row is None:
            raise CourseNotFoundError(course_id)
        return self._row_to_course(row)

    def get_all_courses(self) -> list[Course]:
        rows = self.conn.execute("SELECT * FROM courses").fetchall()
        return [self._row_to_course(r) for r in rows]

    @staticmethod
    def _row_to_course(row: sqlite3.Row) -> Course:
        return Course(row["course_id"], row["name"], row["max_grade"], row["passing_grade"])


    
    def update_course(self, course: Course) -> None:
        """Updates courses database entry if it exists."""
        with self.conn:
            cursor = self.conn.execute("""UPDATE courses SET 
                    name = ? ,
                    max_grade = ? ,
                    passing_grade = ? 
                WHERE course_id = ?
                """,
                (course.name, course.max_grade, course.passing_grade, course.course_id),
            )
            if cursor.rowcount == 0:
                raise CourseNotFoundError(course.course_id)
                
        
    def delete_course(self, course_id: str) -> None:
        """Deletes one Course from the database."""
        with self.conn:
            cursor = self.conn.execute("DELETE FROM courses WHERE course_id = ?", (course_id,),)
            if cursor.rowcount == 0:
                raise CourseNotFoundError(course_id)


    # =============================================== #
    #           Grades 
    # =============================================== #

    def add_grade(self, student_id: str, course_id: str, score: float, date: str, notes: str = "") -> Grade:
        # check post_init in grade before we write to the DB
        student = self.get_student(student_id)
        course = self.get_course(course_id)
        grade = Grade(student=student, course=course, score=score, date=date, notes=notes)

        cursor = self.conn.execute(
            "INSERT INTO grades (student_id, course_id, score, date, notes) "
            "VALUES (?, ?, ?, ?, ?)",
            (student_id, course_id, score, date, notes),
        )
        self.conn.commit()
        grade.grade_id = str(cursor.lastrowid)
        return grade

    def get_all_grades(self) -> list[Grade]:
        rows = self.conn.execute("SELECT * FROM grades").fetchall()
        return [self._row_to_grade(r) for r in rows]

    def get_student_grades(self, student_id: str) -> list[Grade]:
        self.get_student(student_id)
        rows = self.conn.execute(
            "SELECT * FROM grades WHERE student_id = ?", (student_id,)
        ).fetchall()
        return [self._row_to_grade(r) for r in rows]

    def get_course_grades(self, course_id: str) -> list[Grade]:
        self.get_course(course_id)
        rows = self.conn.execute(
            "SELECT * FROM grades WHERE course_id = ?", (course_id,)
        ).fetchall()
        return [self._row_to_grade(r) for r in rows]

    def get_grade(self, grade_id: str) -> Grade:
        row_id = self._grade_row_id(grade_id)
        row = self.conn.execute("SELECT * FROM grades WHERE id = ?", (row_id,)).fetchone()
        if row is None:
            raise GradeNotFoundError(grade_id)
        return self._row_to_grade(row)

    def update_grade(self, grade_id: str, score: float, date: str, notes: str = "") -> Grade:
        existing = self.get_grade(grade_id)  # wirft GradeNotFoundError, falls unbekannt

        # Neues Grade-Objekt bauen -> das validiert score/date automatisch
        # über __post_init__, BEVOR wir die Datenbank verändern.
        updated = Grade(
            student=existing.student,
            course=existing.course,
            score=score,
            date=date,
            notes=notes,
            grade_id=grade_id,
        )
        row_id = self._grade_row_id(grade_id)
        self.conn.execute(
            "UPDATE grades SET score = ?, date = ?, notes = ? WHERE id = ?",
            (score, date, notes, row_id),
        )
        self.conn.commit()
        return updated

    def delete_grade(self, grade_id: str) -> None:
        self.get_grade(grade_id)  # wirft GradeNotFoundError, falls unbekannt
        row_id = self._grade_row_id(grade_id)
        self.conn.execute("DELETE FROM grades WHERE id = ?", (row_id,))
        self.conn.commit()

    def _row_to_grade(self, row: sqlite3.Row) -> Grade:
        student = self.get_student(row["student_id"])
        course = self.get_course(row["course_id"])
        return Grade(
            student=student,
            course=course,
            score=row["score"],
            date=row["date"],
            notes=row["notes"],
            grade_id=str(row["id"]),
        )

    
    # =============================================== #
    #           SQL-statistics 
    # =============================================== #

    def course_average_sql(self, course_id: str) -> float:
        self.get_course(course_id)
        row = self.conn.execute(
            "SELECT AVG(score) AS avg_score FROM grades WHERE course_id = ?", (course_id,)
        ).fetchone()
        return row["avg_score"] or 0.0


    def course_pass_rate_sql(self, course_id: str) -> float:
        course = self.get_course(course_id)
        row = self.conn.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN score >= ? THEN 1 ELSE 0 END) AS passing
            FROM grades WHERE course_id = ?
            """,
            (course.passing_grade, course_id),
        ).fetchone()
        if not row["total"]:
            return 0.0
        return row["passing"] / row["total"] * 100


    def grade_counts_per_course(self) -> dict[str, int]:
        rows = self.conn.execute(
            "SELECT course_id, COUNT(*) AS cnt FROM grades GROUP BY course_id"
        ).fetchall()
        return {r["course_id"]: r["cnt"] for r in rows}




