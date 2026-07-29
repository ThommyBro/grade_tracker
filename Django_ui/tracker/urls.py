from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("students/", views.student_list, name="student_list"),
    path("student-test/", views.student_test, name="student-test"),
    path("students/clear/",views.clear_student_detail, name="clear-student-detail"),
    path("students/<str:student_id>/", views.student_detail, name="student-detail"),
    

    path("courses/", views.course_list, name="course_list"),
]