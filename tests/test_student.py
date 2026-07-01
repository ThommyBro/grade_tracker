import grade_management.student as student

class TestStudent:

    # validate function if firstname is empty    
    def validate_first_name(self, student):
        assert student.first_name != None
    

    # validate function if lastname is empty    
    def validate_last_name(self, student):
        assert student.last_name != None
