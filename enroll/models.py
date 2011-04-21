import random
from datetime import datetime, timedelta

from django.db import models
from django.core.mail import send_mail
from django.template import loader
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save

class VerificationTokenManager(models.Manager):

    def create_token(self, user, verification_type, email=None, account_activation_days=None):
        salt = str(random.random())
        key = sha_constructor(salt+user.username.encode('ascii', 'ignore')).hexdigest()
        key = key[:getattr(settings, 'ENROLL_VERIFICATION_TOKEN_LENGTH', 12)]

        if account_activation_days is None: #can be False
            account_activation_days = getattr(settings, 'ENROLL_VERIFICATION_TOKEN_VALID_DAYS', 14)

        if account_activation_days:
            expire_date = datetime.now() + timedelta(days=account_activation_days)
        else:
            expire_date = None
        return self.create(user=user, verification_type=verification_type, email=email, key=key, expire_date=expire_date)


class VerificationToken(models.Model):

    TYPE_SIGN_UP = 'S'
    TYPE_EMAIL_CHANGE = 'E'
    TYPE_PASSWORD_RESET = 'P'

    VERIFICATION_TYPE_CHOICES = [
        (TYPE_SIGN_UP, _('Sign Up')),
        (TYPE_EMAIL_CHANGE, _('Email change')),
        (TYPE_PASSWORD_RESET, _('Password reset')),
    ]

    user = models.ForeignKey(User)
    key = models.CharField(_('activation key'), max_length=40)
    expire_date = models.DateTimeField(null=True, blank=True)
    verification_type = models.CharField(max_length=1, choices=VERIFICATION_TYPE_CHOICES)
    email = models.EmailField(_('e-mail address'), null=True, blank=True)

    objects = VerificationTokenManager()

    def __unicode__(self):
        return self.key

    def activate_user(self):
        self.user.is_active = True
        self.user.save()

    def notify_user(self, subject, mail_template):
        """Convenient method to notify user after registration"""
        message = loader.render_to_string(mail_template, {
            'user': self.user,
            'activation_key': self.key,
            'expire_date': self.expire_date,
            'site': Site.objects.get_current(),
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email])


""" To override notification behavior, set settings.ENROLL_SEND_VERIFICATION_EMAIL to False
and define your own signal.
"""
@receiver(post_save, sender=VerificationToken)
def post_key_create(sender, **kwargs):
    if getattr(settings, 'ENROLL_SEND_VERIFICATION_EMAIL', True) and kwargs.get('created'):
        token = kwargs.get('instance')
        site = Site.objects.get_current()
        if token.verification_type == VerificationToken.TYPE_SIGN_UP:
            subject = _("%s: user registration confirmation") % site.name
            template =  'registration/activation_email.txt'
        elif token.verification_type == VerificationToken.TYPE_PASSWORD_RESET:
            subject = _("%s: passwotd reset") % site.name
            template =  'registration/password_reset_email.html'
        elif token.verification_type == VerificationToken.TYPE_EMAIL_CHANGE:
            subject = _("%s: email change confirmation") % site.name
            template =  'registration/email_change_email.html'
        token.notify_user(subject, template)

