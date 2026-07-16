import sqlite3
from dataclasses import dataclass
from grade_management.course import Course
from grade_management.student import Student
from grade_management.grade import Grade
 


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
                """C
                REATE TABLE IF NOT EXISTS grades(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    score REAL NOT NULL,
                    date TEXT NOT NULL,
                    notes TEXT DEFAULT '',
                    FOREIGN KEY (student_id) REFERENCES students(student_id),
                    FOREIGN KEY (course_id) REFERENCES courses(course_id)
                )"""
            )


    def add(self, student_id: str, course_id: str, score: float, date: str, notes: str = "") -> None:
        with self.conn:
            cursor = self.conn.execute(
                """
                INSERT INTO grades(
                    grade.student.student_id, 
                    grade.course.course_id, 
                    score, 
                    date, 
                    notes
                ) 
                VALUES(?, ?, ?, ?, ?)
                """,
                (
                    student_id, 
                    course_id, 
                    score, 
                    date, 
                    notes
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






def main():
    # Connection creation:                 
    con = create_connection()

    # define all repos
    #course_repo = CourseRepository(con)
    #student_repo = StudentRepository(con)
    #grade_repo = GradeRepository(con)

    # create tables in all repos
    #course_repo.create_table()
    #student_repo.create_table()
    #grade_repo.create_table()

    # Fill in data
    # course_repo.add("101", "Python 101")
    # student_repo.add("1", "Thomas", "Brockt", "@me")
    # grade_repo.add(1,"1", "101", 99.0, "15.07.2026", "Einfach mega der Typ")

    # ask for data
    #print(course_repo.get_by_id("102"))
    #print(grade_repo.get_by_id(1))







# ---- Check for main file ---- #
if __name__ == "__main__":
    main()