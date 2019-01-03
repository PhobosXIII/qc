from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

from qc import settings


class MyAdminSite(AdminSite):
    site_header = 'Администрирование {}'.format(settings.FULL_PROJECT_NAME)
    site_title = '| Администрирование {}'.format(settings.PROJECT_NAME)


def user_str(self):
    return self.first_name


User.__str__ = user_str


class MyUserAdmin(UserAdmin):
    list_display = ('username', 'first_name')


admin_site = MyAdminSite(name=settings.ADMIN_URL_PATH)
admin_site.register(User, MyUserAdmin)
admin_site.register(Group)
