from rest_framework import routers
from . import api_views as views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewset)
router.register(r'products', views.ProductViewset)
router.register(r'files', views.FileViewset)
router.register(r'regular_users', views.RegularUserViewset)
router.register(r'stores', views.StoreViewset)
router.register(r'categories', views.CategoryViewset)