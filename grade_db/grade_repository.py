import sqlite3

from grade_management.course import Course
from grade_management.student import Student
from grade_management.grade import Grade
 





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
                FOREIGN KEY (course_id) REFERENCES courses(course_id)
                )"""
            )


    def add(self, id: int, student_id: str, course_id: str, score: float, date: str = '', notes: str = '') -> Grade:
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO grades(id, student_id, course_id, score, date, notes) VALUES(?, ?, ?, ?, ? ,?)",
                (id, student_id, course_id, score, date, notes)
            )
        assert cursor.lastrowid is not None, "Failed to insert grade"
        #return Grade(student_id, course_id, score, date, notes)


    def get_by_id(self, id: int) -> Grade | None:
        row = self.conn.execute(
            "SELECT * FROM grades WHERE id = ?", 
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