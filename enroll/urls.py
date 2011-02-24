
from django.conf.urls.defaults import patterns, url
from enroll.views import SignUpView, VerifyAccountView, LoginView, LogoutView
from django.views.decorators.csrf import csrf_protect

urlpatterns = patterns('',
    url(r'^login/$', csrf_protect(LoginView.as_view()), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^signup/$', SignUpView.as_view(), name='enroll_signup'),
    url(r'^verify/([^/]+)/$', VerifyAccountView.as_view(), name='enroll_verify'),
)