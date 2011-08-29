from django.test import TestCase
from django.contrib.auth.models import User
from enroll.backends import ModelBackend


class TestModelBackend(TestCase):

    def test_authenticate(self):
        User.objects.create_user('bob', 'bob@domain.com', 'secret')

        backend = ModelBackend()
        self.assertIsInstance(backend.authenticate('bob', 'secret'), User)
        self.assertIsInstance(backend.authenticate('bob@domain.com', 'secret'), User)
        self.assertIsNone(backend.authenticate('bob', 'invald_password'))
