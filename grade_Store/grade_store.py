from abc import ABC, abstractmethod

from grade_management.student import Student
from grade_management.course import Course
from grade_management.grade import Grade

class GradeStore(ABC):
    """
    Interface for storing gradebook data.
    """

    @abstractmethod
    def add_student(self, student: Student) -> None:
        pass


    @abstractmethod
    def add_course(self, course: Course) -> None:
        pass


    @abstractmethod
    def record_grade(self, grade: Grade) -> None:
        pass

    
    @abstractmethod
    def get_student(self, student: Student) -> Student:
        pass    

    @abstractmethod
    def get_student_grades(self, student_id: str) -> list[Grade]:
        pass 