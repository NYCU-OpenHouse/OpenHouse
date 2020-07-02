from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<monograph_id>[0-9].*)/$', views.monograph_detail, name='monograph_detail'),
]
