from abc import ABC, abstractmethod

from grade_management.student import Student
from grade_management.course import Course
from grade_management.grade import Grade

class GradeStore(ABC):
    """
    Interface for storing gradebook data.
    """

    # --- Add methods --- #
    @abstractmethod
    def add_student(self, student: Student) -> None:
        ...

    @abstractmethod
    def add_course(self, course: Course) -> None:
        ...

    @abstractmethod
    def record_grade(self, grade: Grade) -> None:
        ...


    # --- Get methods --- #
    @abstractmethod
    def get_student(self, student_id: str) -> Student | None:
        ...    

    @abstractmethod
    def get_course(self, course_id: str) -> Course | None:
        ...

    @abstractmethod
    def get_student_grades(self, student_id: str) -> list[Grade]:
        ... 

    @abstractmethod
    def get_all_grades(self) -> list[Grade]:
        ...

    @abstractmethod
    def get_all_students(self) -> list[Student]:
        ...

    @abstractmethod
    def get_all_courses(self) -> list[Course]:
        ...


    # --- Updates --- #
    @abstractmethod
    def update_student(self, student: Student) -> None:
        ...

    @abstractmethod
    def update_course(self, course: Course) -> None:
        ...
    
    @abstractmethod
    def update_grade(self, grade: Grade) -> None:
        ...

    
    # --- Delete --- #
    @abstractmethod
    def delete_student(self, student: Student) -> None:
        ...

    @abstractmethod
    def delete_course(self, course: Course) -> None:
        ...

    @abstractmethod
    def delete_grade(self, grade: Grade) -> None:
        ...