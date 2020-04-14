from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Owner)
admin.site.register(RegularUser)
admin.site.register(Store)
admin.site.register(Product)
admin.site.register(File)
admin.site.register(Category)