import os
from pathlib import Path
from dotenv import load_dotenv

# ── Base directory (folder containing manage.py) ──────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── Load .env from project root ───────────────────────────────
load_dotenv(BASE_DIR / '.env')

# ── Security ──────────────────────────────────────────────────
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ── VCare credentials ─────────────────────────────────────────
VCARE_VENDOR_ID = os.environ.get('VCARE_VENDOR_ID', '')
VCARE_USERNAME  = os.environ.get('VCARE_USERNAME', '')
VCARE_PASSWORD  = os.environ.get('VCARE_PASSWORD', '')
VCARE_PIN       = os.environ.get('VCARE_PIN', '')

# ── Hosts ─────────────────────────────────────────────────────
ALLOWED_HOSTS = [
    'goliteapi.golitemobile.com',
    '34.100.195.29',
    'localhost',
    '127.0.0.1',
]

# ── Static & Media ────────────────────────────────────────────
STATIC_URL  = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL   = '/media/'
MEDIA_ROOT  = BASE_DIR / 'media'

# ── Installed Apps ────────────────────────────────────────────
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'apps.blog',
    'apps.products',
    'apps.accounts',
    'apps.plans',
    'apps.coupons',
    'apps.student_discount',
    'apps.first_responder',
    'apps.military_discount',
    'apps.marine_discount',
    'apps.senior_discount',
    'apps.orders',
    'apps.contact',
    'apps.business_contact',
    'apps.newsletter',
    'apps.jobs',
    'apps.search',
    'django_ckeditor_5',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'apps.esim_checker',
]

# ── Middleware ────────────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ── Database ──────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── Password Validators ───────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalisation ──────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Django REST Framework ─────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 9,
}

# ── CORS ──────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://localhost:5173",
    "https://golitereact.vercel.app",
    "https://react.golitemobile.com",
    "https://lakhan-golite.vercel.app",
    "https://golitemobile.com",
    "https://www.golitemobile.com",
    "https://zoikomobile.com",
    "https://driverxmobile.com",
    "https://zoikoorbit.com",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-frontend-origin",
    "x-secret-key",
]

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

# ── Proxy / HTTPS ─────────────────────────────────────────────
USE_X_FORWARDED_HOST        = True
SECURE_PROXY_SSL_HEADER     = ('HTTP_X_FORWARDED_PROTO', 'https')

# ── Email / SMTP ──────────────────────────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtpout.secureserver.net'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = 'info@zoikogroup.com'
EMAIL_HOST_PASSWORD = 'NoxxMC26070%!LGM'
DEFAULT_FROM_EMAIL  = 'Zoiko Group <info@zoikogroup.com>'

# ── CKEditor 5 ────────────────────────────────────────────────
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'link',
            'bulletedList', 'numberedList',
            'blockQuote', 'imageUpload',
            'undo', 'redo',
        ],
    }
}

# ── Jazzmin ───────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    'custom_css': 'css/jazzmin.css',
    'site_title': 'Golite 1',
    'site_header': 'Admin 1',
    'site_logo': 'img/logo.png',
    'site_logo_classes': 'siteLogo',
    'site_brand': '  Admin 1',
    'welcome_sign': 'Welcome to GoLite Admin 1',
    'show_sidebar': True,
    'navigation_expanded': True,
    'topmenu_links': [
        {'name': 'Home', 'url': '/', 'permissions': ['auth.view_user']},
    ],
    'icons': {
        'plans.plantype':   'fas fa-layer-group',
        'plans.plan':       'fas fa-list',
        'coupons.coupon':   'fa-sharp fa-solid fa-ticket',
        'auth.user':        'fas fa-user',
        'auth.group':       'fas fa-users',
    },
}