from django.urls import path, include

from .api_views import LoginView
from .api_urls import router

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name="auth-login")
]