from django.conf import settings
from django.http import HttpResponseRedirect

from enroll.forms import RequestPassingAuthenticationForm
from enroll.views import LoginMixin


class InlineLoginMiddleware(LoginMixin):

    def process_request(self, request):
        form = None
        if request.method == 'POST' and request.POST.get('form_id') == 'loginform':
            form = RequestPassingAuthenticationForm(request=request, data=request.POST)
            if form.is_valid():
                self.login_user(request, form.get_user())

                next = request.META.get('HTTP_REFERER', None)
                if not next:
                    next = getattr(settings, 'LOGIN_REDIRECT_URL')
                if not next:
                    next = '/'
                return HttpResponseRedirect(next)
            request.login_form = form
        else:
            if not hasattr(request, 'user') or request.user.is_anonymous():
                request.session.set_test_cookie()
                request.login_form = RequestPassingAuthenticationForm(request=request, initial={'form_id': 'loginform'})

    def process_template_response(self, request, response):
        if hasattr(request, 'login_form'):
            response.context_data['login_form'] = request.login_form
        return response




