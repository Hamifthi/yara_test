from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password

from rest_framework_jwt.settings import api_settings
from rest_framework import permissions
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from . import models
from . import serializers
from .permissions import (
    CustomPerUserPermission, ProductViewPermission, FileViewPermission, BaseViewPermission,
    IsRegularUserPermission, IsRegularUserPermission, CategoryViewPermission
)

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

# login class base on jwt token authentication
# jwt tokens are valid for 10 minutes
class LoginView(generics.CreateAPIView):
    serializer_class = serializers.LoginSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = models.User.objects.all()

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            serializer = serializers.TokenSerializer(data={
                "token": jwt_encode_handler(
                    jwt_payload_handler(user)
                )})
            serializer.is_valid() 
            return Response(serializer.validated_data)
        else:
            return Response(status=401)

class UserViewset(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.AllowAny, CustomPerUserPermission,)

    # create my own create method to customize some processes.
    def create(self, request):
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        is_owner = request.POST.get('is_owner', False)
        is_regular_user = request.POST.get('is_regular_user', False)
        if is_owner and is_regular_user: # user can't be owner and regular at the same time.
            raise APIException('You must either be an owner or a regular user not both at the same time')
        serializer = self.get_serializer(
            data={'first_name': first_name, 'last_name': last_name, 'email': email,
            'password': make_password(password), 'is_owner': bool(is_owner),
            'is_regular_user': bool(is_regular_user)})
        if serializer.is_valid():
            user = serializer.save() 
            if is_owner: # save owner if user is owner but regular users needs to activate themselves
                models.Owner.objects.create(user=user)
            return Response(status=201)
        else:
            return Response(data='The data are not correct', status=400)

class ActivateRegularUserView(generics.ListCreateAPIView):
    """
    This class is used to activate regular users. owners don't have permissions to access this view.
    """
    queryset = models.RegularUser.objects.all()
    serializer_class = serializers.RegularUserSerializer
    permission_classes = (permissions.IsAuthenticated, IsRegularUserPermission)

    def create(self, request):
        user = request.user
        balance = request.POST['balance']
        subscription = request.POST.getlist('subscription')
        # create a regular user without subscription and products and files
        serializer = self.get_serializer(
            data={'balance': balance, 'subscription': subscription})
        if serializer.is_valid():
            # if user choose a particular subscription
            if serializer.validated_data['subscription'] != []:
                # users can choose different subscription for different stores
                for subscription in serializer.validated_data['subscription']:
                    # the balance of user must be above the subscription price
                    if serializer.validated_data['balance'] > subscription.price:
                        regular_user = models.RegularUser.objects.create(
                            user=user, balance=serializer.validated_data['balance']
                            )
                        # set the subscription for the user and also subtract price of the subscriptions from user
                        # balance
                        regular_user.subscription.set(serializer.validated_data['subscription'])
                        regular_user.balance -= subscription.price
                        regular_user.save()
                        # if user choose any subscription products and files of that store added to the user 
                        # products and files which user can access it later
                        for product in subscription.store.product_set.all():
                            regular_user.products.add(product)
                            for file_obj in product.file_set.all():
                                regular_user.files.add(file_obj)
                            return Response(status=201)
                    # subscription price is more than user balance
                    else:
                        raise APIException(detail='Your balance for this subscription is not enough')
                        return Response(status=400)
            # user don't choose any particular subscription
            else:
                regular_user = models.RegularUser.objects.create(
                    user=user, balance=serializer.validated_data['balance']
                    )
                return Response(status=201)
        # serializer is invalid
        else:
            return Response(status=400)

class StoreViewset(viewsets.ModelViewSet):
    queryset = models.Store.objects.all()
    serializer_class = serializers.StoreSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, BaseViewPermission,)

class ProductViewset(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, ProductViewPermission)

class FileViewset(viewsets.ModelViewSet):
    queryset = models.File.objects.all()
    serializer_class = serializers.FileSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, FileViewPermission,)

class CategoryViewset(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = (permissions.IsAuthenticated, CategoryViewPermission,)

class OrderProduct(generics.ListCreateAPIView):
    queryset = models.OrderProduct.objects.all()
    serializer_class = serializers.OrderProductSerializer
    # user must be regular user to order a product
    permission_classes = (permissions.IsAuthenticated, IsRegularUserPermission)

    def post(self, request, *args, **kwargs):
        products = request.data.getlist('products')
        quantity = request.data.get('quantity')
        user = request.user
        regular_user = models.RegularUser.objects.get(user=user)
        serializer = self.get_serializer(
            data={'user': regular_user, 'products': products, 'quantity': quantity
            })
        if serializer.is_valid():
            # first we check user has money to purchase these products
            total_price = 0
            for product in serializer.validated_data['products']:
                total_price += product.price
            total_price * serializer.validated_data['quantity']
            if total_price > 0:
                transaction = regular_user.balance - total_price
                # if user has money order can be done
                if transaction > 0:
                    order = models.OrderProduct.objects.create(
                    user=regular_user, quantity=quantity
                    )
                    order.products.set(products)
                    # add all products and their files to the user products and files
                    for product in serializer.validated_data['products']:
                        regular_user.products.add(product)
                        for file_obj in product.file_set.all():
                            regular_user.files.add(file_obj)
                    regular_user.balance = transaction
                    regular_user.save()
                    return Response(status=201)
                else:
                    raise APIException('You don\'nt have enough money to buy this product.')
                    return Response(status=400)
            # if these items were free
            elif total_price == 0:
                order = models.OrderProduct.objects.create(
                    user=regular_user, quantity=quantity
                    )
                order.products.set(products)
                for product in serializer.validated_data['products']:
                        regular_user.products.add(product)
                        for file_obj in product.file_set.all():
                            regular_user.files.add(file_obj)
                return Response(status=201)
        # serializer is invalid
        else:
            return Response(data=serializer.errors, status=400)

class OrderFile(generics.ListCreateAPIView):
    queryset = models.OrderFile.objects.all()
    serializer_class = serializers.OrderFileSerializer
    permission_classes = (permissions.IsAuthenticated, IsRegularUserPermission)

    def post(self, request, *args, **kwargs):
        files = request.data.getlist('files')
        quantity = request.data.get('quantity')
        user = models.User.objects.get(id=3)
        regular_user = models.RegularUser.objects.get(user=user)
        serializer = self.get_serializer(
            data={'user': regular_user, 'files': files, 'quantity': quantity
            })
        if serializer.is_valid():
            # first we check user has money to purchase these files
            total_price = 0
            for file_obj in serializer.validated_data['files']:
                total_price += file_obj.price
            total_price * serializer.validated_data['quantity']
            if total_price > 0:
                # if user has money order can be done
                transaction = regular_user.balance - total_price
                if transaction > 0:
                    order = models.OrderFile.objects.create(
                    user=regular_user, quantity=quantity
                    )
                    order.files.set(files)
                    for file_obj in serializer.validated_data['files']:
                        regular_user.files.add(file_obj)
                    regular_user.balance = transaction
                    regular_user.save()
                    return Response(status=201)
                else:
                    raise APIException('You don\'nt have enough money to buy this file.')
                    return Response(status=400)
            # if these items were free
            elif total_price == 0:
                order = models.OrderFile.objects.create(
                    user=regular_user, quantity=quantity
                    )
                order.files.set(files)
                for file_obj in serializer.validated_data['files']:
                        regular_user.files.add(file_obj)
                return Response(status=201)
        # serializer is invalid
        else:
            return Response(data=serializer.errors, status=400)
