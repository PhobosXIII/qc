from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from main import views as main_views
from main.forms import AuthForm
from qc import settings

urlpatterns = [
    url(r'^{}/'.format(settings.ADMIN_URL_PATH), include(admin.site.urls)),
    url(r'^login/$', auth_views.login, {'authentication_form': AuthForm}, name='auth_login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'auth_login'}, name='auth_logout'),
    url(r'^$', main_views.home, name='home'),
    url(r'^contacts/', include([
        url(r'^$', main_views.contacts, name='contacts'),
        url(r'^org/$', main_views.contacts, {'subj_code': 1}, name='contacts_org'),
    ])),
    url(r'^profile/', include([
        url(r'^$', main_views.my_profile, name='my_profile'),
        url(r'^password_change/$', auth_views.password_change, name='password_change'),
        url(r'^password_change/done/$', auth_views.password_change_done, name='password_change_done'),
    ])),
    url(r'^news/', include([
        url(r'^$', main_views.all_news, name='news'),
        url(r'^(?P<news_id>[0-9]+)/$', main_views.detail_news, name='news_detail'),
    ])),
    url(r'^help/', include([
        url(r'^$', main_views.help, name='help'),
        url(r'^(?P<category_id>[0-9]+)/$', main_views.help_category, name='help_category'),
    ])),
    url(r'^', include('coordination.urls', namespace='coordination')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
