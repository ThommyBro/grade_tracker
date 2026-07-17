import sqlite3
from grade_management.course import Course




# --- Courses --- #
class CourseRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def create_table(self):
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS courses(
                    course_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    max_grade REAL NOT NULL DEFAULT 100.0,
                    passing_grade REAL NOT NULL DEFAULT 50.0
                )
                """
            )
    def course_exists(self, course_id: str) -> bool:
            """Checks if course_id is already known"""
            row = self.conn.execute(
                """
                SELECT 1
                FROM courses
                WHERE course_id = ?
                """,
                (course_id,)
            ).fetchone()
            return row is not None

    def add(self, course: Course) -> None:
        """
        Saves a course object into courses table.
        If Course is known it will be skipped.
        """

        if self.course_exists(course.course_id):
            return 

        with self.conn:
            self.conn.execute(
                """
                    INSERT INTO courses(
                    course_id, 
                    name, 
                    max_grade, 
                    passing_grade
                ) 
                VALUES(?, ?, ?, ?)
                """,
                (
                    course.course_id,
                    course.name,
                    course.max_grade,
                    course.passing_grade
                )
            )
        


    def get_by_id(self, course_id: str) -> Course | None:
        """Type in a course_id and get the corresponding course object back."""
        row = self.conn.execute(
            """
            SELECT 
                course_id,
                name,
                max_grade,
                passing_grade 
            FROM courses 
            WHERE course_id = ?
            """, 
            (course_id,)
        ).fetchone()
        if row is None:
            return None
        return Course(*row)


    def get_all(self) -> list[Course]:
        """Returns a list of all courses from the database"""
        rows = self.conn.execute(
            """
            SELECT
                course_id,
                name,
                max_grade,
                passing_grade
            FROM courses
            """
              )
        return [Course(*row) for row in rows]


    def update(self, course: Course) -> None:
        """Updates courses database entry if it exists."""
        with self.conn:
            cursor = self.conn.execute(
                """
                UPDATE courses 
                SET 
                    name = ? ,
                    max_grade = ? ,
                    passing_grade = ? 
                WHERE course_id = ?
                """,
                (
                    course.name,
                    course.max_grade,
                    course.passing_grade,
                    course.course_id
                    ),
            )

            if cursor.rowcount == 0:
                raise ValueError("Course not found")
            
    
    def delete(self, course: Course) -> None:
        """Deletes one Course from the database."""
        with self.conn:
            cursor = self.conn.execute(
                """
                DELETE FROM courses 
                WHERE course_id = ?
                """,
                (course.course_id,),
            )
            if cursor.rowcount == 0:
                raise ValueError("Course not found")


 