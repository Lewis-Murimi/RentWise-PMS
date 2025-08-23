from rest_framework.permissions import BasePermission

class IsLandlordOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["landlord", "admin"]

class IsLandlordOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["landlord", "property_manager"]

class IsTenant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "tenant"

class IsCaretaker(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "caretaker"
