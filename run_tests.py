import os
import sys
import django
from django.test.runner import DiscoverRunner

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")


def run_tests():
    django.setup()
    test_runner = DiscoverRunner()
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))


if __name__ == "__main__":
    run_tests()
