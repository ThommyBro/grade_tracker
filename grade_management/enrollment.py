from dataclasses import dataclass


@dataclass
class Enrollment:
    student_id: str
    course_id: str

    