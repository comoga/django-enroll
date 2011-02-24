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

class ActivationKeyManager(models.Manager):

    def create_user_key(self, user, account_activation_days=None):
        salt = str(random.random())
        key = sha_constructor(salt+user.username).hexdigest()
        key = key[:getattr(settings, 'ENROLL_ACTIVATION_KEY_LENGTH', 12)]

        if account_activation_days is None: #can be False
            account_activation_days = getattr(settings, 'ENROLL_ACTIVATION_VALID_DAYS', 30)

        if account_activation_days:
            expire_date = datetime.now() + timedelta(days=account_activation_days)
        else:
            expire_date = None
        return self.create(user=user, key=key, expire_date=expire_date)


class ActivationKey(models.Model):
    user = models.ForeignKey(User)
    key = models.CharField(_('activation key'), max_length=40)
    expire_date = models.DateTimeField(null=True, blank=True)

    objects = ActivationKeyManager()

    def __unicode__(self):
        return self.key

    def activate_user(self):
        self.user.is_active = True;
        self.user.save()

    def notify_user(self, subject=None, mail_template="registration/activation_email.txt"):
        """Convenient method to notify user after registration"""

        site = Site.objects.get_current()
        if not subject:
            subject = _("%s: user registration confirmation") % site.name

        message = loader.render_to_string(mail_template, {
            'user': self.user,
            'activation_key': self.key,
            'expire_date': self.expire_date,
            'site': site,
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email])


""" To override notification behavior, set settings.ENROLL_ACTIVATION_SEND_EMAIL to False
and define your own signal"""

@receiver(post_save, sender=ActivationKey)
def post_register(sender, **kwargs):
    if getattr(settings, 'ENROLL_ACTIVATION_SEND_EMAIL', True) and kwargs.get('created'):
        instance = kwargs.get('instance')
        instance.notify_user()

