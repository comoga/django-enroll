from django.conf.urls.defaults import patterns, include

from django.http import HttpResponse

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^enroll/', include('enroll.urls')),
    (r'^$', lambda req : HttpResponse("ok")),
)

