from dataclasses import dataclass, field
import re
import json
import csv
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
        
    
    def __repr__(self):
        return f"{self.score}, {self.date}, {self.notes}"
        

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

    

    #----------- Basic Methods -----------#

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


    #----------- Statistical Methods -----------#

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

    

    # helper function for all stundent averages

    def all_student_averages(self):
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
        return all_stud_avgs
                                                    

    def top_students(self, n: int):
        """
        Top n students by overall average.
        """
        if n > len(self.students):
            raise ValueError(f"We don't have {n} students.")
        
        # call helper function
        # take top n students by slicing
        return self.all_student_averages()[0:n]
    

    def students_at_risk(self, threshold: int):
        """"
        Students with average below threshold (percentage).
        Uses helper function all_student_averages.
        """
        return [student for student in self.all_student_averages() if student[1] <= threshold ]
    

    #----------- Search Methods -----------#

    def search_students(self, query: str):
        """
        Search Students by Name or Mail.
        Regex search if mailaddress is given, if so, string is generated and compared with known student mail addresses.
        If regex is None, full name search is performed.
        """
        # (...) optional if one skips top level domain part
        regex = r"^\w+@\w+(\.\w+)*$"
        mail_match = re.search(regex, query.strip())
        possible_studis = []
  
        if mail_match:
            # extract string from mail_match with group()
            mail =  mail_match.group().lower()
            for studi in self.students: 
                if mail.lower() in studi.email.lower():
                    possible_studis.append(studi)
            return f"Possible students with mail '{query}' found: \n{possible_studis}"
            
        else:
            for studi in self.students: 
                if query.lower() in studi.first_name.lower() or query.lower() in studi.last_name.lower():
                    possible_studis.append(studi)
            return  f"Possible students with name '{query}' found: \n{possible_studis}"
            
        

    def search_course(self, query: str):
        """
        Search Course by name.
        Regex is maximal flexible.
        List of possible matching courses is returned.
        """    
        regex = r"^\w+$"
        course_match = re.search(regex, query.strip())
        possible_courses = []

        if course_match:
            course = course_match.group().lower()
            for subject in self.courses:
                if course in subject.name.lower():
                    possible_courses.append(subject)
            return possible_courses
        return f"No course '{query}' found." 
    



     #----------- JSON Stuff -----------#

    def to_dict(self):
        """
        write a dictionary with students, courses and grades. 
        """
        return {
                "students": [
                    {
                        "student_id": stud.student_id,
                        "first_name": stud.first_name,
                        "last_name": stud.last_name,
                        "email": stud.email
                     }
                     for stud in self.students
                ],
                    "courses": [
                    {
                        "course_id": course.course_id,
                        "name": course.name,
                        "max_grade": course.max_grade,
                        "passing_grade": course.passing_grade
                    }
                    for course in self.courses
                ],
                    "grade": [
                    {
                        "student_id": grade.student.student_id,
                        "course_id": grade.course.course_id,
                        "score": grade.score,
                        "date": grade.date,
                        "notes": grade.notes
                    }
                    for grade in self.grades
                ]
                }


    def save_as_json(self, filename):
        """Saves entire gradebook as json. Just enter a filename e.g. 'my_file.json' """
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)
            


## unnütz?
    def gradebook_serializer(obj):
        if isinstance(obj, Student):
            return {
                        "_type": "student", 
                        "student_id": obj.student_id, 
                        "first_name": obj.first_name, 
                        "last_name": obj.last_name,
                        "email": obj.email
                    }
        elif isinstance(obj, Course):
            pass


    def student_hook(self, d):
        if d.get("_type") == "student":
            return Student(d["student_id"], d["first_name"], d["last_name"], d["email"])
        return d
    
