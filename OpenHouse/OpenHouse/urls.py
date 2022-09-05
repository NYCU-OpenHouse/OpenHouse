"""OpenHouse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import include, path
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import rdss.views
import general.views
from ckeditor_uploader import views as ckeditor_views
# for media file
from django.conf import settings
from django.conf.urls.static import static
import oauth2_provider.views as oauth2_views

# OAuth2 provider endpoints
oauth2_endpoint_views = [
    path('authorize/', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    path('token/', oauth2_views.TokenView.as_view(), name="token"),
    path('revoke-token/', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

if settings.DEBUG:
    # OAuth2 Application Management endpoints
    oauth2_endpoint_views += [
        path('applications/', oauth2_views.ApplicationList.as_view(), name="list"),
        path('applications/register/', oauth2_views.ApplicationRegistration.as_view(), name="register"),
        path('applications/<pk>/', oauth2_views.ApplicationDetail.as_view(), name="detail"),
        path('applications/<pk>/delete/', oauth2_views.ApplicationDelete.as_view(), name="delete"),
        path('applications/<pk>/update/', oauth2_views.ApplicationUpdate.as_view(), name="update"),
    ]

    # OAuth2 Token Management endpoints
    oauth2_endpoint_views += [
        path('authorized-tokens/', oauth2_views.AuthorizedTokensListView.as_view(), name="authorized-token-list"),
        path('authorized-tokens/<pk>/delete/', oauth2_views.AuthorizedTokenDeleteView.as_view(),
            name="authorized-token-delete"),
    ]



urlpatterns = [
    # custom sponsorship admin url and view
    
    url(r'', include('general.urls')),  # add '' on the include path!!!
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URL
    url(r'^admin/rdss/', include('rdss.admin_urls')),
    url(r'^admin/recruit/', include('recruit.admin_urls')),
    url(r'^admin/careermentor/', include('careermentor.admin_urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^company/', include('company.urls')),  # add '' on the include path!!!
    url(r'^company/rdss/', include('rdss.internal_urls')),  # add '' on the include path!!!
    url(r'^company/recruit/', include('recruit.internal_urls')),  # add '' on the include path!!!
    url(r'^staff/', include('staff.urls')),  # add '' on the include path!!!
    url(r'^admin/staff/', include('staff.admin_urls')),

    url(r'^rdss/', include('rdss.public_urls')),  # add '' on the include path!!!
    # url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^ckeditor/upload/', login_required(ckeditor_views.upload), name='ckeditor_upload'),
    url(r'^ckeditor/browse/', never_cache(login_required(ckeditor_views.browse)), name='ckeditor_browse'),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^mentor/', include('careermentor.urls')),
    url(r'^recruit/', include('recruit.public_urls')),
    url(r'^visit/', include('company_visit.urls')),
    # url(r'^vote/', include('vote.urls')),
    url(r'^monograph/', include('monograph.urls')),
    path('o/', include((oauth2_endpoint_views, 'oauth2_provider'), namespace="oauth2_provider")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
