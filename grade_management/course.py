from dataclasses import dataclass

@dataclass
class Course:
        course_id: str
        name: str
        max_grade: float = 100.0
        passing_grade: float = 50.0

        def __eq__(self, other):
            """Compare Courses by ID."""
            if not isinstance(other, Course):
                return NotImplemented
            return self.course_id == other.course_id
        
        def __str__(self):
             return f"Course('{self.name}', {self.course_id})"
