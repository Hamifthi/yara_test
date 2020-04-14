from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

from .models import Product, File

def create_owner_group(sender, **kwargs):
    owner_group, created = Group.objects.get_or_create(name='Owner')
    if created:
        product_content_type = ContentType.objects.get_for_model(Product)
        product_all_permissions = Permission.objects.filter(content_type=product_content_type)
        file_content_type = ContentType.objects.get_for_model(File)
        file_all_permissions = Permission.objects.filter(content_type=file_content_type)
        owner_group.permissions.set(product_all_permissions | file_all_permissions)
    else:
        pass

def set_owners_to_owner_group(sender, instance, created, **kwargs):
    if created:
        owner_group = Group.objects.get(name='Owner')
        owner_group.user_set.add(instance.user)