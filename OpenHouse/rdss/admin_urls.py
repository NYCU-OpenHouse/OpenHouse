from django.conf.urls import url
from django.urls import path
import rdss.views as views
import rdss.export as export

urlpatterns = [
    # Examples:
    # url(r'^$', 'oh2016_dj.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^sponsorship_situation/$', views.SponsorAdmin, name="rdss_sponsorship_situation"),
    url(r'^collect_points/$', views.CollectPoints, name="rdss_collect_points"),
    url(r'^reg_card/$', views.RegisterCard, name="rdss_reg_card"),
    url(r'redeem/$', views.RedeemPrize, name='rdss_redeem'),
    url(r'export_points_info/$', export.ExportPointsInfo, name='rdss_export_points_info'),
    url(r'^seminar_attended_student/$', views.SeminarAttendedStudent, name='rdss_seminar_attended_student'),
    path(r'seminar_attended_student/detail/<int:seminar_id>', views.SeminarAttendedStudentDetail, name='rdss_seminar_attended_student_detail'),
    url(r'import_student_card_info/$', views.ImportStudentCardInfo, name='rdss_import_student_card_info'),
    url(r'clear_student_info/$', views.ClearStudentInfo, name='rdss_clear_student_info'),
    url(r'^export_activity_info/$', export.ExportActivityInfo, name="rdss_export_activity_info"),
    url(r'^export_all/$', export.ExportAll, name="rdss_export_all"),
    url(r'^export_ad/$', export.ExportAdFormat,name="rdss_export_ad"),
    url(r'^export_jobfair/$', export.ExportJobfair,name="rdss_export_jobfair"),
    url(r'^export_seminar/$', export.ExportSeminar,name="rdss_export_seminar"),
    url(r'^export_jobs/$', export.ExportJobs,name="rdss_export_jobs"),
    path(r'jobfairslot/bulk_add', views.bulk_add_jobfairslot, name='bulk_add_jobfairslot'),
    path(r'companycategories/sync', views.sync_company_categories, name='sync_company_categories'),
    url(r'show_3_seminar_attendance_student_2024/$', views.show_3_seminar_attendance_student_2024, name='show_3_seminar_attendance_student_2024'),
    path(r'redeem_seminar_meal_ticket_2024/<str:student_id>/<str:date>/', views.redeem_seminar_meal_ticket_2024, name='show_3_seminar_attendance_student_2024_redeem'),
	#export urls are defined in admin.py
]
