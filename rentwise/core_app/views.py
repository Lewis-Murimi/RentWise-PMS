from rest_framework import viewsets, permissions, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import (
    User, Property, Unit, TenantProfile,
    CaretakerProfile, Payment, MaintenanceRequest, ManagerProfile, TenantUnit
)
from .serializers import (
    UserSerializer, PropertySerializer, UnitSerializer,
    TenantProfileSerializer, CaretakerProfileSerializer,
    PaymentSerializer, MaintenanceRequestSerializer, CustomTokenObtainPairSerializer
)
from .permissions import IsLandlordOrManager, IsLandlordOrAdmin


# ---------------------------
# User ViewSet (Admin Only)
# ---------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


# ---------------------------
# Current User Endpoint (/me/)
# ---------------------------
class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def get(request):
        user = request.user
        data = UserSerializer(user).data

        # Include the profile matching the user's role
        if user.role == 'tenant':
            profile = getattr(user, 'tenant_profile', None)
            if profile:
                data['tenant_profile'] = TenantProfileSerializer(profile).data
        elif user.role == 'caretaker':
            profile = getattr(user, 'caretaker_profile', None)
            if profile:
                data['caretaker_profile'] = CaretakerProfileSerializer(profile).data
        elif user.role == 'property_manager':
            profile = getattr(user, 'manager_profile', None)
            if profile:
                data['manager_profile'] = {
                    'managed_properties': [p.id for p in profile.managed_properties.all()]
                }
        # Landlord and admin roles could also include properties
        elif user.role == 'landlord':
            data['properties'] = [p.id for p in user.properties.all()]
        return Response(data)


# ---------------------------
# Property ViewSet
# ---------------------------
class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated, IsLandlordOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Property.objects.none()
        if user.role == 'admin':
            return Property.objects.all()
        elif user.role in ['landlord', 'property_manager']:
            return Property.objects.filter(owner=user)
        return Property.objects.none()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# ---------------------------
# Unit ViewSet
# ---------------------------
class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Unit.objects.none()
        role = user.role
        if role == 'admin':
            return Unit.objects.all()
        elif role in ['landlord', 'property_manager']:
            if role == 'landlord':
                return Unit.objects.filter(property__owner=user)
            else:  # manager
                return Unit.objects.filter(property__in=user.manager_profile.managed_properties.all())

        elif role == 'tenant':
            tenant_profile = getattr(user, 'tenant_profile', None)
            if tenant_profile:
                return tenant_profile.units.all()
        return Unit.objects.none()


# ---------------------------
# TenantProfile ViewSet
# ---------------------------
class TenantProfileViewSet(viewsets.ModelViewSet):
    queryset = TenantProfile.objects.all()
    serializer_class = TenantProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return TenantProfile.objects.none()
        role = user.role
        if role == 'admin':
            return TenantProfile.objects.all()
        elif role == 'tenant':
            return TenantProfile.objects.filter(user=user)
        elif role in ['landlord', 'property_manager']:
            return TenantProfile.objects.filter(units__property__owner=user).distinct()
        return TenantProfile.objects.none()


# ---------------------------
# CaretakerProfile ViewSet
# ---------------------------
class CaretakerProfileViewSet(viewsets.ModelViewSet):
    queryset = CaretakerProfile.objects.all()
    serializer_class = CaretakerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return CaretakerProfile.objects.none()
        role = user.role
        if role == 'admin':
            return CaretakerProfile.objects.all()
        elif role in ['caretaker', 'property_manager', 'landlord']:
            return CaretakerProfile.objects.all()
        return CaretakerProfile.objects.none()


# ---------------------------
# Payment ViewSet
# ---------------------------
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Payment.objects.none()
        role = user.role
        if role == 'admin':
            return Payment.objects.all()
        elif role == 'tenant':
            return Payment.objects.filter(tenant__user=user)
        elif role in ['landlord', 'property_manager']:
            return Payment.objects.filter(tenant__units__property__owner=user).distinct()
        return Payment.objects.none()


# ---------------------------
# MaintenanceRequest ViewSet
# ---------------------------
class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return MaintenanceRequest.objects.none()
        role = user.role
        if role == 'admin':
            return MaintenanceRequest.objects.all()
        elif role == 'tenant':
            return MaintenanceRequest.objects.filter(tenant__user=user)
        elif role in ['landlord', 'property_manager', 'caretaker']:
            return MaintenanceRequest.objects.filter(tenant__units__property__owner=user).distinct()
        return MaintenanceRequest.objects.none()


