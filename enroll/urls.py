
from django.conf.urls.defaults import patterns, url
from enroll.views import SignUpView, VerifyAccountView, VerifyPasswordResetView, \
                         LoginView, LogoutView, PasswordResetView
from django.views.decorators.csrf import csrf_protect

urlpatterns = patterns('',
    url(r'^login/$', csrf_protect(LoginView.as_view()), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^signup/$', SignUpView.as_view(), name='enroll_signup'),
    url(r'^verify/([^/]+)/$', VerifyAccountView.as_view(), name='enroll_verify'),
    url(r'^reset/$', PasswordResetView.as_view(), name='enroll_password_reset'),
    url(r'^verify-reset/([^/]+)/$', VerifyPasswordResetView.as_view(), name='enroll_verify_password_reset'),
)