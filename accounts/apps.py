from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        """ Load monkey patching. """
        # For multiple apps, it should not matter which one you do this
        from .monkey_patch import monkey_patching
        monkey_patching()
