from rest_framework import permissions

from . import models

class CustomPerUserPermission(permissions.BasePermission):
    """
    Permission class to check that a user can update his own resource only and allow user anonymous
    users create a user if they want to.
    """
    def has_permission(self, request, view):
        # check that its an update request and user is modifying his resource only
        UNSAFE_METHODS = ['retrieve', 'update', 'partial_update', 'destroy']
        if view.action not in UNSAFE_METHODS: # let Post for anonymous users
            return True
        elif view.action in UNSAFE_METHODS and view.kwargs['pk'] == str(request.user.id) or\
            request.user.is_superuser:
            return True # grant access
        else:
            return False # not grant access otherwise

SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS', 'list', 'retrieve']

class BaseViewPermission(permissions.BasePermission):
    """
    Permission class that let anonymous users visit the stores and files and products but doesn't allow
    them to create them.
    also let each owner user check and CRUD their own store.
    and each regular user access their products and files
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated == False:
            if view.action in SAFE_METHODS:
                return True
            else:
                return False
        elif request.user.is_owner or view.action in SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        try:
            regular_user = models.RegularUser.objects.get(user=request.user)
        except:
            regular_user = None
        if request.user.is_authenticated == False:
            if view.action in SAFE_METHODS:
                return True
            else:
                return False
        elif request.user == obj.owner.user or view.action in SAFE_METHODS:
            return True
        elif regular_user != None:
            if regular_user.products.filter(id=obj.id) or regular_user.files.filter(id=obj.id):
                return True
            else:
                return False
        return False

class ProductViewPermission(BaseViewPermission):
    """
    This permission inherit from above permission just because object relation is different.
    """
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj.store)

class FileViewPermission(BaseViewPermission):
    """
    This permission inherit from above permission just because object relation is different.
    """
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj.product.store)

class IsRegularUserPermission(permissions.BasePermission):
    """
    This permission check if the user is regular or not to let some operations.
    """
    def has_permission(self, request, view):
        if request.user.is_regular_user == True:
            return True
        return False

class CategoryViewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_owner or view.action in SAFE_METHODS:
            return True
        return False