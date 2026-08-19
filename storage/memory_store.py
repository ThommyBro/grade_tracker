from grade_management.student import Student
from grade_management.course import Course
from grade_management.grade import Grade

from grade_store.grade_store import GradeStore

from exceptions import (DuplicateEntryError, StudentNotFoundError, CourseNotFoundError)


class InMemoryGradeStore(GradeStore):
    """
    Saves all data in dicts and lists. There is no persistence.
    """

    def __init__(self):
        self._students: dict[str, Student] = {}
        self._courses: dict[str, Course] = {}
        self._grades: list[Grade] = []

    
    # --- Add --- #
    def add_student(self, student: Student) -> None:
        if student.student_id in self._students:
            raise DuplicateEntryError("Student", student.student_id)
        self._students[student.student_id] = student


    def add_course(self, course: Course) -> None:
        if course.course_id in self._courses:
            raise DuplicateEntryError("Course", course.course_id)
        self._courses[course.course_id] = course

            
    def add_grade(self, student_id: str, course_id: str, score: float, date: str, notes: str = "") -> Grade:
        student = self.get_student(student_id)
        course = self.get_course(course_id)
        grade = Grade(student=student, course=course, score=score, date=date, notes=notes)
        self._grades.append(grade)
        return grade


    # --- Get --- #
    def get_student(self, student_id: str) -> Student:
        student = self._students.get(student_id)
        if student is None:
            raise StudentNotFoundError(student_id)
        return student

    def get_all_students(self) -> list[Student]:
        return list(self._students.values())


    def get_course(self, course_id: str) -> Course:
        course = self._courses.get(course_id)
        if course is None:
            raise CourseNotFoundError(course_id)
        return course

    def get_all_courses(self) -> list[Course]:
        return list(self._courses.values())


    def get_all_grades(self) -> list[Grade]:
        return list(self._grades)

    def get_student_grades(self, student_id: str) -> list[Grade]:
        self.get_student(student_id)    # raises error if not found
        return [g for g in self._grades if student_id == g.student.student_id] 

    def get_course_grades(self, course_id: str) -> list[Grade]:
        self.get_course(course_id)       # raises error if not found
        return [g for g in self._grades if course_id == g.course.course_id]


    # --- Updates --- #
    def update_student(self, student: Student) -> None:
        self._students[student.student_id] = student

        for g in self._grades:
            if g.student.student_id == student.student_id:
                g.student = student


    def update_course(self, course: Course) -> None:
        self._courses[course.course_id] = course

        for g in self._grades:
            if g.course.course_id == course.course_id:
                g.course = course


    def update_grade(self, grade: Grade) -> None:
        for index, g in enumerate(self._grades):
                    if (
                        g.student.student_id == grade.student.student_id
                        and g.course.course_id == grade.course.course_id
                        and g.date == grade.date
                        ):
                            self._grades[index] = grade
                        


    # --- Delete --- #
    def delete_student(self, student: Student) -> None:
        """
        Deletes a student from students dict and also all related grades from this student.
        """
        self.get_student(student.student_id)
        del(self._students[student.student_id])

        for index, g in enumerate(self._grades):
            if g.student.student_id == student.student_id:
                del(self._grades[index])


    
    def delete_course(self, course: Course) -> None:
        self.get_course(course.course_id)
        del(self._courses[course.course_id])

  
    def delete_grade(self, grade: Grade) -> None:
        for index, g in enumerate(self._grades):
            if (
                g.student.student_id == grade.student.student_id
                and g.course.course_id == grade.course.course_id
                and g.date == grade.date
            ):
                self._grades.remove(g)
                
