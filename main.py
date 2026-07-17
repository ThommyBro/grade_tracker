from sample_data import (
    create_test_data,
    populate_gradebook,
    populate_database,
)

from grade_management.gradebook import GradeBook

from grade_db.connection import create_connection

from grade_db.student_repository import StudentRepository
from grade_db.course_repository import CourseRepository
from grade_db.grade_repository import GradeRepository
from grade_db.statistics_repository import StatisticsRepository



# =============================
#    Database Stuff
# =============================

def setup_database():
    """Create all repos and tables in DB."""

    # Create database connection in Grade_Tracker path
    # Creates 'grade.db' file, if it not exists
    con = create_connection()

    # Create repositories
    student_repo = StudentRepository(con)
    course_repo = CourseRepository(con)
    grade_repo = GradeRepository(con)
    stats_repo = StatisticsRepository(con)

    # Create database tables
    student_repo.create_table()
    course_repo.create_table()
    grade_repo.create_table()

    return (
                con,
                student_repo,
                course_repo,
                grade_repo,
                stats_repo
            )


def load_sample_data(student_repo, course_repo, grade_repo, stats_repo):

    # Load all data from sampla_data
    data = create_test_data()

    # Fill in data to database
    populate_database(student_repo, course_repo, grade_repo, data)



# =============================
#    Python Stuff
# =============================
def setup_gradebook(data):

    # Create gradebook
    gbook = GradeBook()

    # Fill in sample data to gradebook
    populate_gradebook(gbook, data)

    return gbook



def main():

    # Create sample Data
    data = create_test_data()

    # ==================== #
    # --- Database side ---# 
    # ==================== #

    # Extract Data from setup_database
    (con, student_repo, course_repo, grade_repo, stats_repo) = setup_database()
    
    # Load all extracted data to fill database with sample data
    load_sample_data(student_repo, course_repo, grade_repo, stats_repo)

    print("\nSQL statistics:")
    print(stats_repo.average_per_student())



    # =================== #
    # --- Python side --- #
    # =================== #

    gbook = setup_gradebook(data)   

    print("\nPython statistics:")
    print(gbook.all_student_averages())


 

    # Close Connection
    con.close()





# ====== Call MAIN ====== #
if __name__ == "__main__":
    main()