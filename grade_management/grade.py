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
        



##################### GRADEBOOK #####################

@dataclass
class GradeBook:
    students: list = field(default_factory=list)
    courses: list = field(default_factory=list)
    grades: list = field(default_factory=list)
    course_grades: dict = field(default_factory=dict)
    top_students_all: dict = field(default_factory=dict)
    top_n_students: tuple = field(default_factory=tuple)

    


    def add_student(self, student: Student):
        """
        Creates set of existing student ids.
        Checks new student against this set. Appends student list if id is not exiting.
        """
        if not student in self.students:
            self.students.append(student)
        else:
            raise ValueError(f"Student {student.full_name} already exists.")


    def add_course(self, course: Course):
        """
        Creates set of existing course ids.
        Checks new course against this set. Appends courses list if id is not exiting.
        """
        if not course in self.courses:
            self.courses.append(course)
        else:
            raise ValueError(f"Course {course.name} already exists.")
        

    def record_grade(self, student: Student, course: Course, score=0, date="", note=""):
        """
        Creates Grade Object.
        Checks if stundent and course exists.
        If so, appends list of grades with new Grade obejct. 
        """
        grade = Grade(student, course, score, date, note)
        # use __eq__ of student and course!
        if student in self.students and course in self.courses:
            self.grades.append(grade)
        else:
            raise ValueError(f"Check if student and course exists.")
        

    def get_student_grades(self, student: Student):
        """
        Returns  dict of course names with corresponding grades (percentages and letters).
        """
        return {grade.course.name: (grade.percentage, grade.letter_grade) for grade in self.grades if grade.student == student}
    

    def get_course_grades(self, course: Course):
        """
        Updates course_grades dict with corresponding course and returns a sorted dict with:
        keys = letter_grades
        values = list of students + percentages
        """
        for grade in self.grades:
            if grade.course == course:
                self.course_grades.setdefault(grade.letter_grade, []).append(grade.student.full_name + " " + '('+(str(grade.percentage))+' %)')
        return {k: v for k, v in sorted(self.course_grades.items(), key=lambda item: item[0])}


    def student_average(self, studentID: str):
        """
        Checks if student exists.
        Average percentage across all courses.
        returns float in intervall [0.0, 1.0]
        """
        total = 0
        count = 0
        for grade in self.grades:
            if studentID == grade.student.student_id:
                total += grade.percentage
                count += 1
        return (
                round(total/count,1) if count > 0
                else f"Student {studentID} has no courses finished."
                )

            

    def course_average(self, courseID: str):
        """
        Checks if course exists.
        Average score for a course.
        returns float in intervall  [0.0, 100.0]
        """
        total = 0
        count = 0
        for grade in self.grades:
            if courseID == grade.course.course_id:
                total += grade.percentage
                count += 1
        return (
                round(total/count,1) if count > 0
                else f"Course {courseID} has no participants."
                )
   
            

    def course_pass_rate(self, courseID: str):
        """
        Checks if course exists.
        Percentages of passing grades.
        returns float in intervall [0.0, 1.0]
        """
        all_participants, all_passers = 0, 0
        
        for grade in self.grades:
            if courseID == grade.course.course_id:
                all_participants += 1
                if grade.is_passing: all_passers += 1
        return (
                round(all_passers/all_participants,1) if all_participants > 0 
                else f"Course does not exist."
                )

        

    def top_students(self, n: int):
        """
        Top n students by overall average.
        """
        if n > len(self.students):
            raise ValueError(f"We don't have {n} students.")
        
        for grade in self.grades:
            stud_avg = self.student_average(grade.student.student_id)
            stud_name = grade.student.full_name

            # create dict with student names as keys and their overall averages as values
            self.top_students_all.setdefault(stud_name, stud_avg)

        # temp dict with all students and average grades
        # sort by value = average percentage then reverse to get high to low ordering
        # make a tuple
        all_stud_avgs = tuple({k: v for k, v in sorted(self.top_students_all.items(), 
                                                       key=lambda item: item[1], 
                                                       reverse=True)}.items()
                             )
        # take top n students by slicing
        return all_stud_avgs[0:n]
        








######################## MAIN() ########################
def main():
    s1 = Student("001","t", "b","some@mit.com")
    c1 = Course("101", "QM1")
    g1 = Grade(s1,c1, 100, "01.07.2026", "some note")
    s2 = Student("002","a", "b","ab@sample.com")
    s3 = Student("003", "g","z","abc@cba.bac")
    s4 = Student("004","Anna", "Alpha", "anna@home.de")
    s5 = Student("005", "Benno", "Beta", "benno@home.com")
    c2 = Course("102", "Python classics")
    c3 = Course("103","Higher Category Theory", 100.0, 75)
    #print(f"Letter-Grade: {g1.letter_grade}")
    #print(f"Pass: {g1.is_passing}")
    #print(s1)
    gbook = GradeBook()
    gbook.add_student(s1)
    gbook.add_student(s2)
    gbook.add_course(c1)
    gbook.add_student(s3)
    gbook.add_student(s4)
    gbook.add_student(s5)
    gbook.add_course(c2)
    gbook.add_course(c3)
    gbook.record_grade(s1,c1,99,"03.07.2026")
    gbook.record_grade(s2,c2,50,"03.07.2026")
    gbook.record_grade(s1,c2,100,"10.06.2026")
    gbook.record_grade(s3,c2,95)
    gbook.record_grade(s5,c1,30,"03.07.2026")
    gbook.record_grade(s4,c3,25,"03.07.2026")
    #gbook.record_grade(Student("007","Thomas","B","some@mail.com"), c1) # student not known
    #gbook.record_grade(s1,Course("123","Category Theory 101"),100) # course not known
    #print(gbook.grades)
    #print(gbook.courses)
    #print(gbook.get_student_grades(s1))
    #print(gbook.get_course_grades(c1))
    #print(gbook.student_average("001"))
    #print(gbook.course_average("101"))
    #print(gbook.course_pass_rate("101"))
    #print(gbook.top_students(3))
    print(gbook.top_students(3))
    
    




if __name__ == "__main__":
    main()