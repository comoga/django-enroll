from django.conf import settings
from django.http import HttpResponseRedirect

from enroll.forms import RequestPassingAuthenticationForm
from enroll.views import LoginMixin


class InlineLoginMiddleware(LoginMixin):

    def process_request(self, request):
        if request.method == 'POST' and request.POST.get('form_id') == 'loginform':
            form = RequestPassingAuthenticationForm(request=request, data=request.POST)
            if form.is_valid():
                self.login_user(form.get_user())

                next = request.META.get('HTTP_REFERER', None)
                if not next:
                    next = getattr(settings, 'LOGIN_REDIRECT_URL')
                if not next:
                    next = '/'
                return HttpResponseRedirect(next)
        else:
            form = RequestPassingAuthenticationForm(request=request, initial={'form_id': 'loginform'})
        request.login_form = form

    def process_template_response(self, request, response):
        response.context_data['login_form'] = request.login_form
        return response




