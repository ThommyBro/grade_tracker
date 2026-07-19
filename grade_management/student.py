from dataclasses import dataclass, field
import random



def id_generator():
    i = ""
    id = ""
    for _ in range(5):
        i = str(random.randint(0,9))
        id += i
    return id

@dataclass
class Student:
    student_id: str # = field(default_factory=id_generator, kw_only=True) # key-word only, stud_id can be first attribute despite standard value
    first_name: str
    last_name: str
    email: str

    def __post_init__(self):

        if not isinstance(self.first_name, str):
            raise ValueError("First name must be a string")

        if not isinstance(self.last_name, str):
            raise ValueError("Last name must be a string")

        if not self.first_name:
            raise ValueError("First name must not be empty")

        if not self.last_name:
            raise ValueError("Last name must not be empty")

        if not isinstance(self.email, str) or "@" not in self.email:
            raise ValueError(f"Student must have a valid email address")
        


    def __str__(self):
        """Just a pretty Student object."""
        return (f"Student(Student ID: {self.student_id}, Name: {self.first_name} {self.last_name}, " 
                f"Email: {self.email})"
        )
    
    def __repr__(self):
        return f"{self.student_id}, {self.first_name}, {self.last_name}, {self.email} "


    def __eq__(self, other):
        """Compare Students by ID."""
        if not isinstance(other, Student):
            return NotImplemented
        return self.student_id == other.student_id


    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    






# def main():
#     student = Student("0001", "Thomas", "Brockt", "thomas@home.edu")
#     print(student)
    




# if __name__ == "__main__":
#     main()