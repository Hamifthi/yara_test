from django.urls import path, include

from . import views
from .api_urls import router

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view(), name='login'),
    path('users/activate/', views.ActivateRegularUserView.as_view(), name='activate_regular_user'),
    path('order/products/', views.OrderProduct.as_view(), name='order_product'),
    path('order/files/', views.OrderFile.as_view(), name='order_file'),
]