from django.urls import path
import company_visit.views as views
import company_visit.export as export

urlpatterns = [

    path('student_signup_status/list', views.ListCompanyVisit, name="listStudentSignupStatus"),
    path('student_signup_status/export/<int:id>', export.ExportStudentSignupStatus, name="exportStudentSignupStatus"),
]
