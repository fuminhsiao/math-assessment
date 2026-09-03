from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("teacher/sets/new/", views.teacher_create_set, name="teacher_create_set"),
    path("teacher/sets/<uuid:public_id>/created/", views.teacher_set_created, name="teacher_set_created"),
    path("teacher/sets/<uuid:public_id>/results/", views.teacher_set_results, name="teacher_set_results"),
    path("quiz/<uuid:public_id>/", views.student_take_set, name="student_take_set"),
    path("submission/<int:submission_id>/complete/", views.submission_complete, name="submission_complete"),
]
