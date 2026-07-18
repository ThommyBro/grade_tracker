from grade_management.gradebook import GradeBook
from grade_management.student import Student
from grade_management.course import Course
from grade_management.grade import Grade

from grade_store.grade_store import GradeStore


class InMemoryGradeStore(GradeStore):
    """
    Uses the gradebook dataclass. Easy for testing and no persistent data storage.
    """

    def __init__(self):
        self.gradebook = GradeBook()

    
    # --- Add --- #
    def add_student(self, student: Student) -> None:
        self.gradebook.add_student(student)

    def add_course(self, course: Course) -> None:
        self.gradebook.add_course(course)
    
    def record_grade(self, grade: Grade) -> None:
        self.gradebook.record_grade(
            grade.student,
            grade.course,
            grade.score,
            grade.date,
            grade.notes
        )


    # --- Get --- #
    def get_student_grades(self, student_id: str) -> list[Grade]:
        # next stopps at first encounter
        student = next((s for s in self.gradebook.students if student_id == s.student_id), None)
        if student is None:
            return []
        
        return [grade for grade in self.gradebook.grades if grade.student == student]
    

    def get_student(self, student_id: str) -> Student | None:
        return next((s for s in self.gradebook.students if student_id == s.student_id), None)
        
    
    def get_course(self, course_id: str) -> Course | None:
        return next((c for c in self.gradebook.courses if course_id == c.course_id), None)
        

    def get_all_grades(self) -> list[Grade]:
        return self.gradebook.grades.copy()     # return only a copy of the list, so the original can't be manipulated
    

    def get_all_courses(self) -> list[Course]:
        return self.gradebook.courses.copy()    # return only a copy of the list, so the original can't be manipulated
    

    def get_all_students(self) -> list[Student]:
        return self.gradebook.students.copy()   # return only a copy of the list, so the original can't be manipulated
    

    # --- Update --- #
    def update_student(self, student: Student) -> None:

        for index, s in enumerate(self.gradebook.students):
            if s.student_id == student.student_id:
                self.gradebook.students[index] = student
                return
        raise ValueError(f"Student not found")
    

    def update_course(self, course: Course) -> None:

        for index, c in enumerate(self.gradebook.courses):
            if c.course_id == course.course_id:
                self.gradebook.courses[index] = course
                return
        raise ValueError(f"Course not found")
    
    def update_grade(self, grade: Grade) -> None:

        for index, g in enumerate(self.gradebook.grades):
            if (
                g.student.student_id == grade.student.student_id
                and g.course.course_id == grade.course.course_id
                and g.date == grade.date
            ):
                self.gradebook.grades[index] = grade
                return
        raise ValueError("Grade not found")
    



    # --- Delete --- #
    def delete_student(self, student: Student) -> None:

        for index, s in enumerate(self.gradebook.students):
            if s.student_id == student.student_id:
                self.gradebook.students.remove(s)
                return
        raise ValueError(f"Student not found")


    def delete_course(self, course: Course) -> None:
        
        for index, c in enumerate(self.gradebook.courses):
            if c.course_id == course.course_id:
                self.gradebook.courses.remove(c)
                return
        raise ValueError(f"Course not found")
    

    def delete_grade(self, grade: Grade) -> None:

        for index, g in enumerate(self.gradebook.grades):

            if (
                g.student.student_id == grade.student.student_id
                and g.course.course_id == grade.course.course_id
                and g.date == grade.date
            ):
                self.gradebook.grades.remove(g)
                return

        raise ValueError("Grade not found")
