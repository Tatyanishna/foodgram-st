from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.core.management import call_command


def load_initial_data(sender, **kwargs):
    call_command("load_initial_data")


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        post_migrate.connect(load_initial_data, sender=self)
