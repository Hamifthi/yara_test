from django.forms.widgets import PasswordInput

from rest_framework import serializers

from . import models

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = (
            'first_name', 'last_name', 'email', 'password', 'is_active', 'is_owner', 'is_regular_user'
            )
        extra_kwargs = {
            'is_active': {
                'help_text':None
            },
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }

class RegularUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RegularUser
        exclude = ['user', 'products', 'files']

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('email', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.File
        fields = '__all__'

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Store
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'

class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)

class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderProduct
        exclude = ['user']

class OrderFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderFile
        exclude = ['user']

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subscription
        exclude = ['user']