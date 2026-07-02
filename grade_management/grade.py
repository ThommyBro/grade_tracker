from dataclasses import dataclass
from student import Student 
from course import Course

@dataclass
class Grade():
    student: Student
    course: Course
    score: float
    date: str
    notes: str = ""
    

    def __post_init__(self):      
        if not 0 <= self.score <= self.course.max_grade:
            raise ValueError(f"Score {self.score} out of range "                
                             f"[0, {self.course.max_grade}]"           
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
        




@dataclass
class GradeBook:
    
    def add_student(self):
        pass


    def add_course(self):
        pass






def main():
    s = Student("001","Thomas", "Brockt","sdf")
    c = Course("101", "QM1")
    g = Grade(s,c, 100, "01.07.2026", "some note")
    print(g.letter_grade)
    print(g.is_passing)
    
    




if __name__ == "__main__":
    main()