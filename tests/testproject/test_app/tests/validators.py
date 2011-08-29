#coding: utf-8

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from enroll.validators import *

class ValidatorTest(TestCase):

    def test_plain_username_validator(self):
        validator = PlainUsernameValidator()
        #if valid no exception should be thrown
        validator('bob')
        validator('alice_007')
        validator('bob@domain.com')
        with self.assertRaises(ValidationError):
            self.assertFalse(validator('bob$'))
        with self.assertRaises(ValidationError):
            self.assertFalse(validator('Černý bob'))

    def test_unique_username_validator(self):
        User.objects.create_user('bob', 'bob@domain.com', 'secret')
        validator = UniqueUsernameValidator()
        validator('alice')
        with self.assertRaises(ValidationError):
            self.assertFalse(validator('bob'))

    def test_unique_email_validator(self):
        User.objects.create_user('bob', 'bob@domain.com', 'secret')
        validator = UniqueEmailValidator()
        validator('bob')
        validator('somemail@mail.com')
        with self.assertRaises(ValidationError):
            self.assertFalse(validator('bob@domain.com'))

    def test_email_domain_validator(self):
        validator = EmailDomainValidator([ 'xxx.com', 'banned.name'])
        validator('bob@domain.com')
        with self.assertRaises(ValidationError):
            validator('bob@xxx.com')
        with self.assertRaises(ValidationError):
            validator('alice@banned.name')

    def test_too_simple_password_validator(self):
        validator = TooSimplePasswordValidator()
        validator('Rmc74s7lx')
        with self.assertRaises(ValidationError):
            validator('abc')
        with self.assertRaises(ValidationError):
            validator('1111')
        with self.assertRaises(ValidationError):
            validator('LMNOPQ')
        with self.assertRaises(ValidationError):
            validator('987654')
