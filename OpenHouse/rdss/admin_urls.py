from django.conf.urls import url
from django.urls import path
import rdss.views as views
import rdss.export as export

urlpatterns = [
    # Examples:
    # url(r'^$', 'oh2016_dj.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^sponsorship/$', views.SponsorAdmin, name="rdss_sponsorship_situation"),
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
    path(r'jobfairslot/bulk_add', views.bulk_add_jobfairslot, name='rdss_bulk_add_jobfairslot'),
    path(r'companycategories/sync', views.sync_company_categories, name='rdss_sync_company_categories'),
    path(r'redeem_seminar_daily_prize/<str:idcard_no>/<str:date>/', views.redeem_seminar_daily_prize, name='rdss_redeem_seminar_daily_prize'),
    url(r'show_student_with_daily_seminar_prize/$', views.show_student_with_daily_seminar_prize, name='rdss_show_student_with_daily_seminar_prize'),	
	#export urls are defined in admin.py
]
