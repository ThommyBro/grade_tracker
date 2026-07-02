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
    students: list = field(default_factory=list)
    courses: list = field(default_factory=list)


    def add_student(self, student: Student):
        """
        Creates set of existing student ids.
        Checks new student against this set. Appends student list if id is not exiting.
        """
        stud_ids = set()
        for old_student in self.students:
            stud_ids.add(old_student.student_id)
        if not student.student_id in stud_ids:
            self.students.append(student)
        else:
            raise ValueError(f"Student {student.full_name} already exists.")


    def add_course(self, course: Course):
        """
        Creates set of existing course ids.
        Checks new course against this set. Appends courses list if id is not exiting.
        """
        course_ids = set()
        for old_course in self.courses:
            course_ids.add(old_course.course_id)
        if not course.course_id in self.courses:
            self.courses.append(course)
        else:
            raise ValueError(f"Course {course.name} already exists.")






def main():
    s1 = Student("001","t", "b","some@mit.com")
    c1 = Course("101", "QM1")
    g1 = Grade(s1,c1, 100, "01.07.2026", "some note")
    s2 = Student("002","a", "b","ab@sample.com")
    s3 = Student("003", "g","z","abc@cba.bac")
    #print(f"Letter-Grade: {g1.letter_grade}")
    #print(f"Pass: {g1.is_passing}")
    #print(s1)
    gbook = GradeBook()
    gbook.add_student(s1)
    gbook.add_student(s2)
    gbook.add_course(c1)
    #print(gbook)
    gbook.add_student(s3)
    print(gbook)
    
    




if __name__ == "__main__":
    main()