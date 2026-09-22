from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("teacher/questions/", views.teacher_question_bank, name="teacher_question_bank"),
    path("teacher/questions/new/", views.teacher_question_create, name="teacher_question_create"),
    path("teacher/questions/<int:pk>/edit/", views.teacher_question_edit, name="teacher_question_edit"),
    path("teacher/questions/<int:pk>/delete/", views.teacher_question_delete, name="teacher_question_delete"),
    path("teacher/sets/new/", views.teacher_create_set, name="teacher_create_set"),
    path("teacher/sets/<uuid:public_id>/explain/", views.teacher_explain_set, name="teacher_explain_set"),
    path("teacher/sets/<uuid:public_id>/delete/", views.teacher_delete_set, name="teacher_delete_set"),
    path("teacher/annotations/question/<int:question_id>/create/", views.teacher_free_annotation_create, name="teacher_free_annotation_create"),
    path("teacher/annotations/<int:annotation_id>/update/", views.teacher_free_annotation_update, name="teacher_free_annotation_update"),
    path("teacher/annotations/<int:annotation_id>/delete/", views.teacher_free_annotation_delete, name="teacher_free_annotation_delete"),
    path("teacher/sets/<uuid:public_id>/created/", views.teacher_set_created, name="teacher_set_created"),
    path("teacher/sets/<uuid:public_id>/results/", views.teacher_set_results, name="teacher_set_results"),
    path("quiz/<uuid:public_id>/", views.student_take_set, name="student_take_set"),
    path("submission/<int:submission_id>/complete/", views.submission_complete, name="submission_complete"),
]
