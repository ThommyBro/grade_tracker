import sqlite3


# --- Statistics --- #
class StatisticsRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def average_grade_by_course(self):
        rows = self.conn.execute(
            """
            SELECT 
                course_id,
                AVG(score)
            FROM grades
            GROUP BY course_id
            """
            )
        
        # return a dict with course_id keys and average scores as values
        return {
            course_id: round(avg,2)
            for course_id, avg in rows
            }
    
    
    def count_students_per_course(self):
        rows = self.conn.execute(
            """
            SELECT
                course_id,
                COUNT(DISTINCT student_id)
            FROM grades
            GROUP BY course_id
            """
        )

        return rows.fetchall()
    

    def average_per_student(self):
        rows = self.conn.execute(
            """
            SELECT 
                student_id,
                AVG(score)
            FROM grades
            GROUP BY student_id
            """
            )
        
        # return a dict with student_id keys and average scores as values
        return {
            student_id: round(avg,2)
            for student_id, avg in rows
            }
    

    def best_students(self):
        rows = self.conn.execute(
            """
            SELECT
                student_id,
                AVG(score) AS average_score
            FROM grades
            GROUP BY student_id
            ORDER BY average_score DESC
            LIMIT 5
            """
        )
        # return a dict with student_id keys and average scores as values
        return {
            student_id: round(avg,2)
            for student_id, avg in rows
            }
    
    def max_grade_by_course(self):
        rows = self.conn.execute(
            """
            SELECT
                course_id,
                MAX(score)
            FROM grades
            GROUP BY course_id
            """
        )

        return rows.fetchall()
        
    
    def average_grade_by_student(self, student_id: str):
        row = self.conn.execute(
            """
            SELECT
                AVG(score)
            FROM grades
            WHERE student_id = ?
            """,
            (student_id,)
        ).fetchone()

        if row[0] is None:
            return None

        return round(row[0], 2)
    

    def courses_by_student(self, student_id: str):
        rows = self.conn.execute(
            """
            SELECT DISTINCT
                c.course_id,
                c.name
            FROM grades g
            JOIN courses c
                ON g.course_id = c.course_id
            WHERE g.student_id = ?
            """,
            (student_id,)
        )

        return [
            {
                "course_id": course_id,
                "name": name,
            }
            for course_id, name in rows
        ]
