from settings import BASE_DIR, SECRET_KEY, INSTALLED_APPS, MIDDLEWARE_CLASSES, WSGI_APPLICATION, ROOT_URLCONF, LANGUAGE_CODE, TIME_ZONE, STATIC_URL
import os

DEBUG = True
TEMPLATE_DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "deekshadb",
        "USER": "postgres",
        "PASSWORD": "shashank",
        "HOST": "localhost",
        
    }
}