from django.urls import path
import careermentor.views as views
import careermentor.export as export

urlpatterns = [

    path('student_signup_status/list', views.ListCareerMentor, name="listStudentSignupStatus"),
    path('student_signup_status/export/<int:id>', export.ExportStudentSignupStatus, name="exportStudentSignupStatus"),
]
