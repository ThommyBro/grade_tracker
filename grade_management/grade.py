from dataclasses import dataclass, field
import re
import json
import csv
from pathlib import Path

from grade_management.student import Student 
from grade_management.course import Course



@dataclass
class Grade():
    student: Student
    course: Course
    score: float
    date: str
    notes: str = ""
    
    

    def __post_init__(self):      
        if not 0.0 <= self.score <= self.course.max_grade:
            raise ValueError(
                                f"Score {self.score} out of range "                
                                f"[0, {self.course.max_grade}]"           
                             )
        
    
    def __repr__(self):
        return (
            f"Grade("
            f"student={self.student.student_id}, "
            f"course={self.course.course_id}, "
            f"score={self.score},"
            f"date={self.date}"
            f")"
        )

        
    @property
    def is_passing(self) -> bool:
        if self.score >= self.course.passing_grade:
            return True
        else:
            return False


    @property
    def percentage(self) -> float:
        return round((self.score / self.course.max_grade) * 100, 1)


    @property
    def letter_grade(self) -> str:
        if self.percentage >= 90:
            return "A"
        elif self.percentage >= 80:
            return "B"
        elif self.percentage >= 70:
            return "C"
        elif self.percentage >= 60:
            return "D"
        else:
            return "F"
        

