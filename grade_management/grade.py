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
    pass






def main():
    g = Grade(Student("001","Thomas", "Brockt","sdf"), Course("101", "QM1"), 75, "01.07.2026", "some note")
    print(g.letter_grade)
    




if __name__ == "__main__":
    main()