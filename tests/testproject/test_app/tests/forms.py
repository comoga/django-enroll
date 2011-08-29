from django.test import TestCase
from enroll.forms import SignUpForm, BaseSignUpForm
from django.contrib.auth.models import User

class TestSignUpForm(TestCase):

    FORM_DATA = {
        'username': 'alice',
        'email': 'alice@al.com',
        'password1': 'secret',
        'password2': 'secret',
    }

    def test_save(self):
        form = SignUpForm(request={}, data=self.FORM_DATA)
        form.full_clean()
        form.save()
        user = User.objects.get(username=self.FORM_DATA['username'])
        self.assertEquals(self.FORM_DATA['email'], user.email)
        self.assertEquals(user.is_active, False)


    def test_auto_verify_user(self):
        form = SignUpForm(request={}, data=self.FORM_DATA)
        form.auto_verify_user = True
        form.full_clean()
        form.save()
        user = User.objects.get(username=self.FORM_DATA['username'])
        self.assertEquals(user.is_active, True)

    def test_unique_username(self):
        #validator should be in defualt
        User.objects.create_user(self.FORM_DATA['username'], 'another@email.com', 'secret')
        form = SignUpForm(request={}, data=self.FORM_DATA)
        form.full_clean()
        self.assertTrue(form.errors)

    #HARD TO TEST, REFACTOR SOURCE, REMOVE UNCHANGEABLE GLOBAL SETTINGS

#    def test_email_act_as_username(self):
#        from django.conf import settings
#        try:
#            data = self.FORM_DATA.copy()
#            del data['username']
#            settings.ENROLL_SIGNUP_FORM_USER_FIELDS = ['email', ]
#            form = SignUpForm(request={}, data=data)
#            form.full_clean()
#            print form.errors
#            form.save()
#            self.assertEquals(1, User.objects.get(username=self.FORM_DATA['email']).count())
#        finally:
#            del settings.ENROLL_SIGNUP_FORM_USER_FIELDS



