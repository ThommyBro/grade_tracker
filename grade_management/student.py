from dataclasses import dataclass, field


@dataclass
class Student:
    student_id: str
    first_name: str
    last_name: str
    email: str



    def full_name(self) -> str:
        pass