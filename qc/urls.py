"""qc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from main import views as main_views
from qc import settings

urlpatterns = [
    url(r'^{}/'.format(settings.ADMIN_URL_PATH), include(admin.site.urls)),
    url(r'^login/$', auth_views.login, name='auth_login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'auth_login'}, name='auth_logout'),
    url(r'^$', main_views.home, name='home'),
    url(r'^contacts/$', main_views.contacts, name='contacts'),
    url(r'^contacts/org/$', main_views.contacts, {'subj_code': 1}, name='contacts_org'),
    url(r'^profile/', include([
        url(r'^$', main_views.my_profile, name='my_profile'),
        url(r'^password_change/$', auth_views.password_change, name='password_change'),
        url(r'^password_change/done/$', auth_views.password_change_done, name='password_change_done'),
    ])),
    url(r'^news/', include([
        url(r'^$', main_views.all_news, name='news'),
        url(r'^(?P<news_id>[0-9]+)/$', main_views.detail_news, name='news_detail'),
    ])),
    url(r'^', include('coordination.urls', namespace='coordination')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