# ---------------------------
# JWT Token View
# ---------------------------
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ---------------------------
# Assignment APIs (Landlord Only)
# ---------------------------
class AssignManagerToPropertyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def post(request):
        if request.user.role != 'landlord':
            return Response({"detail": "Only landlords can assign managers"}, status=status.HTTP_403_FORBIDDEN)

        manager_id = request.data.get('manager_id')
        property_id = request.data.get('property_id')

        from .models import User
        try:
            manager = User.objects.get(id=manager_id, role='property_manager')
        except User.DoesNotExist:
            return Response({"detail": "Manager not found"}, status=status.HTTP_400_BAD_REQUEST)

        from .models import Property, ManagerProfile
        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({"detail": "Property not found"}, status=status.HTTP_400_BAD_REQUEST)

        profile, _ = ManagerProfile.objects.get_or_create(user=manager)
        profile.managed_properties.add(property_obj)
        profile.save()
        return Response({"detail": f"{manager.username} assigned to {property_obj.name}"})


class AssignCaretakerToPropertyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def post(request):
        if request.user.role != 'landlord':
            return Response({"detail": "Only landlords can assign caretakers"}, status=status.HTTP_403_FORBIDDEN)

        caretaker_id = request.data.get('caretaker_id')
        property_id = request.data.get('property_id')

        from .models import User, Property, CaretakerProfile
        try:
            caretaker = User.objects.get(id=caretaker_id, role='caretaker')
        except User.DoesNotExist:
            return Response({"detail": "Caretaker not found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({"detail": "Property not found"}, status=status.HTTP_400_BAD_REQUEST)

        profile, _ = CaretakerProfile.objects.get_or_create(user=caretaker)
        profile.assigned_property = property_obj
        profile.save()
        return Response({"detail": f"{caretaker.username} assigned to {property_obj.name}"})


class AssignUnitToTenantView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role not in ['landlord', 'property_manager', 'caretaker']:
            return Response({"detail": "Only landlords, managers, or caretakers can assign units"},
                            status=status.HTTP_403_FORBIDDEN)

        tenant_id = request.data.get('tenant_id')
        unit_id = request.data.get('unit_id')
        move_in_date = request.data.get('move_in_date')
        move_out_date = request.data.get('move_out_date')

        from .models import User, Unit, TenantProfile, TenantUnit
        try:
            tenant_user = User.objects.get(id=tenant_id, role='tenant')
        except User.DoesNotExist:
            return Response({"detail": "Tenant not found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            unit = Unit.objects.get(id=unit_id)
        except Unit.DoesNotExist:
            return Response({"detail": "Unit not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Optional: Only allow assignment if user has access to the property
        if user.role == 'property_manager':
            if not unit.property in user.manager_profile.managed_properties.all():
                return Response({"detail": "Manager does not manage this property"}, status=status.HTTP_403_FORBIDDEN)
        elif user.role == 'caretaker':
            if unit.property != user.caretaker_profile.assigned_property:
                return Response({"detail": "Caretaker does not manage this property"}, status=status.HTTP_403_FORBIDDEN)

        tenant_profile, _ = TenantProfile.objects.get_or_create(user=tenant_user)
        TenantUnit.objects.create(
            tenant=tenant_profile,
            unit=unit,
            move_in_date=move_in_date,
            move_out_date=move_out_date
        )
        return Response({"detail": f"Unit {unit.unit_number} assigned to {tenant_user.username}"})



# ---------------------------
# Vacate / Unassign Endpoints
# ---------------------------
class VacateUnitFromTenantView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def post(request):
        if request.user.role != 'landlord':
            return Response({"detail": "Only landlords can vacate units"}, status=status.HTTP_403_FORBIDDEN)

        tenant_id = request.data.get('tenant_id')
        unit_id = request.data.get('unit_id')

        try:
            tenant_profile = TenantProfile.objects.get(user__id=tenant_id)
            tenant_unit = TenantUnit.objects.get(tenant=tenant_profile, unit__id=unit_id)
            tenant_unit.delete()
            return Response({"detail": f"Unit {unit_id} vacated from tenant {tenant_profile.user.username}"})
        except (TenantProfile.DoesNotExist, TenantUnit.DoesNotExist):
            return Response({"detail": "Tenant or unit assignment not found"}, status=status.HTTP_400_BAD_REQUEST)


class UnassignCaretakerFromPropertyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def post(request):
        if request.user.role != 'landlord':
            return Response({"detail": "Only landlords can unassign caretakers"}, status=status.HTTP_403_FORBIDDEN)

        caretaker_id = request.data.get('caretaker_id')

        try:
            caretaker_profile = CaretakerProfile.objects.get(user__id=caretaker_id)
            caretaker_profile.assigned_property = None
            caretaker_profile.save()
            return Response({"detail": f"Caretaker {caretaker_profile.user.username} unassigned from property"})
        except CaretakerProfile.DoesNotExist:
            return Response({"detail": "Caretaker not found"}, status=status.HTTP_400_BAD_REQUEST)


class UnassignManagerFromPropertyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def post(request):
        if request.user.role != 'landlord':
            return Response({"detail": "Only landlords can unassign managers"}, status=status.HTTP_403_FORBIDDEN)

        manager_id = request.data.get('manager_id')
        property_id = request.data.get('property_id')

        try:
            manager_profile = ManagerProfile.objects.get(user__id=manager_id)
            property_obj = Property.objects.get(id=property_id)
            manager_profile.managed_properties.remove(property_obj)
            return Response({"detail": f"Manager {manager_profile.user.username} unassigned from {property_obj.name}"})
        except (ManagerProfile.DoesNotExist, Property.DoesNotExist):
            return Response({"detail": "Manager or property not found"}, status=status.HTTP_400_BAD_REQUEST)

# ---------------------------
# Tenants by Property
# ---------------------------
class TenantsByPropertyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def get(request, property_id):
        user = request.user
        # RBAC: only landlords/managers for their properties
        if user.role not in ['landlord', 'property_manager']:
            return Response({"detail": "Forbidden"}, status=403)

        tenants = TenantProfile.objects.filter(units__property__id=property_id).distinct()
        serializer = TenantProfileSerializer(tenants, many=True)
        return Response(serializer.data)


# ---------------------------
# Units by Property
# ---------------------------
class UnitsByPropertyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def get(request, property_id):
        user = request.user
        if user.role not in ['landlord', 'property_manager']:
            return Response({"detail": "Forbidden"}, status=403)

        units = Unit.objects.filter(property__id=property_id)
        serializer = UnitSerializer(units, many=True)
        return Response(serializer.data)


# ---------------------------
# Payments Summary by Property
# ---------------------------
class PaymentsByPropertyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def get(request, property_id):
        user = request.user
        if user.role not in ['landlord', 'property_manager']:
            return Response({"detail": "Forbidden"}, status=403)

        payments = Payment.objects.filter(tenant__units__property__id=property_id)
        serializer = PaymentSerializer(payments, many=True)
        total_due = sum(p.amount for p in payments if p.status != 'paid')
        total_collected = sum(p.amount for p in payments if p.status == 'paid')
        return Response({
            "payments": serializer.data,
            "total_due": total_due,
            "total_collected": total_collected
        })


# ---------------------------
# Maintenance Requests by Property
# ---------------------------
class MaintenanceByPropertyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def get(request, property_id):
        user = request.user
        if user.role not in ['landlord', 'property_manager', 'caretaker']:
            return Response({"detail": "Forbidden"}, status=403)

        maintenance_requests = MaintenanceRequest.objects.filter(tenant__units__property__id=property_id)
        serializer = MaintenanceRequestSerializer(maintenance_requests, many=True)
        return Response(serializer.data)


# ---------------------------
# Payments Summary by Tenant
# ---------------------------
class PaymentsByTenantView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def get(request, tenant_id):
        user = request.user
        # tenants can see their own payments
        if user.role == 'tenant' and user.id != tenant_id:
            return Response({"detail": "Forbidden"}, status=403)
        payments = Payment.objects.filter(tenant__user__id=tenant_id)
        serializer = PaymentSerializer(payments, many=True)
        total_due = sum(p.amount for p in payments if p.status != 'paid')
        total_collected = sum(p.amount for p in payments if p.status == 'paid')
        return Response({
            "payments": serializer.data,
            "total_due": total_due,
            "total_collected": total_collected
        })