from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from .managers import CustomUserManager
from .choices import ACCESS_STATUS
# Create your models here.
class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(_('Email Address'), unique=True, null=True)
    is_owner = models.BooleanField(default=False)
    is_regular_user = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.first_name}_{self.last_name}'

class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.user)

class Category(models.Model):
    category_type = models.CharField(max_length=200)

    def __str__(self):
        return str(self.category_type)

def store_directory_path(instance, filename): 
    # file will be uploaded to MEDIA_ROOT / store_<id>/<filename> 
    return f'store_{instance.product.stroe.id}/{filename}'

class Store(models.Model):
    owner = models.OneToOneField(Owner, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(f'{self.owner}_store')

class Product(models.Model):
    name = models.CharField(max_length=100, null=True)
    kind = models.CharField(max_length=7, verbose_name='type', choices=ACCESS_STATUS)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True)
    categories = models.ManyToManyField(Category)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator]
        )

    def __str__(self):
        return str(f'{self.name}')

class File(models.Model):
    VIDEO = 'video'
    AUDIO = 'audio'
    PDF = 'PDF'
    TYPE_STATUS = [
       (VIDEO, _('Video')),
       (AUDIO, _('Audio')),
       (PDF, _('PDF')),
    ]
    name = models.CharField(max_length=100, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file_type = models.CharField(max_length=5, choices=TYPE_STATUS)
    the_file = models.FileField(upload_to=store_directory_path)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator]
        )
    kind = models.CharField(max_length=7, verbose_name='type', choices=ACCESS_STATUS)

    def __str__(self):
        return str(f'{self.name}')

class Subscription(models.Model):
    SPECIAL = 'special'
    NON_SPECIAL = 'not_special'
    SUBSCRIPTION_STATUS = [
       (SPECIAL, _('Special')),
       (NON_SPECIAL, _('Not_Special')),
    ]
    store = models.OneToOneField(Store, on_delete=models.SET_NULL, null=True)
    type_of_subscription = models.CharField(max_length=11, choices=SUBSCRIPTION_STATUS, default=NON_SPECIAL)

class RegularUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    subscription = models.OneToOneField(Subscription, on_delete=models.SET_NULL, null=True)
    files = models.ManyToManyField(File)
    products = models.ManyToManyField(Product)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class OrderProduct(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    products = models.ManyToManyField(Product)
    date = models.DateTimeField(auto_now=True)
    quantity = models.IntegerField(default=1)

    def get_total_price(self):
        total_prices = 0
        for product in self.products:
            total_prices += product.price
        return total_prices * self.quantity

class OrderFile(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    files = models.ManyToManyField(File)
    date = models.DateTimeField(auto_now=True)
    quantity = models.IntegerField(default=1)

    def get_total_price(self):
        total_prices = 0
        for file_obj in self.files:
            total_prices += file_obj.price
        return total_prices * self.quantity