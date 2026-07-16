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
    
    