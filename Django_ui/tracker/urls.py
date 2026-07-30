from django.urls import path

from . import views

urlpatterns = [

    path("", views.home, name="home"),

    path("students/", views.student_list, name="student_list"),

    path("students/table/", views.student_table, name="student-table"),

    path(
        "students/clear/",
        views.clear_student_detail,
        name="clear-student-detail"
    ),

    path(
        "students/create/",
        views.create_student,
        name="create-student"
    ),

    path(
        "students/<str:student_id>/edit/",
        views.edit_student,
        name="edit-student"
    ),

    path(
        "students/<str:student_id>/update/",
        views.update_student,
        name="update-student"
    ),

    path(
        "students/<str:student_id>/delete/",
        views.delete_student,
        name="delete-student"
    ),


    path(
        "students/<str:student_id>/",
        views.student_detail,
        name="student-detail"
    ),


    path("student-test/", views.student_test, name="student-test"),

    path("courses/", views.course_list, name="course_list"),
]