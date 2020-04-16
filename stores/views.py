from django.contrib.auth import authenticate, login

from rest_framework_jwt.settings import api_settings
from rest_framework import permissions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from . import models
from . import serializers
from .permissions import (
    CustomPerUserPermission, ProductViewPermission, FileViewPermission, StoreViewPermission
)

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

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
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class UserViewset(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.AllowAny, CustomPerUserPermission,)

    def create(self, request):
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        is_owner = request.POST.get('is_owner', False)
        is_regular_user = request.POST.get('is_regular_user', False)
        if is_owner and is_regular_user:
            raise APIException('You must either be an owner or a regular user not both at the same time')
        serializer = self.get_serializer(
            data={'first_name': first_name, 'last_name': last_name, 'email': email, 'password': password,
            'is_owner': bool(is_owner), 'is_regular_user': bool(is_regular_user)})
        if serializer.is_valid():
            serializer.save()
            return Response(status=201)
        else:
            return Response(status=400)

class StoreViewset(viewsets.ModelViewSet):
    queryset = models.Store.objects.all()
    serializer_class = serializers.StoreSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, StoreViewPermission,)

class ProductViewset(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, ProductViewPermission)

class FileViewset(viewsets.ModelViewSet):
    queryset = models.File.objects.all()
    serializer_class = serializers.FileSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, FileViewPermission,)

class OrderProduct(generics.ListCreateAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializers.OrderProductSerializer

    def post(self, request, *args, **kwargs):
        user = request.POST['user']
        products = request.POST['products']
        date = request.POST['date']
        quantity = request.POST['quantity']
        serializer = self.get_serializer(
            data={'user': user, 'products': products, 'date': date, 'quantity': quantity
            })
        if serializer.is_valid():
            total_price = 0
            for product in serializer.data['products']:
                total_price += product.price
            total_price * serializer.data['quantity']
            if total_price > 0:
                transaction = user.balance - total_price
                if transaction > 0:
                    order = OrderProduct.objects.create(
                    user=user, products=products, date=date, quantity=quantity
                    )
                    request.user.product.add(serializer.data['products'])
                    user.balance = transaction
                    return Response(status=201)
                else:
                    raise APIException('You don\'nt have enough money to buy this product.')
                    return Response(status=400)
            elif total_price == 0:
                order = OrderProduct.objects.create(
                    user=user, products=products, date=date, quantity=quantity
                    )
                request.user.product.add(serializer.data['products'])
                return Response(status=201)
        else:
            return Response(status=400)

        def get(self, request, *args, **kwargs):
            return Response(status=200)







# class CategoryViewset(viewsets.ModelViewSet):
#     queryset = models.Category.objects.all()
#     serializer_class = serializers.CategorySerializer
#     permission_classes = (permissions.IsAuthenticated, UserIsOwnerPermission)