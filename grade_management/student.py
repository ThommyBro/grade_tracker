from dataclasses import dataclass


@dataclass
class Student:
    student_id: str
    first_name: str
    last_name: str
    email: str

    def __post_init__(self):
        if self.first_name is "" or self.last_name is "":
            raise ValueError(f"First and Lastname must not be empty!")
        elif not "@" in self.email:
            raise ValueError(f"Emailaddress must contain '@' symbol!")  


    def __str__(self):
        return (f"Student(Student ID: {self.student_id}, Name: {self.first_name} {self.last_name}, " 
                f"Email: {self.email})"
        )


    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    






def main():
    student = Student("0001", "Thomas", "Brockt", "thomas@home.edu")
    print(student)
    




if __name__ == "__main__":
    main()