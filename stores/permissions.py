from rest_framework import permissions

class CustomPerUserPermission(permissions.BasePermission):
    """
    Permission class to check that a user can update his own resource only
    """
    def has_permission(self, request, view):
        # check that its an update request and user is modifying his resource only
        UNSAFE_METHODS = ['retrieve', 'update', 'partial_update', 'destroy']
        if view.action not in UNSAFE_METHODS:
            return True
        elif view.action in UNSAFE_METHODS and view.kwargs['pk'] == str(request.user.id) or\
            request.user.is_superuser:
            return True # grant access
        else:
            return False # not grant access otherwise

SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS', 'list', 'retrieve']

def anonymous_user_get_permission(request, view):
    if request.user.is_authenticated == False:
        if view.action in SAFE_METHODS:
            return True
        else:
            return False
    else:
        False

class StoreViewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if anonymous_user_get_permission(request, view):
            return True
        if request.user.is_owner or view.action in SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if anonymous_user_get_permission(request, view):
            return True
        if request.user == obj.owner.user or view.action in SAFE_METHODS:
            return True
        return False

class ProductViewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if anonymous_user_get_permission(request, view):
            return True
        if request.user.is_owner or view.action in SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if anonymous_user_get_permission(request, view):
            return True
        if request.user == obj.store.owner.user or view.action in SAFE_METHODS:
            return True
        return False

class FileViewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if anonymous_user_get_permission(request, view):
            return True
        if request.user.is_owner or view.action in SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if anonymous_user_get_permission(request, view):
            return True
        if request.user == obj.product.store.owner.user or view.action in SAFE_METHODS:
            return True
        return False
