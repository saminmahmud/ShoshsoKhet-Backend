from django.apps import AppConfig
from django.utils import timezone
from django.apps import apps


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        try:
            OutstandingToken = apps.get_model(
                'token_blacklist',
                'OutstandingToken'
            )
            OutstandingToken.objects.filter(
                expires_at__lt=timezone.now()
            ).delete()
        except Exception:
            pass



# from django.apps import AppConfig


# class AccountsConfig(AppConfig):
#     name = 'accounts'
