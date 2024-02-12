from django.conf.urls import url
import recruit.views as views
import recruit.export as export

urlpatterns = [
    # Examples:
    # url(r'^$', 'oh2016_dj.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^sponsorship/$', views.SponsorAdmin),
    url(r'^export_activity_info/$', export.ExportActivityInfo, name="recruit_export_activity_info"),
    url(r'^export_all/$', export.ExportAll, name="recruit_export_all"),
    url(r'^export_ad/$', export.ExportAdFormat, name="recruit_export_ad"),
    url(r'^export_seminar_info/$', export.export_seminar_info, name="recruit_export_seminar_info"),
    url(r'^export_online_seminar_info/$', export.export_online_seminar_info, name="recruit_export_online_seminar_info"),
    url(r'^export_jobfair_info/$', export.export_jobfair_info, name="recruit_export_jobfair_info"),
    
    url(r'^reg_card/$', views.RegisterCard, name='recruit_reg_card'),
    url(r'^collect_points/$', views.CollectPoints, name='collect_points'),
    url(r'^exchange_prize/$', views.ExchangePrize, name='exchange_prize'),
    url(r'export_points_info/$', export.ExportPointsInfo, name='rdss_export_points_info'),
    url(r'^seminar_attended_student/$', views.SeminarAttendedStudent, name='recruit_seminar_attended_student'),
    url(r'seminar_attended_student/detail/<int:seminar_id>', views.SeminarAttendedStudentDetail, name='recruit_seminar_attended_student_detail'),

    url(r'^export_jobs/$', export.ExportJobs,name="recruit_export_jobs"),

    #export urls are defined in admin.py
]
