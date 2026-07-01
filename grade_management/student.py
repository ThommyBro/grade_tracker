from dataclasses import dataclass


@dataclass
class Student:
    student_id: str
    first_name: str
    last_name: str
    email: str


    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    






def main():
    student = Student("0001", "Thomas", "Brockt", "thomas@home.edu")
    print(student)
    




if __name__ == "__main__":
    main()