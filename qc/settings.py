# Django settings for qc project.

import os
import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse_lazy


def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)


# Get ENV VARIABLES key
ENV_ROLE = get_env_variable('ENV_ROLE')
QC_UPLOAD = get_env_variable('QC_UPLOAD') == 'True'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = get_env_variable('QC_SECRET_KEY')

PROJECT_NAME = 'QC'
FULL_PROJECT_NAME = 'QuestCoordination'
PROJECT_VERSION_BASE = 'v3.4'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'main',
    'coordination',
    'ckeditor',
)

BASE_MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
MEDIA_URL = '/media/'

if QC_UPLOAD:
    INSTALLED_APPS += (
        'sendfile',
    )
    SENDFILE_ROOT = os.path.join(MEDIA_ROOT, 'mission_imgs')
    SENDFILE_URL = '/mission_imgs'

if ENV_ROLE == 'dev':
    DEBUG = True
    ALLOWED_HOSTS = []
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    if QC_UPLOAD:
        SENDFILE_BACKEND = 'sendfile.backends.development'

    MIDDLEWARE = BASE_MIDDLEWARE

if ENV_ROLE == 'prod' or ENV_ROLE == 'stage':
    DEBUG = False

    QC_OPBEAT = get_env_variable('QC_OPBEAT') == 'True'
    if QC_OPBEAT:
        INSTALLED_APPS += (
            'opbeat.contrib.django',
        )
        OPBEAT = {
            'ORGANIZATION_ID': get_env_variable('OPBEAT_ORG_ID'),
            'APP_ID': get_env_variable('OPBEAT_APP_ID'),
            'SECRET_TOKEN': get_env_variable('OPBEAT_SECRET'),
        }
        MIDDLEWARE = (
                         'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
                     ) + BASE_MIDDLEWARE
    else:
        MIDDLEWARE = BASE_MIDDLEWARE

    if QC_UPLOAD:
        SENDFILE_BACKEND = 'sendfile.backends.nginx'

    if ENV_ROLE == 'stage':
        PROJECT_VERSION = PROJECT_VERSION_BASE + '-beta'
        ALLOWED_HOSTS = [
            '127.0.0.1',
            'localhost',
            '.quect.ru',
            '.quect.herokuapp.com',
        ]

    if ENV_ROLE == 'prod':
        PROJECT_VERSION = PROJECT_VERSION_BASE
        ALLOWED_HOSTS = [
            '.quect.ru',
        ]
else:
    PROJECT_VERSION = PROJECT_VERSION_BASE + '-debug'

ADMINS = (
    ('Phobos', 'dev@quect.ru'),
)

MANAGERS = ADMINS

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_HOST_USER = 'dev@quect.ru'
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

ROOT_URLCONF = 'qc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.global_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'qc.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Asia/Krasnoyarsk'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Parse database configuration from $DATABASE_URL
DATABASES = {'default': dj_database_url.config(conn_max_age=500)}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    ('assets', os.path.join(BASE_DIR, 'templates/assets')),
)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

LOGOUT_URL = reverse_lazy('auth_logout')
LOGIN_URL = reverse_lazy('auth_login')
LOGIN_REDIRECT_URL = reverse_lazy('home')

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CRISPY_TEMPLATE_PACK = 'bootstrap3'

ADMIN_URL_PATH = get_env_variable('ADMIN_URL_PATH')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console', 'mail_admins'],
            'propagate': True
        }
    }
}

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            {'name': 'clipboard', 'items': ['Undo', 'Redo', 'Maximize']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'SpecialChar']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', 'Outdent', 'Indent', 'Blockquote', 'JustifyLeft',
                       'JustifyCenter', 'JustifyRight', 'JustifyBlock', 'TextColor', 'BGColor']},
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', 'RemoveFormat']},
            {'name': 'styles', 'items': ['Format', 'Font', 'FontSize']},
        ],
        'width': '100%',
        'extraPlugins': ','.join(
            [
                'autolink',
                'autoembed',
                'embed',
            ]),
        'forcePasteAsPlainText': True,
        'fontSize_sizes': '10/10px;12/12px;14/14px;16/16px;20/20px;24/24px;36/36px;48/48px;',
        'format_tags': 'p;div',
    },
}

HTML_MINIFY = False
