import sqlite3

from grade_db.student_repository import StudentRepository
from grade_db.course_repository import CourseRepository
from grade_db.grade_repository import GradeRepository

from grade_store.grade_store import GradeStore

from grade_management.student import Student
from grade_management.course import Course
from grade_management.grade import Grade


class SqliteGradeStore(GradeStore):

    def __init__(
            self,
            student_repo: StudentRepository,
            course_repo: CourseRepository,
            grade_repo: GradeRepository
        ):
        self.student_repo = student_repo
        self.course_repo = course_repo
        self.grade_repo = grade_repo

    
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
    
    # Old version: Object is build here
        # student = self.student_repo.get_by_id(student_id)
        # if student is None:
        #     return []
        
        # records = self.grade_repo.get_by_student(student_id)
        # grades = []
        # for record in records:
        #     course = self.course_repo.get_by_id(record.course_id)
        #     if course is None:
        #         raise ValueError(f"Course {record.course_id} not found.")

        #     grade = Grade(
        #                     student = student,
        #                     course = course,
        #                     score = record.score,
        #                     date = record.date,
        #                     notes = record.notes
        #                 )
        #     grades.append(grade)

        # return grades
    

    def get_course_grades(self, course_id: str) -> list[Grade]:
        # New version: Object is build in repo
        return self.grade_repo.get_by_course_with_details(course_id)
    
        # Old version
        # course = self.course_repo.get_by_id(course_id)
        # if course is None:
        #     raise ValueError(f"Course {course_id} not found.")
        
        # records = self.grade_repo.get_by_course(course_id)
        # grades = []
        # for record in records:
        #     student = self.student_repo.get_by_id(record.student_id)
        #     if student is None:
        #         raise ValueError(f"Stundent {record.student_id} not found")
            
        #     grade = Grade(
        #                     student= student,
        #                     course= course,
        #                     score= record.score,
        #                     date= record.date,
        #                     notes= record.notes
        #                 )
        #     grades.append(grade)
        # return grades
    

    def get_all_grades(self) -> list[Grade]:
        return self.grade_repo.get_all_with_details()
    

    # --- Updates --- #
    def update_course(self, course: Course) -> None:
        return self.course_repo.update(course)
    
    def update_student(self, student: Student) -> None:
        return self.student_repo.update(student)
    

    def update_grade(self, grade: Grade) -> None:
        ...
    #    return self.grade_repo.update(grade)
    # needs handling bc of grade obejcts in grade_repo


    # --- Deletes --- #
    def delete_course(self, course: Course) -> None:
        return self.course_repo.delete(course)

    def delete_student(self, student: Student) -> None:
        return self.student_repo.delete(student)       
    
    # don't know GradeRecord/Grade
    def delete_grade(self, grade: Grade) -> None:
        ...
    #    return self.grade_repo.delete(?)