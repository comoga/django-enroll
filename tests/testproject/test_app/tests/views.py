from django.test import TestCase
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

class TestSignUpView(TestCase):
    SIGN_UP_ARGS = {
        'username': 'alice',
        'email': 'alice@al.com',
        'password1': 'secret',
        'password2': 'secret',
    }

    def test_signup_view(self):
        response = self.client.post(reverse('enroll_signup'), self.SIGN_UP_ARGS)
        self.assertIsInstance(response, HttpResponseRedirect)


