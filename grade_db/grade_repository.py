import sqlite3
from dataclasses import dataclass

from grade_management.grade import Grade
from grade_db.connection import create_connection
 


# --- Auxillary dataclasses --- #
@dataclass
class GradeRecord:
    """Only to keep repos seperated, so the GradeRepo can return this object."""
    id: int
    student_id: str
    course_id: str
    score: float
    date: str
    notes: str

# --- Grading --- #
class GradeRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def create_table(self):
        with self.conn:
            self.conn.execute(
                """
                    CREATE TABLE IF NOT EXISTS grades(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        course_id TEXT NOT NULL,
                        score REAL NOT NULL,
                        date TEXT NOT NULL,
                        notes TEXT DEFAULT NULL,
                    FOREIGN KEY (student_id) REFERENCES students(student_id),
                    FOREIGN KEY (course_id) REFERENCES courses(course_id)
                )"""
            )


    def grade_exists(self, grade: Grade) -> bool:
        """
        Define two grades to be the same when: same student_id, same course_id and same date.
        """
        row = self.conn.execute(
            """
            SELECT 1 
            FROM grades
            WHERE student_id = ? AND course_id = ? AND date = ?
            """,
            (
                grade.student.student_id, 
                grade.course.course_id, 
                grade.date
            )
        ).fetchone()

        return row is not None


    def add(self, grade: Grade) -> None:
        
        # Check if grade is known
        if self.grade_exists(grade):
            return 
        

        with self.conn:
            self.conn.execute(
                """
                INSERT INTO grades(
                    student_id, 
                    course_id, 
                    score, 
                    date, 
                    notes
                ) 
                VALUES(?, ?, ?, ?, ?)
                """,
                (
                    grade.student.student_id, 
                    grade.course.course_id, 
                    grade.score, 
                    grade.date, 
                    grade.notes
                )
            )
        
        


    def get_by_id(self, grade_id: int) -> GradeRecord | None:
        row = self.conn.execute(
            """
            SELECT 
                id,
                student_id,
                course_id,
                score,
                date,
                notes 
            FROM grades 
            WHERE id = ?
            """, 
            (grade_id,)
        ).fetchone()
        if row is None:
            return None
        return GradeRecord(*row)


    def get_all(self) -> list[GradeRecord]:
        rows = self.conn.execute(
            """
            SELECT 
                id,
                student_id,
                course_id,
                score,
                date,
                notes 
            FROM grades
            """
            )
        return [GradeRecord(*row) for row in rows]


    def update(self, graderecord: GradeRecord) -> None:
        with self.conn:
            cursor = self.conn.execute(
                """
                UPDATE grades 
                SET 
                    student_id = ? ,
                    course_id = ? ,
                    score = ? ,
                    date = ? ,
                    notes = ? 
                WHERE id = ?
                """,
                (
                    graderecord.student_id, 
                    graderecord.course_id, 
                    graderecord.score, 
                    graderecord.date, 
                    graderecord.notes,
                    graderecord.id
                ),
            )
            if cursor.rowcount == 0:
                raise ValueError("Graderecord not found")
            
    
    def delete(self, graderecord: GradeRecord) -> None:
        """Deletes one graderecord from the database."""
        with self.conn:
            cursor = self.conn.execute(
                """
                DELETE FROM grades 
                WHERE id = ?
                """,
                (graderecord.id,),
            )
            if cursor.rowcount == 0:
                raise ValueError("Graderecord not found")
            

    def get_by_student(self, student_id: str) -> list[GradeRecord]:
        rows = self.conn.execute(
            """
                SELECT 
                id,
                student_id,
                course_id,
                score,
                date,
                notes
                FROM grades
                WHERE student_id = ?
            """,
            (student_id,)
        )
        return [GradeRecord(*row) for row in rows]




