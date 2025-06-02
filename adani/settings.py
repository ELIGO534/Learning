from pathlib import Path
import os
import dj_database_url
import environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()  # Reads the .env file

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your_default_secret_key')  # Fetch from environment variables

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['learning-1-a6c2.onrender.com','eligo.space','www.eligo.space','localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ["https://eligo.space", "https://www.eligo.space","https://learning-1-a6c2.onrender.com"]
SECURE_SSL_REDIRECT = False  # Ensures all traffic is redirected to HTTPS


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'whitenoise.runserver_nostatic',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'adani.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'adani.wsgi.application'

# Database configuration
DATABASES = {
    'default': env.db(),  # This line loads the DATABASE_URL from .env automatically
}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Corrected STATICFILES_DIRS (remove duplicate)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # Only this line is needed
]

# For production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Production collection

LOGIN_URL = '/login/'  # Change to your login URL


# Media files (profile pictures, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Ensure all static files are collected into the STATIC_ROOT during deployment
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default backend
    'myapp.backends.PhoneBackend',  # Your custom backend
]

# Custom user model
AUTH_USER_MODEL = 'myapp.CustomUser'

# CSRF trusted origins

# CSRF settings for security
CSRF_COOKIE_SAMESITE = 'Lax'  # 'Strict' for more security
CSRF_COOKIE_SECURE = False  # Disable secure cookies for testing
CSRF_COOKIE_HTTPONLY = False  # Disable HTTPOnly for testing


# Security: Use secure cookies in production
