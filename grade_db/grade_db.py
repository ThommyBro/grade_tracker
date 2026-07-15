import sqlite3
from dataclasses import dataclass
from grade_management.course import Course
from grade_management.student import Student
from grade_management.grade import Grade

# ------- Create Connection for all repos ------- #
def create_connection(db_path: str = ":memory:") -> sqlite3.Connection:
    """Create a database connection to in-memory DB for testing"""
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON") 
    return con




# ------- Create Repos  ------- #

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
                max_grade REAL NOT NULL DEFAULT 100.0
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

# --- Students --- #
class StudentRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def create_table(self):
        with self.conn:
            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS students(
                student_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL
                )"""
            )


    def add(self, student_id: str, first_name: str, last_name: str, email: str) -> Student:
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO students(student_id, first_name, last_name, email) VALUES(?, ?, ?, ?)",
                (student_id, first_name, last_name, email)
            )
        assert cursor.lastrowid is not None, "Failed to insert student"
        return Student(str(cursor.lastrowid), first_name, last_name, email)


    def get_by_id(self, student_id: int) -> Student | None:
        row = self.conn.execute(
            "SELECT * FROM students WHERE student_id = ?", 
            (student_id,)
        ).fetchone()
        if row is None:
            return None
        return Student(*row)


    def get_all(self):
        rows = self.conn.execute("SELECT * FROM students")
        return [Student(*row) for row in rows]


    def update(self) -> Student:
        with self.conn:
            self.conn.execute(
                "UPDATE students SET first_name = ? last_name = ? email = ? WHERE student_id = ?",
                (Student.first_name, Student.last_name, Student.email),
            )


# --- Grading --- #
class GradeRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def create_table(self):
        with self.conn:
            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS grades(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_id TEXT NOT NULL,
                score REAL NOT NULL,
                date TEXT NOT NULL,
                notes TEXT DEFAULT '',
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY course_id REFERENCES courses(course_id)
                )"""
            )


    def add(self, id: int, student_id: str, course_id: str, score: float, date: str = '', notes: str = '') -> Grade:
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO grades(id, student_id, student_id, course_id, score, date, notes) VALUES(?, ?, ?, ?, ? ,? ,?)",
                (id, student_id, student_id, course_id, score, date, notes)
            )
        assert cursor.lastrowid is not None, "Failed to insert grade"
        #return Grade(student_id, course_id, score, date, notes)


    def get_by_id(self, id: int) -> Grade | None:
        row = self.conn.execute(
            "SELECT * FROM students WHERE student_id = ?", 
            (id,)
        ).fetchone()
        if row is None:
            return None
        return Grade(*row)


    def get_all(self):
        rows = self.conn.execute("SELECT * FROM grades")
        return [Grade(*row) for row in rows]


    def update(self) -> Grade:
        with self.conn:
            self.conn.execute(
                "UPDATE grades SET student_id = ? student_id = ? course_id = ? score = ? date = ? notes WHERE id = ?",
                (Grade.student, Grade.course, Grade.score, Grade.date, Grade.notes),
            )
