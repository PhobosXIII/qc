from django.contrib.admin import AdminSite

from qc import settings


class MyAdminSite(AdminSite):
    site_header = 'Администрирование {}'.format(settings.FULL_PROJECT_NAME)
    site_title = '| Администрирование {}'.format(settings.PROJECT_NAME)


admin_site = MyAdminSite(name=settings.ADMIN_URL_PATH)
