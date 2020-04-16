from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models import *

@admin.register(User)
class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('email', 'is_staff', 'is_active')
    fieldsets = (
        ('Personal_Info', {'fields': (
            'first_name', 'last_name', 'email', 'password', 'is_owner', 'is_regular_user'
            )}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        ('Credentials', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'password1', 'password2',
            'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('id',)

# Register your models here.
admin.site.register(Owner)
admin.site.register(RegularUser)
admin.site.register(Store)
admin.site.register(Product)
admin.site.register(File)
admin.site.register(Category)