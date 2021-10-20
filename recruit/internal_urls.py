from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.recruit_company_index, name='recruit_company_index'),
    url(r'^signup/$', views.recruit_signup, name='recruit_signup'),
    url(r'^seminar/info/$', views.seminar_info, name='recruit_seminar_info'),
    # url(r'^seminar/info/$', views.seminar_info_temporary, name='recruit_seminar_info'),
    url(r'^online_seminar/info/$', views.online_seminar_info, name='recruit_online_seminar_info'),
    url(r'^seminar/select/$', views.seminar_select_form_gen, name='recruit_seminar_select'),
    url(r'^seminar/select_ctrl/$', views.seminar_select_control, name='recruit_seminar_select_ctrl'),
    url(r'^online_seminar/select/$', views.online_seminar_select_form_gen, name='recruit_online_seminar_select'),
    url(r'^online_seminar/select_ctrl/$', views.online_seminar_select_control,
        name='recruit_online_seminar_select_ctrl'),
    url(r'^jobfair/info/$', views.jobfair_info, name='recruit_jobfair_info'),
    # url(r'^jobfair/info/$', views.jobfair_info_temp, name='recruit_jobfair_info'),
    url(r'^jobfair/select/$', views.jobfair_select_form_gen, name='recruit_jobfair_select'),
    url(r'^jobfair/select_ctrl/$', views.jobfair_select_control, name='recruit_jobfair_select_ctrl'),
    url(r'^sponsor/$', views.Sponsor, name='recruit_sponsor'),
    url(r'^survey/$', views.company_survey, name='recruit_survey'),
    url(r'^status$', views.Status, name="recruit_status"),

]
