import sqlite3
from grade_management.course import Course




# --- Courses --- #
class CourseRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def create_table(self):
        with self.conn:
            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS courses(
                course_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                max_grade REAL NOT NULL DEFAULT 100.0,
                passing_grade REAL NOT NULL DEFAULT 50.0
                )"""
            )


    def add(self, course_id: str, name: str, max_grade: float = 100.0, passing_grade: float = 50.0) -> Course:
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO courses(course_id, name, max_grade, passing_grade) VALUES(?, ?, ?, ?)",
                (course_id, name, max_grade, passing_grade)
            )
        assert cursor.lastrowid is not None, "Failed to insert course"
        return Course(str(cursor.lastrowid), name, max_grade, passing_grade)


    def get_by_id(self, course_id: int) -> Course | None:
        row = self.conn.execute(
            "SELECT * FROM courses WHERE course_id = ?", 
            (course_id,)
        ).fetchone()
        if row is None:
            return None
        return Course(*row)


    def get_all(self):
        rows = self.conn.execute("SELECT * FROM courses")
        return [Course(*row) for row in rows]


    def update(self) -> Course:
        with self.conn:
            self.conn.execute(
                "UPDATE courses SET name = ? max_grade = ? passing_grade = ? WHERE course_id = ?",
                (Course.name, Course.max_grade, Course.passing_grade),
            )
 