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
                COUNT(student_id) AS count
            FROM grades
            GROUP BY course_id
            """
        )

        return {
            course_id: count
            for course_id, count in rows
        }
    

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
            SELECT TOP 5
                student_id,
                AVG(score) AS average_score
            FROM grades
            GROUP BY student_id
            ORDER BY average_score DESC;
            """
        )
        # return a dict with student_id keys and average scores as values
        return {
            student_id: round(avg,2)
            for student_id, avg in rows
            }
        
