from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.public, name='public'),
    url(r'^jobs/$', views.list_jobs, name='list_jobs'),
    url(r'^seminar/$', views.seminar, name='seminar'),
    # url(r'^seminar/$', views.seminar_temporary, name='seminar'),
    # url(r'^jobfair/(?P<company_cid>[0-9].*)/$', views.jobfair_online, name='jobfair_online'),
    url(r'^jobfair/$', views.jobfair, name='jobfair'),
    url(r'^querypts/$', views.query_points, name='query_points'),
]
