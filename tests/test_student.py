import pytest

from grade_management.student import Student


def test_valid_student_creation():
  student = Student("12345","Jane", "Doe", "jane.doe@example.com")
  assert student.student_id == "12345"
  assert student.first_name == "Jane"
  assert student.last_name == "Doe"
  assert student.email == "jane.doe@example.com"
  assert student.full_name == "Jane Doe"

def test_empty_firstname():
    #studi.first_name == ""
    with pytest.raises(ValueError, match="First name must not be empty"):
       Student("12345","", "Doe", "jane.doe@example.com")

def test_empty_lastname():
    #studi.last_name == ""
    with pytest.raises(ValueError, match="Last name must not be empty"):
       Student("12345","Jane", "", "jane.doe@example.com")

def test_invalid_email():
   with pytest.raises(ValueError, match="Student must have a valid email address"):
        Student("12345","Jane", "Doe", "jane.doe.com")


def test_firstname_must_be_String():
   with pytest.raises(ValueError, match="First name must be a string"):
       Student("12345",123, "Doe", "jane.doe@example.com")


def test_lastname_must_be_string():
   with pytest.raises(ValueError, match="Last name must be a string"):
       Student("12345","Jane", 213, "jane.doe@example.com")


   
   

   
   