##################
    

   # ------- load JSON --------#
    @classmethod
    def load_from_json(cls, filename):
        """
        Call by g = Gradebook.load_from_json("filename.json")
        Instantiates a new gradebook and load complete data from .json file.
        Returns complete gradebook with all students and courses.
        """
        with open(filename, encoding="utf-8") as f:
            loaded = json.load(f)
        
        # define new gradebook
        gbook = cls()

        # implement students from data
        students = {}
        for s in loaded["students"]: # loaded["students"] = key with value = list of dicts of student attributes
            student = Student(**s)  #  generates Student object with attributes-names from keys and attribute-values from values by **s
            students[student.student_id] = student 
            gbook.add_student(student)

        # implement courses from data
        courses = {}
        for c in loaded["courses"]:
            course = Course(**c)
            courses[course.course_id] = course
            gbook.add_course(course)

        # implement grades with student and course objects
        for g in loaded["grade"]:
            gbook.record_grade(
                student = students[g["student_id"]],
                course = courses[g["course_id"]],
                score = g["score"],
                date = g["date"],
                note = g["notes"]
            )
        
        # return complete gradebook
        return gbook
    

    # ------- CSV Stuff --------#
    def read_csv_grade(self):
        """
        Reads a csv file 'grades.csv' from same directory as this py file.
        Counts and list unknown stundet ids.
        Counts and list unknown course ids.
        If an empty row is found in the csv reading stopps, no error is thrown.
        """
        with open('grades.csv', 'r', newline='', encoding="utf-8") as csvfile:
            grade_reader = csv.reader(csvfile)
        
            # Reading the header
            header = next(grade_reader ) # extract header

            # Dict-comprehension for student ids and course id respectivley for easy search and grading by ids
            known_students = {Student.student_id: Student for Student in self.students}
            known_courses = {Course.course_id: Course for Course in self.courses}

            # initialize counter for unknown students and courses respectively
            unknown_students_count = 0
            unknown_students = []

            unknwon_courses_count = 0
            unknwon_courses = []

            # counter for successful imports and all given rows
            successful = 0
            all_rows = 0

             # Reading each row of the CSV
            for row in grade_reader:
                # if empty line stop reading
                if not row:
                    break
                # if student id is unknown
                elif not row[0] in known_students.keys():
                    unknown_students_count += 1
                    unknown_students.append(row[0])
                # if course id is unknown
                elif not row[1] in known_courses.keys():
                    unknwon_courses_count += 1
                    unknwon_courses.append(row[1])
                # course- and student id are known -> grading will be imported
                else:
                    self.record_grade(known_students[row[0]], known_courses[row[1]],int(row[2]),row[3])
                    successful += 1
                # count +1 for read row
                all_rows += 1

            # print results
            students_result = (
                            f"{unknown_students_count} student ids were not known: {unknown_students}\n"
                            if unknown_students_count > 0 
                            else "all student ids were found.\n"
                        )
            
            courses_result =   (
                            f"{unknwon_courses_count} course ids were not found: {unknwon_courses}\n"
                            if unknown_students_count > 0
                            else "all courses were found.\n"
                        )
            print(
                    f"{successful} / {all_rows} grades successful importet\n"
                    f"{students_result}"
                    f"{courses_result}"
                  )
            







######################## MAIN() ########################
def main():
    #- create gradebook
    gbook = GradeBook()

    #- create students
    s1 = Student("12345","t", "b","some.student@mit.com")
    s2 = Student("23456","a", "b","ab@sample.com")
    s3 = Student("34567","g","z","abc@cba.bac")
    s4 = Student("45678","Anna", "Alpha", "anna@home.de")
    s5 = Student("56789","Benno", "Beta", "benno@home.com")
    s7 = Student("67891","Benno", "der Zweite", "benno.zwei@mail.com")
    s6 = Student("78912","Celine","Gamma","123@test.com")

    #- create courses
    c1 = Course("101", "QM1")
    c2 = Course("102", "Python classics")
    c3 = Course("103","Higher Category Theory", 100.0, 75)
    c4  = Course("104", "QM2", 100, 50)

    #- register students
    gbook.add_student(s1)
    gbook.add_student(s2)
    gbook.add_student(s3)
    gbook.add_student(s4)
    gbook.add_student(s5)
    gbook.add_student(s6)
    gbook.add_student(s7)

    #- register courses
    gbook.add_course(c1)
    gbook.add_course(c2)
    gbook.add_course(c3)
    gbook.add_course(c4)

    #- record grades
    # gbook.record_grade(s1,c1,99,"03.07.2026")
    # gbook.record_grade(s2,c2,50,"03.07.2026")
    # gbook.record_grade(s1,c2,100,"10.06.2026")
    # gbook.record_grade(s3,c2,95)
    # gbook.record_grade(s5,c1,30,"03.07.2026")
    # gbook.record_grade(s4,c3,25,"03.07.2026")
    
    #- print grades, courses, students
    #print(gbook.grades)
    #print(gbook.courses)
    #print(gbook.students)

    #- evaluate individual methods and print results
    #print(gbook.get_student_grades(s1))
    #print(gbook.get_course_grades(c1))
    #print(gbook.student_average("001"))
    #print(gbook.course_average("101"))
    #print(gbook.course_pass_rate("101"))
    #print(gbook.top_students(3))
    #print(gbook.top_students(4))
    #print(gbook.students_at_risk(50))
    #print(gbook.search_students("benno"))
    #print(gbook.search_course("higher"))

    #- save and load json files
    #gbook.save_as_json("gradebook.json")
    #gradebook = GradeBook.load_from_json("gradebook.json")
    
    #- read and write csv files
    gbook.read_csv_grade()
    

 
    
    




if __name__ == "__main__":
    main()