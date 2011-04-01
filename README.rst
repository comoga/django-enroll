Features
========

Djnago-enroll is inspired with django-registration.

Motivation to create new user registration library is to provide
more flexible app with easily configurable behavior and ability
to easy override of any part.

To fulfill such aim new Django classed base views are very helpful.
So django-enroll requires Django 1.3 (it means trunk development version nowadays).

Installation
============


Functionality overriding
========================

There are three ways to change django-enroll default functionality.

1. passing argument to classed based view (usually from URL mapping)
This is Django classed base view feature. It allows change any class property
by passing new value to constructor kwargs. (see Django classed base view documentation)

2. Set proper variable in your settings.py (see settings section)

3. Override view class. The most complex but the most flexible way.


Views
=====

Supports django.contrib.messages - see  SuccessMessageMixin, FailureMessageMixin

Form views can end (on success) with redirect or display template.

SignUpView
VerifyAccountView
LoginView
LogoutView
PasswordResetView
VerifyPasswordResetView

Settings variables
==================

All settings are optional. Defaults are:

::

    ENROLL_SIGNUP_FORM_USER_FIELDS = ('username', 'email')
    ENROLL_FORM_VALIDATORS = {
        'username': [
            'enroll.validators.UniqueUsernameValidator'
        ],
        'email': [
            'enroll.validators.UniqueEmailValidator'
        ],
    } #used by SignUpForm and PasswordResetForm (if contains password validator)

    ENROLL_EMAIL_BANNED_DOMAINS = []     #(enable EmailDomainValidator to have effect)
    ENROLL_PASSWORD_MIN_LENGTH = 4
    ENROLL_FORBIDDEN_PASSWORDS = []      #(enable TooSimplePasswordValidator to have effect)
    ENROLL_FORBID_USERNAME_DERIVED_PASSWORD = False

    ENROLL_AUTH_BACKEND_LOGIN_ATTRIBUTES  = [ username ]  #(use enroll.backends.ModelBackend to have effect)
    ENROLL_AUTH_BACKEND_INACTIVE_USER = True  #is allowed login authentication by inactive user

    ENROLL_VERIFICATION_TOKEN_VALID_DAYS = 14 #unlimited if False
    ENROLL_VERIFICATION_TOKEN_LENGTH = 12
    ENROLL_SEND_VERIFICATION_EMAIL = True
    ENROLL_AUTO_LOGIN = True
    ENROLL_AUTO_VERIFY = True

    LOGIN_REDIRECT_URL #(also used by django auth)
    LOGOUT_REDIRECT_URL


TODO
====

Email change usecase.
Password change usecase.


