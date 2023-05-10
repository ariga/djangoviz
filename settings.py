from django.conf import settings as global_settings

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = ["djangoviz", "tests.app1", "tests.app2"]
