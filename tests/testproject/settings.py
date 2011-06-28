DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',

    'enroll',

    'testproject.test_app',
)

ROOT_URLCONF = 'testproject.urls'


ENROLL_AUTH_BACKEND_LOGIN_ATTRIBUTES = ['username', 'email']

