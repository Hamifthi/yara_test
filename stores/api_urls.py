from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewset)
router.register(r'stores', views.StoreViewset)
router.register(r'products', views.ProductViewset)
router.register(r'files', views.FileViewset)
router.register(r'categories', views.CategoryViewset)