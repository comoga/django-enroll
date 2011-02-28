from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.forms.models import ModelFormMetaclass
from django.contrib.auth.forms import AuthenticationForm as DjangoAuthenticationForm
from django.contrib.auth import authenticate

from enroll.models import VerificationKey
from enroll.validators import UniqueUsernameValidator, UniqueEmailValidator
from enroll import import_class
from enroll.signals import post_registration

class BaseSignUpFormMetaclass(ModelFormMetaclass):
    '''Adds defined field validators to class fields'''

    def __new__(cls, name, bases, attrs):
        new_class = super(BaseSignUpFormMetaclass, cls).__new__(cls, name, bases, attrs)
        for field, validators in new_class.field_validators.iteritems():
            if field not in new_class.base_fields:
                #TODO logger.warning - validator for non-existing field on model
                continue
            for validator in validators:
                if isinstance(validator, basestring):
                    validator = import_class(validator)()
                elif isinstance(validator, type):
                    validator = validator()
                new_class.base_fields[field].validators.append(validator)
        return new_class


class BaseSignUpForm(forms.ModelForm):
    """If username is not between fields use email as user's username"""

    __metaclass__ = BaseSignUpFormMetaclass

    verification_required = getattr(settings , 'ENROLL_ACCOUNT_VERIFICATION_REQUIRED', True)

    field_validators = getattr(settings , 'ENROLL_SIGNUP_FORM_VALIDATORS', {
        'username': [ UniqueUsernameValidator ],
        'email': [ UniqueEmailValidator ],
    })

    class Meta:
        model = User
        fields = getattr(settings , 'ENROLL_SIGNUP_FORM_USER_FIELDS', ('username', 'email'))

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(BaseSignUpForm, self).__init__(*args, **kwargs)
        self.request = request

    def create_activation_key(self, user):
        return VerificationKey.objects.create_user_key(user)

    def get_username(self, cleaned_data):
        """User email as username if username field is not present"""
        return self.cleaned_data.get('username', self.cleaned_data.get('email'))

    def save(self):
        #use UserManager to create instance instead of saving self.instance
        password = self.cleaned_data['password1']
        email = self.cleaned_data.get('email')
        username = self.get_username(self.cleaned_data)

        user = User.objects.create_user(username, email, password)

        if self.verification_required:
            user.is_active = False
            user.save()
            activation_key = self.create_activation_key(user)
        else:
            activation_key = None

        post_registration.send(sender=user.__class__, user=user, request=self.request, activation_key=activation_key)
        return user


class SignUpForm(BaseSignUpForm):

    password1 = forms.CharField(required=True, widget=forms.PasswordInput, label=_(u'password'), min_length=getattr(settings , 'ENROLL_PASSWORD_MIN_LENGTH', 4))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput, label=_(u'password (again)'))

    def check_username_derived_password(self, username, password):
        username = username.lower()
        password = password.lower()
        if password.startswith(username) or password[::-1].startswith(username):
            raise forms.ValidationError(_(u'Password cannot be derived from username'))

    def clean(self):
        if 'password1' in self.cleaned_data:
            if getattr(settings, 'ENROLL_FORBID_USERNAME_DERIVED_PASSWORD', False) and 'username' in self.cleaned_data:
                self.check_username_derived_password(self.cleaned_data['username'], self.cleaned_data['password1'])
            if 'password2' in self.cleaned_data:
                if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                    raise forms.ValidationError(_(u'You must type the same password each time'))
        return super(SignUpForm, self).clean()


class RequestPassingAuthenticationForm(DjangoAuthenticationForm):
    """
        Pass request to backend.
        Also patched to allow login by inactive users. Maybe it will be fixed in Django 1.3
    """
    supports_inactive_user = getattr(settings, 'ENROLL_AUTH_FORM_SUPPORTS_INACTIVE_USER', False)

    #copied and patched from parent class
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password, request=self.request)
            if self.user_cache is None:
                raise forms.ValidationError(_("Please enter a correct username and password. Note that both fields are case-sensitive."))
            elif not self.supports_inactive_user and not self.user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive."))
        self.check_for_test_cookie()
        return self.cleaned_data

