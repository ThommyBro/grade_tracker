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


def main():

    # Create sample data
    data = create_test_data()


    # Create GradeBook
    gbook = GradeBook()

    
    # Populate GradeBook
    populate_gradebook(gbook, data)


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


    # Populate database
    populate_database(
        student_repo,
        course_repo,
        grade_repo,
        data,
    )


    # Test output
    print("Students:")
    print(student_repo.get_all())

    print("\nCourses:")
    print(course_repo.get_all())

    print("\nGrades:")
    print(grade_repo.get_all())


    # Close Connection
    con.close()





# ====== Call MAIN ====== #
if __name__ == "__main__":
    main()