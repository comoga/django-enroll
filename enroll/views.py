import urlparse
from datetime import datetime

from django import http
from django.views.generic.edit import BaseCreateView, FormView
from django.views.generic.base import TemplateResponseMixin, View, TemplateView
from django.contrib.auth import login as auth_login, get_backends
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.http import HttpResponseNotFound
from django.utils.translation import ugettext_lazy as _

from enroll.forms import SignUpForm, RequestPassingAuthenticationForm,\
    PasswordResetStepOneForm, PasswordResetStepTwoForm, ChangeEmailForm
from enroll.models import VerificationToken
from enroll.signals import post_login, post_logout

# --------------  Helper Views ----------------------

class SuccessMessageMixin(object):
    """Mixin to create django.contrib.messages"""
    success_message = None

    def get_success_message(self):
        return self.success_message

    def send_success_message(self):
        msg = self.get_success_message()
        if msg:
            from django.contrib import messages
            messages.add_message(self.request, messages.INFO, msg)


class FailureMessageMixin(object):
    """Mixin to create django.contrib.messages"""
    failure_message = None

    def get_failure_message(self):
        return self.failure_message

    def send_failure_message(self):
        msg = self.get_failure_message()
        if msg:
            from django.contrib import messages
            messages.add_message(self.request, messages.WARNING, msg)


class AutoLoginMixin(object):
    """Provides method to log user"""

    login_on_success = getattr(settings, 'ENROLL_AUTO_LOGIN', True)

    def login_user(self, user):
        anonymous_session_data = dict(self.request.session.items())
        for backend in get_backends():
            if not user.is_active:
                #inactive user login is supported by Django 1.3
                if not getattr(backend, 'supports_inactive_user', False):
                    continue
            #user must be annotated with backend
            user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            break

        auth_login(self.request, user)
        post_login.send(
            sender=user.__class__,
            request=self.request,
            user=user,
            session_data=anonymous_session_data
        )


class SuccessMessageFormView(SuccessMessageMixin, FormView):

    def form_valid(self, form):
        response = super(SuccessMessageFormView, self).form_valid(form)
        self.send_success_message()
        return response


# --------------  Regular Views ----------------------

class SignUpView(TemplateResponseMixin, SuccessMessageMixin, AutoLoginMixin, BaseCreateView):
    """See also BaseSignUpForm. It contains almost all logic around user registration."""
    template_name = 'registration/registration_form.html'
    form_class = SignUpForm
    success_url = '/'

    def get_form_kwargs(self):
        kwargs = dict(request=self.request)
        kwargs.update(super(SignUpView, self).get_form_kwargs())
        return kwargs

    def form_valid(self, form):
        response = super(SignUpView, self).form_valid(form)

        if self.login_on_success:
            #try to login here is OK. Following method log inactive user only if
            #backend with such support exists
            self.login_user(self.object)

        self.send_success_message()
        return response


class VerifyAccountView(SuccessMessageMixin, FailureMessageMixin, AutoLoginMixin, View):
    success_url = getattr(settings, 'LOGIN_REDIRECT_URL')
    failure_url = '/'

    def get(self, request, verification_key):
        try:
            token = VerificationToken.objects.get(
                            key=verification_key,
                            expire_date__gt=datetime.now(),
                            verification_type=VerificationToken.TYPE_SIGN_UP
                        )
        except VerificationToken.DoesNotExist:
            return self.on_failure(request, verification_key)
        return self.on_success(request, token)

    def on_success(self, request, token):
        user = token.user

        token.activate_user()
        token.delete()

        if self.login_on_success:
            self.login_user(user)

        self.send_success_message()
        return http.HttpResponseRedirect(self.success_url)

    def on_failure(self, request, verification_key):
        self.send_failure_message()
        return http.HttpResponseRedirect(self.failure_url)


class PasswordResetView(SuccessMessageFormView):
    template_name = 'registration/password_reset_form.html'
    form_class = PasswordResetStepOneForm
    success_url = '/'
    success_message = _('An verification link has been sent to the your e-mail address.')

    def get_form_kwargs(self):
        kwargs = dict(request=self.request)
        kwargs.update(super(PasswordResetView, self).get_form_kwargs())
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(PasswordResetView, self).form_valid(form)


