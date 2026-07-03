from dataclasses import dataclass

@dataclass
class Course:
        course_id: str
        name: str
        max_grade: float = 100.0
        passing_grade: float = 50.0

        def __eq__(self, other):
            if not isinstance(other, Course):
                return NotImplemented
            return self.course_id == other.course_id
