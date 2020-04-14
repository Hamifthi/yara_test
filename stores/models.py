from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager
from .choices import ACCESS_STATUS
# Create your models here.
class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(_('Email Address'), unique=True, null=True, required=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
                return f'{self.first_name}_{self.last_name}'

class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
                return str(self.user)

class RegularUser(models.Model):
    SPECIAL = 'special'
    NON_SPECIAL = 'not_special'
    SUBSCRIPTION_STATUS = [
       (SPECIAL, _('Special')),
       (NON_SPECIAL, _('Not_Special')),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # set default subscription to non special
    type_of_subscription = models.CharField(
        max_length=11, choices=SUBSCRIPTION_STATUS, default=NON_SPECIAL
        )
    files = models.ManyToManyField(File, required=False)
    products = models.ManyToManyField(Product, required=False)

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.BigIntegerField()
    kind = models.CharField(max_length=7, verbose_name='type', choices=ACCESS_STATUS)

class Store(models.Model):
    # check if it's not necessary delete the owner class and set direct relation to the User class
    owner = models.OneToOneField(Owner, on_delete=models.SET_NULL, null=True)
    products = models.ManyToManyField(Product)

def store_directory_path(instance, filename): 
    # file will be uploaded to MEDIA_ROOT / store_<id>/<filename> 
    return f'store_{instance.store.id}/{filename}'

class File(models.Model):
    VIDEO = 'video'
    AUDIO = 'audio'
    PDF = 'PDF'
    TYPE_STATUS = [
       (VIDEO, _('Video')),
       (AUDIO, _('Audio')),
       (PDF, _('PDF')),
    ]
    name = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file_type = models.CharField(max_length=5, choices=TYPE_STATUS)
    the_file = models.FileField(upload_to=store_directory_path)
    price = models.BigIntegerField()
    kind = models.CharField(max_length=7, verbose_name='type', choices=ACCESS_STATUS)

class Category(models.Model):
    category_type = models.CharField(max_length=200)
    products = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)