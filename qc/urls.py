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
from django.contrib import admin
from django.contrib.auth import views as auth_views
from main import views as main_views
from qc import settings

urlpatterns = [
    url(r'^{}/'.format(settings.ADMIN_URL_PATH), include(admin.site.urls)),
    url(r'^login/$', auth_views.login, name='auth_login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'auth_login'}, name='auth_logout'),
    url(r'^password_change/$', auth_views.password_change, name='auth_password_change'),
    url(r'^password_change/done/$', auth_views.password_change_done, name='auth_password_change_done'),
    url(r'^$', main_views.home, name='home'),
    url(r'^', include('coordination.urls', namespace='coordination')),
]
