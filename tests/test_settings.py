import os

SECRET_KEY = 'fake-test-key'

INSTALLED_APPS = [
    "tests", "django_aux_timeperiods",
]


name = os.getenv('DB_NAME', 'aux_test')
user = os.getenv('DB_USER', 'postgres')
host = os.getenv('DB_HOST', 'localhost')
password = os.getenv('DB_PASSWORD')
port = os.getenv('DB_PORT', '5432')

DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.postgresql',
        'NAME': name,
        'USER': user,
        'PASSWORD': password,
        'HOST': host,
        'PORT': port,
    },
}
