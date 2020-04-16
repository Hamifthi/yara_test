from django.urls import path, include

from . import views
from .api_urls import router

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view(), name='login'),
    path('order/product', views.OrderProduct.as_view(), name='order_product')
]