"""Configurações do projeto TECAB."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_list(name, default):
    return [v.strip() for v in os.environ.get(name, default).split(',') if v.strip()]


SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-insecure-troque-esta-chave-em-producao')
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,[::1]')
CSRF_TRUSTED_ORIGINS = env_list('DJANGO_CSRF_TRUSTED_ORIGINS', '')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'website',
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

X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
# Ative (=1) quando o site estiver atrás de HTTPS.
if os.environ.get('DJANGO_HTTPS', '0') == '1':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30

ROOT_URLCONF = 'tecab.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'website.context_processors.site',
            ],
        },
    },
]

WSGI_APPLICATION = 'tecab.wsgi.application'

# Produção (Docker): PostgreSQL, ativado quando POSTGRES_DB está definido.
# Desenvolvimento e testes: SQLite local.
if os.environ.get('POSTGRES_DB'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ['POSTGRES_DB'],
            'USER': os.environ.get('POSTGRES_USER', 'tecab'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
            'HOST': os.environ.get('POSTGRES_HOST', 'db'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
            'CONN_MAX_AGE': 60,
            'CONN_HEALTH_CHECKS': True,
        }
    }
    # Banco SQLite da versão anterior: se existir, a migration website.0003 copia os dados dele
    # para o PostgreSQL (uma única vez, com o banco novo vazio).
    _sqlite_legado = os.environ.get('DJANGO_SQLITE_LEGADO', '')
    if _sqlite_legado and Path(_sqlite_legado).is_file():
        DATABASES['legado'] = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': Path(_sqlite_legado)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': Path(os.environ.get('DJANGO_DB_PATH', BASE_DIR / 'db.sqlite3')),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Permite entrar com nome de usuário ou e-mail ("Login ou E-mail").
AUTHENTICATION_BACKENDS = ['website.backends.UsernameOrEmailBackend']

LOGIN_URL = 'website:login'
LOGIN_REDIRECT_URL = 'website:area_colaborador'
LOGOUT_REDIRECT_URL = 'website:home'

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Fortaleza'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    # Os CSS originais referenciam arquivos inexistentes no servidor de origem, por isso
    # não usamos o storage com manifesto (que falharia no collectstatic).
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}

MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.environ.get('DJANGO_MEDIA_ROOT', BASE_DIR / 'media'))

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# E-mail: por padrão imprime no console; configure SMTP pelas variáveis de ambiente.
EMAIL_BACKEND = os.environ.get('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('DJANGO_EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('DJANGO_EMAIL_PORT', '25'))
EMAIL_HOST_USER = os.environ.get('DJANGO_EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('DJANGO_EMAIL_USE_TLS', '0') == '1'
DEFAULT_FROM_EMAIL = os.environ.get('DJANGO_DEFAULT_FROM_EMAIL', 'TECAB <no-reply@tecab.srv.br>')

# Destinatários dos formulários "Contato" e "Trabalhe Conosco".
TECAB_CONTATO_DESTINATARIOS = env_list('TECAB_CONTATO_DESTINATARIOS', 'comercial@tecab.srv.br')
TECAB_INTEGRIDADE_DESTINATARIOS = env_list('TECAB_INTEGRIDADE_DESTINATARIOS', 'lgpd@tecab.srv.br')
TECAB_CURRICULO_MAX_BYTES = int(os.environ.get('TECAB_CURRICULO_MAX_BYTES', str(5 * 1024 * 1024)))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'WARNING'},
}
