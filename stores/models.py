from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from .managers import CustomUserManager
from .choices import ACCESS_STATUS
# Create your models here.
# use default user for user types
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

# have a seperate model for the owners and regular users to deal with it more simple.
class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.user)

class Category(models.Model):
    category_type = models.CharField(max_length=200)

    def __str__(self):
        return str(self.category_type)

# function to define the path of the files and products on server.
def store_directory_path(instance, filename): 
    # file will be uploaded to MEDIA_ROOT / store_<id>/<filename> 
    return f'store_{instance.product.store.id}/{filename}'

class Store(models.Model):
    name = models.CharField(max_length=200, null=True)
    owner = models.OneToOneField(Owner, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(f'{self.name}_store')

# product object
class Product(models.Model):
    name = models.CharField(max_length=100, null=True)
    kind = models.CharField(max_length=7, verbose_name='type', choices=ACCESS_STATUS)
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True)
    categories = models.ManyToManyField(Category)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator]
        )

    def __str__(self):
        return str(f'{self.name}')

# file object with 3 types choices
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
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    file_type = models.CharField(max_length=5, choices=TYPE_STATUS)
    the_file = models.FileField(upload_to=store_directory_path)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator]
        )
    kind = models.CharField(max_length=7, verbose_name='type', choices=ACCESS_STATUS)

    def __str__(self):
        return str(f'{self.name}')

class Subscription(models.Model):
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True)
    type_of_subscription = models.CharField(max_length=7, default='Special')
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator]
        )

    def __str__(self):
        return str(f'{self.store.name}_subscription')

# seperate model for the regular users to store more information about the regular users
class RegularUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    files = models.ManyToManyField(File, blank=True)
    products = models.ManyToManyField(Product, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subscription = models.ManyToManyField(Subscription, blank=True)

    def __str__(self):
        return str(self.user)

class OrderProduct(models.Model):
    user = models.ForeignKey(RegularUser, on_delete=models.SET_NULL, null=True)
    products = models.ManyToManyField(Product)
    date = models.DateTimeField(auto_now=True)
    quantity = models.IntegerField(default=1)

class OrderFile(models.Model):
    user = models.ForeignKey(RegularUser, on_delete=models.SET_NULL, null=True)
    files = models.ManyToManyField(File)
    date = models.DateTimeField(auto_now=True)
    quantity = models.IntegerField(default=1)