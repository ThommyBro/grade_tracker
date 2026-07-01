from dataclasses import dataclass, field
from student import Student 
from course import Course

@dataclass
class Grade():
    student: Student
    course: Course
    score: float
    date: str
    notes: str = ""
    


    @property
    def is_passing(self):
        pass


    @property
    def percentage(self):
        pass


    @property
    def letter_grade(self):
        pass




@dataclass
class GradeBook:
    pass
