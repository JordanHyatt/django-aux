import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_label = sys.argv[-1]
    else:
        test_label = 'tests'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests([test_label])
    sys.exit(bool(failures))