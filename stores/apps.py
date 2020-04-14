from django.apps import AppConfig
from django.db.models.signals import post_migrate, post_save

class StoresConfig(AppConfig):
    name = 'stores'

    def ready(self):
        from .signals import create_owner_group, set_owners_to_owner_group
        from .models import Owner
        post_migrate.connect(create_owner_group, sender=self)
        post_save.connect(set_owners_to_owner_group, sender=Owner)