class VerifyPasswordResetView(AutoLoginMixin, SuccessMessageFormView, FailureMessageMixin):
    template_name ='registration/password_reset_confirm.html'
    form_class = PasswordResetStepTwoForm
    success_url = '/'
    success_message = _('Your password has been updated.')
    login_on_success = getattr(settings, 'ENROLL_AUTO_LOGIN', True)
    failure_url = '/'
    failure_message = _('Invalid verification link.')

    def get_form_kwargs(self):
        kwargs = dict(request=self.request, user=self.token.user)
        kwargs.update(super(VerifyPasswordResetView, self).get_form_kwargs())
        return kwargs

    @method_decorator(never_cache)
    def dispatch(self, request, verification_key, *args, **kwargs):
        self.request = request
        try:
            self.token = VerificationToken.objects.get(key=verification_key)
        except VerificationToken.DoesNotExist:
            return self.on_failure(request, verification_key)
        return super(VerifyPasswordResetView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        if self.login_on_success:
            self.login_user(self.token.user)
        self.token.delete()
        return super(VerifyPasswordResetView, self).form_valid(form)

    def on_failure(self, request, verification_key):
        self.send_failure_message()
        return http.HttpResponseRedirect(self.failure_url)


class ChangeEmailView(SuccessMessageFormView):
    form_class = ChangeEmailForm
    template_name = 'registration/change_email.html'
    success_url = '/'
    success_message = _('An activation link has been sent to your new address.')

    def get_form_kwargs(self):
        kwargs = dict(request=self.request)
        kwargs.update(super(ChangeEmailView, self).get_form_kwargs())
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(ChangeEmailView, self).form_valid(form)


class VerifyEmailChangeView(SuccessMessageMixin, FailureMessageMixin, View):
    success_url = '/'
    success_message = _('Your e-mail address has been updated.')
    failure_url = '/'
    failure_message = _('Invalid activation link.')

    def get(self, request, verification_key):
        try:
            token = VerificationToken.objects.get(
                            key=verification_key,
                            expire_date__gt=datetime.now(),
                            verification_type=VerificationToken.TYPE_EMAIL_CHANGE
                        )
        except VerificationToken.DoesNotExist:
            return self.on_failure(request, verification_key)
        return self.on_success(request, token)

    def on_success(self, request, token):
        user = token.user
        user.email = token.email
        user.save()
        token.delete()

        self.send_success_message()
        return http.HttpResponseRedirect(self.success_url)

    def on_failure(self, request, verification_key):
        self.send_failure_message()
        return http.HttpResponseRedirect(self.failure_url)


class LoginView(FormView):
    form_class = RequestPassingAuthenticationForm
    template_name = 'registration/login.html'
    redirect_field_name = REDIRECT_FIELD_NAME
    success_url = getattr(settings, 'LOGIN_REDIRECT_URL')

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def get_redirect_to(self):
        return self.request.REQUEST.get(self.redirect_field_name, '')

    def get_success_url(self):
        redirect_to = self.get_redirect_to()
        netloc = urlparse.urlparse(redirect_to)[1]
        # Light security check -- make sure redirect_to isn't garbage.
        if not redirect_to or ' ' in redirect_to:
            redirect_to = super(LoginView, self).get_success_url()
        # Heavier security check -- don't allow redirection to a different
        # host.
        elif netloc and netloc != self.request.get_host():
            redirect_to = super(LoginView, self).get_success_url()
        return redirect_to

    def form_valid(self, form):
        anonymous_session_data = dict(self.request.session.items())
        # Okay, security checks complete. Log the user in.
        user = form.get_user()
        auth_login(self.request, user)

        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        post_login.send(sender=user.__class__, request=self.request, user=user, session_data=anonymous_session_data)
        return super(LoginView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        self.request.session.set_test_cookie()
        current_site = get_current_site(self.request)
        context = {
            self.redirect_field_name: self.get_redirect_to(),
            'site': current_site,
            'site_name': current_site.name,
        }
        context.update(**kwargs)
        return context


class LogoutView(TemplateView):
    url = getattr(settings, 'LOGOUT_REDIRECT_URL')
    template_name = 'registration/logged_out.html'
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_redirect_url(self, **kwargs):
        return self.request.REQUEST.get(self.redirect_field_name, self.url)

    def get_context_data(self, **kwargs):
        current_site = get_current_site(self.request)
        context = dict(site=current_site, site_name=current_site.name, title=_('Logged out'))
        context.update(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated():
            from django.contrib.auth import logout
            logout(request)
            post_logout.send(sender=request.user.__class__, request=request, user=user)

        url = self.get_redirect_url()
        if url:
            return http.HttpResponseRedirect(url)
        return super(LogoutView, self).get(self, request, *args, **kwargs)
