import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-yrl1t#yfkgr^a)ukj%zfj(vzl=1+0#ja6#jj!(x_x)_tlf@5fk')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool, default=False)

ALLOWED_HOSTS = [
    host.strip() for host in config("ALLOWED_HOSTS", default="").split(",")
    if host.strip()  # Remove espaços em branco e ignore entradas vazias
]

if not DEBUG:

    CSRF_TRUSTED_ORIGINS = [
        origin.strip() for origin in config("CSRF_TRUSTED_ORIGINS", default="").split(",")
        if origin.strip()  # Remove espaços em branco e ignore entradas vazias
    ]

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Força o redirecionamento permanente (301) de HTTP para HTTPS
#    SECURE_SSL_REDIRECT = True  # Defina como True em produção

    # Isenta a rota /health/ do redirecionamento para HTTPS
    # SECURE_REDIRECT_EXEMPT = [r'^health/$']

    # Protege o cookie de sessão contra envio em conexões não-seguradas
    SESSION_COOKIE_SECURE = True 

    # Protege o cookie do CSRF contra envio em conexões não-seguradas
    CSRF_COOKIE_SECURE = True 

    # Define a política SameSite para os cookies de sessão e CSRF
    SESSION_COOKIE_SAMESITE = "Lax"

    # Define a política SameSite para os cookies de sessão e CSRF
    CSRF_COOKIE_SAMESITE = "Lax"

    # Habilita o HSTS com duração de 1 ano (em segundos)
    SECURE_HSTS_SECONDS = 31536000  # 1 ano 

    # Inclui subdomínios na regra do HSTS (opcional, remova se usar subdomínios HTTP)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    # Garante que o HSTS não seja removido acidentalmente
    SECURE_HSTS_PRELOAD = True  # Defina como True se você quiser enviar seu site para a lista de pré-carregamento HSTS


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'material',
    'home',
    'usuarios',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

LOGIN_URL = '/admin/login/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'pt-BR'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}
