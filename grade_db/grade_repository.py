import sqlite3
from dataclasses import dataclass

from grade_management.student import Student
from grade_management.course import Course
from grade_management.grade import Grade
#from grade_db.connection import create_connection



 


# --- Auxillary dataclasses --- #
@dataclass
class GradeRecord:
    """Only to keep repos seperated, so the GradeRepo can return this object."""
    student_id: str
    course_id: str
    score: float
    date: str
    notes: str
    id: int | None = None

    @classmethod
    def from_grade(cls, grade: Grade):
        return cls(
            id = None,
            student_id=grade.student.student_id,
            course_id=grade.course.course_id,
            score=grade.score,
            date=grade.date,
            notes=grade.notes
        )
    
    
    

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
    

    def get_grade_by_id(self, grade_id: int) -> Grade | None:

        row = self.conn.execute(
            """
            SELECT
                -- Student
                students.student_id,
                students.first_name,
                students.last_name,
                students.email,

                -- Course
                courses.course_id,
                courses.name,
                courses.max_grade,
                courses.passing_grade,

                -- Grade
                grades.score,
                grades.date,
                grades.notes,
                grades.id

            FROM grades

            JOIN students
                ON grades.student_id = students.student_id

            JOIN courses
                ON grades.course_id = courses.course_id

            WHERE grades.id = ?
            """,
            (grade_id,)
        ).fetchone()

        if row is None:
            return None

        student = Student(
            row[0],
            row[1],
            row[2],
            row[3]
        )

        course = Course(
            row[4],
            row[5],
            row[6],
            row[7]
        )

        return Grade(
            student=student,
            course=course,
            score=row[8],
            date=row[9],
            notes=row[10],
            id=row[11]
        )


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
                    score = ? ,
                    notes = ? 
                WHERE student_id = ?
                AND course_id = ?
                AND date = ?
                """,
                (
                    graderecord.score, 
                    graderecord.notes,
                    graderecord.student_id,
                    graderecord.course_id,
                    graderecord.date
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
                WHERE student_id = ?
                AND course_id = ?
                AND date = ?
                """,
                (graderecord.student_id,
                 graderecord.course_id,
                 graderecord.date),
            )
            if cursor.rowcount == 0:
                raise ValueError("Graderecord not found")
        # print(f"Cursor rowcount: {cursor.rowcount}") # just for debugging
            

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
    

    def get_by_course(self, course_id: str) -> list[GradeRecord]:
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
            WHERE course_id = ?
            """,
            (course_id,)
        )
        return [GradeRecord(*row) for row in rows]
    

    def get_all_with_details(self) -> list[Grade]:

        rows = self.conn.execute(
        """
        SELECT
            -- Student
            students.student_id,
            students.first_name,
            students.last_name,
            students.email,

            -- Course
            courses.course_id,
            courses.name,
            courses.max_grade,
            courses.passing_grade,

            -- Grade
            grades.score,
            grades.date,
            grades.notes,
            grades.id

        FROM grades
        JOIN students
            ON grades.student_id = students.student_id
        JOIN courses
            ON grades.course_id = courses.course_id
        """
        )

        grades = []

        for row in rows:

            student = Student(
                row[0],
                row[1],
                row[2],
                row[3]
            )

            course = Course(
                row[4],
                row[5],
                row[6],
                row[7]
            )

            grade = Grade(
                student=student,
                course=course,
                score=row[8],
                date=row[9],
                notes=row[10],
                id=row[11]
            )

            grades.append(grade)

        return grades
    

    def get_by_student_with_details(self, student_id: str) -> list[Grade]:

        rows = self.conn.execute(
        """
        SELECT
            -- Student
            students.student_id,
            students.first_name,
            students.last_name,
            students.email,

            -- Course
            courses.course_id,
            courses.name,
            courses.max_grade,
            courses.passing_grade,

            -- Grade
            grades.score,
            grades.date,
            grades.notes

        FROM grades
        JOIN students
            ON grades.student_id = students.student_id
        JOIN courses
            ON grades.course_id = courses.course_id
        WHERE grades.student_id = ?
        """,
            (student_id,)
        )

        grades = []

        for row in rows:

            student = Student(
                row[0],
                row[1],
                row[2],
                row[3]
            )

            course = Course(
                row[4],
                row[5],
                row[6],
                row[7]
            )

            grade = Grade(
                student=student,
                course=course,
                score=row[8],
                date=row[9],
                notes=row[10]
                
            )

            grades.append(grade)

        return grades
    

    def get_by_course_with_details(self, course_id: str) -> list[Grade]:

        rows = self.conn.execute(
        """
        SELECT
            -- Student
            students.student_id,
            students.first_name,
            students.last_name,
            students.email,

            -- Course
            courses.course_id,
            courses.name,
            courses.max_grade,
            courses.passing_grade,

            -- Grade
            grades.score,
            grades.date,
            grades.notes

        FROM grades
        JOIN students
            ON grades.student_id = students.student_id
        JOIN courses
            ON grades.course_id = courses.course_id
        WHERE grades.course_id = ?
        """,
            (course_id,)
        )

        grades = []

        for row in rows:

            student = Student(
                row[0],
                row[1],
                row[2],
                row[3]
            )

            course = Course(
                row[4],
                row[5],
                row[6],
                row[7]
            )

            grade = Grade(
                student=student,
                course=course,
                score=row[8],
                date=row[9],
                notes=row[10]
            )

            grades.append(grade)

        return grades

    





