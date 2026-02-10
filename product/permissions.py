from rest_framework import permissions


class IsSeller(permissions.BasePermission):
    message = 'Only sellers can perform this action.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'seller'


class IsBuyer(permissions.BasePermission):
    message = 'Only buyers can perform this action.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'buyer'


class IsAdmin(permissions.BasePermission):
    message = 'Only admins can perform this action.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'admin'


class IsSellerOwner(permissions.BasePermission):
    message = 'You can only manage your own products.'

    def has_object_permission(self, request, view, obj):
        return obj.seller.user == request.user


class IsSellerOrAdmin(permissions.BasePermission):
    message = 'Only sellers or admins can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.user_type in ['seller', 'admin']
        )

class IsBuyerOrAdmin(permissions.BasePermission):
    message = 'Only buyers or admins can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.user_type in ['buyer', 'admin']
        )