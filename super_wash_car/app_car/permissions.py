from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.profile.role == 'admin'

class IsLaveur(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.profile.role == 'laveur'

class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.profile.role == 'client'
