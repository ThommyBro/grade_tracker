from grade_management.student import Student
from grade_management.course import Course
from grade_management.grade import Grade

from grade_store.grade_store import GradeStore

from exceptions import (DuplicateEntryError, StudentNotFoundError, CourseNotFoundError, GradeNotFoundError)


class InMemoryGradeStore(GradeStore):
    """
    Saves all data in dicts and lists. There is no persistence.
    """

    def __init__(self):
        self._students: dict[str, Student] = {}
        self._courses: dict[str, Course] = {}
        self._grades: dict[str, Grade] = {}
        self._next_grade_id = 1

    
     # ------------------------------------------------------------------ #
    # Students
    # ------------------------------------------------------------------ #
    def add_student(self, student: Student) -> None:
        if student.student_id in self._students:
            raise DuplicateEntryError("Student", student.student_id)
        self._students[student.student_id] = student

    def get_student(self, student_id: str) -> Student:
        student = self._students.get(student_id)
        if student is None:
            raise StudentNotFoundError(student_id)
        return student

    def list_students(self) -> list[Student]:
        return list(self._students.values())

    def update_student(self, student: Student) -> None:
        
        if student.student_id not in self._students:
            raise StudentNotFoundError(student.student_id)
        self._students[student.student_id] = student

        for grade_id, grade in list(self._grades.items()):
            if grade.student.student_id == student.student_id:
                self._grades[grade_id] = Grade(
                    student=student,
                    course=grade.course,
                    score=grade.score,
                    date=grade.date,
                    notes=grade.notes,
                    grade_id=grade_id,
                )

    def delete_student(self, student: Student) -> None:
        self.get_student(student.student_id)  # wirft StudentNotFoundError, falls unbekannt

        ids_to_delete = [
            grade_id
            for grade_id, grade in self._grades.items()
            if grade.student.student_id == student.student_id
        ]
        for grade_id in ids_to_delete:
            del self._grades[grade_id]

        del self._students[student.student_id]

    # ------------------------------------------------------------------ #
    # Courses
    # ------------------------------------------------------------------ #
    def add_course(self, course: Course) -> None:
        if course.course_id in self._courses:
            raise DuplicateEntryError("Kurs", course.course_id)
        self._courses[course.course_id] = course

    def get_course(self, course_id: str) -> Course:
        course = self._courses.get(course_id)
        if course is None:
            raise CourseNotFoundError(course_id)
        return course

    def list_courses(self) -> list[Course]:
        return list(self._courses.values())

    def update_course(self, course: Course) -> None:
        if course.course_id not in self._courses:
            raise CourseNotFoundError(course.course_id)
        self._courses[course.course_id] = course

        for grade_id, grade in list(self._grades.items()):
            if grade.course.course_id == course.course_id:
                self._grades[grade_id] = Grade(
                    student=grade.student,
                    course=course,
                    score=grade.score,
                    date=grade.date,
                    notes=grade.notes,
                    grade_id=grade_id,
                )

    def delete_course(self, course: Course) -> None:
        self.get_course(course.course_id)  # wirft CourseNotFoundError, falls unbekannt

        ids_to_delete = [
            grade_id
            for grade_id, grade in self._grades.items()
            if grade.course.course_id == course.course_id
        ]
        for grade_id in ids_to_delete:
            del self._grades[grade_id]

        del self._courses[course.course_id]

    # ------------------------------------------------------------------ #
    # Grades
    # ------------------------------------------------------------------ #
    def add_grade(
        self, student_id: str, course_id: str, score: float, date: str, notes: str = ""
    ) -> Grade:
        student = self.get_student(student_id)
        course = self.get_course(course_id)

        grade_id = str(self._next_grade_id)
        self._next_grade_id += 1

        grade = Grade(
            student=student, course=course, score=score, date=date, notes=notes, grade_id=grade_id
        )
        self._grades[grade_id] = grade
        return grade

    def get_student_grades(self, student_id: str) -> list[Grade]:
        self.get_student(student_id)  # error if unknown
        return [g for g in self._grades.values() if g.student.student_id == student_id]

    def get_course_grades(self, course_id: str) -> list[Grade]:
        self.get_course(course_id)  # error if unknown
        return [g for g in self._grades.values() if g.course.course_id == course_id]

    def list_grades(self) -> list[Grade]:
        return list(self._grades.values())  

    def get_grade(self, grade_id: str) -> Grade:
        grade = self._grades.get(grade_id)
        if grade is None:
            raise GradeNotFoundError(grade_id)
        return grade

    def update_grade(self, grade_id: str, score: float, date: str, notes: str = "") -> Grade:
        existing = self.get_grade(grade_id)  # error if unknown

        updated = Grade(
            student=existing.student,
            course=existing.course,
            score=score,
            date=date,
            notes=notes,
            grade_id=existing.grade_id,  
        )
        self._grades[grade_id] = updated
        return updated

    def delete_grade(self, grade_id: str) -> None:
        if grade_id not in self._grades:
            raise GradeNotFoundError(grade_id)
        del self._grades[grade_id]
                
