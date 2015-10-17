from django.conf import settings


def global_settings(request):
    return {
        'PROJECT_NAME': settings.PROJECT_NAME,
        'FULL_PROJECT_NAME': settings.FULL_PROJECT_NAME,
        'PROJECT_VERSION': settings.PROJECT_VERSION,
    }