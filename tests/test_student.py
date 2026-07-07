from grade_management.student import Student


def test_valid_student_creation():
  studi = Student("Jane", "Doe", "jane.doe@example.com")
  assert studi.email == "jane.doe@example.com"
  assert studi.full_name == "Jane Doe"

def test_empty_firstname():
    studi = Student("", "Doe", "jane.doe@example.com")
    #studi.first_name == ""

def test_empty_lastname():
    studi = Student("Jane", "", "jane.doe@example.com")
    #studi.last_name == ""

def test_false_email():
   studi = Student("Jane", "Doe", "jane.doe.com")
   
   

