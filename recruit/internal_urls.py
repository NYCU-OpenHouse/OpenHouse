from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.recruit_company_index, name='recruit_company_index'),
    url(r'^signup/$', views.recruit_signup, name='recruit_signup'),
    url(r'^jobfair/info/$', views.jobfair_info, name='recruit_jobfair_info'),
    url(r'^sponsor/$', views.recruit_sponsor, name='recruit_sponsor'),
    url(r'^survey/$', views.company_servey, name='recruit_survey'),
]