from abc import ABC, abstractmethod
from gradebook_new import GradeBook

class ReportGenerator(ABC):
    """Baseclass for CSV and TXT reports"""

    @abstractmethod
    def generate_student_report(self, student_id: str, gradebook: "GradeBook") -> str: ...

    @abstractmethod
    def generate_course_report(self, course_id: str, gradebook: "GradeBook") -> str: ...

    @abstractmethod
    def generate_summary_report(self, gradebook: "GradeBook") -> str: ...