import string, re

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.validators import RegexValidator


class PlainUsernameValidator(RegexValidator):
    regex = re.compile(r'^[-+@\.\w]+$')
    message = _(u'Only letters, digits and -+.@ characters are allowed.')
    code = None


class UniqueUsernameValidator(object):

    message = _(u'This username is already taken. Please choose another.')

    def __call__(self, value):
        #import traceback
        #traceback.print_stack()
        if User.objects.filter(username__iexact=value.strip()).count():
            raise ValidationError(self.message)


class UniqueEmailValidator(object):

    message = _(u'This email address is already in use. Please supply a different email address.')

    def __call__(self, value):
        if User.objects.filter(email__iexact=value.strip()).count():
            raise ValidationError(self.message)


class EmailDomainValidator(object):

    message = _(u'Registration using email on %s domain is prohibited. Please supply a different email address.')

    def __init__(self, banned_domains=None):
        self.banned_domains = banned_domains or getattr(settings , 'ENROLL_EMAIL_BANNED_DOMAINS', [])

    def __call__(self, value):
        try:
            email_domain = value.strip().split('@')[1]
        except IndexError:
            return
        if email_domain in self.banned_domains:
            raise ValidationError(self.message % email_domain)


class PasswordComplexityPolicyValidator(object):

    def __call__(self, value):
        #TODO
        raise NotImplementedError()


class TooSimplePasswordValidator(object):

    LOWERCASE_SEQUENCE = 2 * string.lowercase
    DIGIT_SEQUENCE = 2 * string.digits

    def validate_sequnce(self, password, sequence, message):
        if password in sequence or password[::-1] in sequence:
            raise ValidationError(message)

    def __init__(self, min_unique_chars=3):
        self.min_unique_chars = min_unique_chars

    def __call__(self, password):
        #Case sensitive validations
        if len(set(password)) < self.min_unique_chars:
            raise ValidationError(_(u'Password must contains at least %d unique characters') % self.min_unique_chars)

        #Case insensitive validations
        password = password.lower()
        self.validate_sequnce(password, self.LOWERCASE_SEQUENCE, _(u'Password cannot be ascending or descending sequence.'))
        self.validate_sequnce(password, self.DIGIT_SEQUENCE, _(u'Password cannot be ascending or descending sequence.'))
        self.validate_sequnce(password, getattr(settings , 'ENROLL_FORBIDDEN_PASSWORDS', []), _(u'Password is not allowed.'))

