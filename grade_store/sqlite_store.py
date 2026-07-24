import sqlite3

from grade_db.student_repository import StudentRepository
from grade_db.course_repository import CourseRepository
from grade_db.grade_repository import GradeRepository, GradeRecord

from grade_db.statistics_repository import StatisticsRepository

from grade_store.grade_store import GradeStore

from grade_management.student import Student
from grade_management.course import Course
from grade_management.grade import Grade


class SqliteGradeStore(GradeStore):

    def __init__(
            self,
            student_repo: StudentRepository,
            course_repo: CourseRepository,
            grade_repo: GradeRepository,
            statistics_repo: StatisticsRepository
        ):
        self.student_repo = student_repo
        self.course_repo = course_repo
        self.grade_repo = grade_repo
        self.stats_repo = statistics_repo

    
    def add_student(self, student: Student) -> None:
        self.student_repo.add(student)
        

    def add_course(self, course: Course) -> None:
        self.course_repo.add(course)

    def record_grade(self, grade: Grade) -> None:
        self.grade_repo.add(grade)

    def get_student(self, student_id: str) -> Student | None:
        return self.student_repo.get_by_id(student_id)
    
    def get_course(self, course_id: str) -> Course | None:
        return self.course_repo.get_by_id(course_id)
    
    def get_all_students(self) -> list[Student]:
        return self.student_repo.get_all()
    
    def get_all_courses(self) -> list[Course]:
        return self.course_repo.get_all()   
    
    def get_student_grades(self, student_id: str) -> list[Grade]:
        # New version: Object is build in repo
        return self.grade_repo.get_by_student_with_details(student_id)
    
    def get_course_grades(self, course_id: str) -> list[Grade]:
        # New version: Object is build in repo
        return self.grade_repo.get_by_course_with_details(course_id)
    
    def get_all_grades(self) -> list[Grade]:
        return self.grade_repo.get_all_with_details()
    
    def get_grade_by_id(self, grade_id: str) -> Grade | None:
        return self.grade_repo.get_grade_by_id(grade_id)
    

    # --- Updates --- #
    def update_course(self, course: Course) -> None:
        return self.course_repo.update(course)
    
    def update_student(self, student: Student) -> None:
        return self.student_repo.update(student)
    

    def update_grade(self, grade: Grade) -> None:
        record = GradeRecord.from_grade(grade)
        self.grade_repo.update(record)


    # --- Deletes --- #
    def delete_course(self, course: Course) -> None:
        return self.course_repo.delete(course)

    def delete_student(self, student: Student) -> None:
        return self.student_repo.delete(student)       
    
    
    def delete_grade(self, grade: Grade) -> None:
        record = GradeRecord.from_grade(grade)
        self.grade_repo.delete(record)
        
    # ==========================
    # Statistical Methods
    # ==========================

    def get_student_average(self, student_id):
        return self.stats_repo.average_grade_by_student(student_id)


    def get_student_courses(self, student_id):
        return self.stats_repo.courses_by_student(student_id)