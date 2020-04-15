from django.contrib.auth import authenticate, login

from rest_framework_jwt.settings import api_settings
from rest_framework import permissions
from rest_framework import viewsets, generics
from rest_framework.response import Response

from . import models
from . import serializers

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
    permission_classes = (permissions.AllowAny,)

class ProductViewset(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    permission_classes = (permissions.IsAuthenticated,)

class FileViewset(viewsets.ModelViewSet):
    queryset = models.File.objects.all()
    serializer_class = serializers.FileSerializer
    permission_classes = (permissions.IsAuthenticated,)

class RegularUserViewset(viewsets.ModelViewSet):
    queryset = models.RegularUser.objects.all()
    serializer_class = serializers.RegularUserSerializer
    permission_classes = (permissions.IsAuthenticated,)

class StoreViewset(viewsets.ModelViewSet):
    queryset = models.Store.objects.all()
    serializer_class = serializers.StoreSerializer
    permission_classes = (permissions.IsAuthenticated,)

class CategoryViewset(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = (permissions.IsAuthenticated,)
