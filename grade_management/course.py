from dataclasses import dataclass

@dataclass
class Course:
        course_id: str
        name: str
        max_grade: float = 100.0
        passing_grade: float = 50.0


        def __post_init__(self):
            if not 0 < self.max_grade <=100.0:
                raise ValueError(f"Check your max grade!")
            if not 0 < self.passing_grade <= self.max_grade:
                 raise ValueError(f"Check your passing grade!")
              

        def __eq__(self, other):
            """Compare Courses by ID."""
            if not isinstance(other, Course):
                return NotImplemented
            return self.course_id == other.course_id
        
        def __str__(self):
             return f"Course('{self.name}', {self.course_id})"
        

        def __repr__(self):
             return f"{self.name}, {self.course_id}"
