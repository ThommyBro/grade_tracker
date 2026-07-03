from dataclasses import dataclass
import re


@dataclass
class Student:
    student_id: str
    first_name: str
    last_name: str
    email: str

    def __post_init__(self):
        if self.first_name is "" or self.last_name is "":  # Firstname and Lastname must not be empty
            raise ValueError(f"First and Lastname must not be empty!")
        elif not re.search(r"^\w+@\w+\.\w{2,3}$", self.email):
            # email starts with "word characters" followed by '@', followed by "word", then '.', then 2 or 3 "word characters"
            raise ValueError(f"Stundents must have a valid emailaddress! "
                             f"({self.email})")  


    def __str__(self):
        """Just a pretty Student object."""
        return (f"Student(Student ID: {self.student_id}, Name: {self.first_name} {self.last_name}, " 
                f"Email: {self.email})"
        )


    def __eq__(self, other):
        """Compare Students by ID."""
        if not isinstance(other, Student):
            return NotImplemented
        return self.student_id == other.student_id


    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    






def main():
    student = Student("0001", "Thomas", "Brockt", "thomas@home.edu")
    print(student)
    




if __name__ == "__main__":
    main()