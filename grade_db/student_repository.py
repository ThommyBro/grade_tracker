import sqlite3
from grade_management.student import Student


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

 