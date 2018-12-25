from django.conf.urls import include
from django.contrib.auth import views as auth_views
from django.urls import path, re_path

from main import views as main_views
from main.forms import AuthForm
from qc import settings
from qc.admin import admin_site

urlpatterns = [
    path('{}/'.format(settings.ADMIN_URL_PATH), admin_site.urls),
    path('login/', auth_views.LoginView, {'authentication_form': AuthForm}, name='auth_login'),
    path('logout/', auth_views.LogoutView, {'next_page': 'auth_login'}, name='auth_logout'),
    re_path(r'^$', main_views.home, name='home'),
    path('contacts/', include([
        path('', main_views.contacts, name='contacts'),
        path('org/', main_views.contacts, {'subj_code': 1}, name='contacts_org'),
    ])),
    path('profile/', include([
        path('', main_views.my_profile, name='my_profile'),
        path('password_change/', auth_views.PasswordChangeView, name='password_change'),
        path('password_change/done/', auth_views.PasswordChangeDoneView, name='password_change_done'),
    ])),
    path('news/', include([
        path('', main_views.all_news, name='news'),
        path('<int:news_id>', main_views.detail_news, name='news_detail'),
    ])),
    path('help/', include([
        path('', main_views.help, name='help'),
        path('<int:category_id>/', main_views.help_category, name='help_category'),
    ])),
    re_path(r'^', include(('coordination.urls', 'coordination'), namespace='coordination')),
]
