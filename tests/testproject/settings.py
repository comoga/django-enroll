DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',

    'enroll',

    'testproject.test_app',
)

TEMPLATE_LOADERS = (
    'testproject.test_app.loaders.FakeTemplateLoader',
)

ROOT_URLCONF = 'testproject.urls'
SITE_ID = 1

LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

ENROLL_AUTH_BACKEND_LOGIN_ATTRIBUTES = ['username', 'email']
ENROLL_FORBID_USERNAME_DERIVED_PASSWORD = True


