#!/usr/bin/env python

"""Borrowed from Carl Meyer's django-adminfiles."""

import os
import sys

testapp_dir = os.path.dirname(os.path.abspath(__file__))
enroll_dir = os.path.dirname(testapp_dir)
sys.path.insert(0, testapp_dir)
sys.path.insert(0, enroll_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'testproject.settings'

from django.test.simple import DjangoTestSuiteRunner

def main():
    runner = DjangoTestSuiteRunner()
    failures = runner.run_tests(['test_app'], verbosity=1, interactive=True)
    sys.exit(failures)

if __name__ == '__main__':
    main()
