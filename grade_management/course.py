from dataclasses import dataclass, field

@dataclass
class Course:
        course_id: str
        name: str
        max_grade: float = 0.0
        passing_grade: float = 0.0
        