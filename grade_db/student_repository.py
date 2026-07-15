import sqlite3
from grade_management.student import Student


# --- Students --- #
class StudentRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection


    def create_table(self):
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS students(
                    student_id TEXT PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT NOT NULL
                )"""
            )


    def add(self, student: Student) -> None:
        """Saves a student object into students table."""
        with self.conn:
            self.conn.execute(
                """
                    INSERT INTO students(
                    student_id, 
                    first_name, 
                    last_name, 
                    email
                ) 
                VALUES(?, ?, ?, ?)
                """,
                (
                    student.student_id, 
                    student.first_name, 
                    student.last_name, 
                    student.email
                )
            )
        


    def get_by_id(self, student_id: str) -> Student | None:
        """Type in a student_id and get the corresponding student object back."""
        row = self.conn.execute(
            """
            SELECT
                student_id,
                first_name,
                last_name,
                email
            FROM students 
            WHERE student_id = ?
            """, 
            (student_id,)
        ).fetchone()
        if row is None:
            return None
        return Student(*row)


    def get_all(self) -> list[Student]:
        """Returns a list of all students from the database"""
        rows = self.conn.execute(
            """
            SELECT
                student_id,
                first_name,
                last_name,
                email 
            FROM students
            """
              )
        return [Student(*row) for row in rows]


    def update(self, student: Student) -> None:
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
                (
                    student.first_name, 
                    student.last_name, 
                    student.email,
                    student.student_id
                    ),
            )

            if cursor.rowcount == 0:
                raise ValueError("Student not found")
            
    
    def delete(self, student: Student) -> None:
        """Deletes one Student from the database."""
        with self.conn:
            cursor = self.conn.execute(
                """
                DELETE FROM students 
                WHERE student_id = ?
                """,
                (student.student_id,),
            )
            if cursor.rowcount == 0:
                raise ValueError("Student not found")


 