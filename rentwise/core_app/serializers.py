from rest_framework import serializers
from .models import User, Property, Unit, TenantProfile, CaretakerProfile, Payment, MaintenanceRequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone_number']


class PropertySerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Property
        fields = ['id', 'owner', 'name', 'address', 'description', 'type', 'created_at', 'updated_at']


class UnitSerializer(serializers.ModelSerializer):
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())

    class Meta:
        model = Unit
        fields = ['id', 'property', 'unit_number', 'size', 'rent', 'status']


class TenantProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    units = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all(), many=True)

    class Meta:
        model = TenantProfile
        fields = ['id', 'user', 'units', 'move_in_date', 'move_out_date']

class ManagerProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    managed_properties = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all(), many=True)

    class Meta:
        model = User
        fields = ['id', 'user', 'managed_properties']
        extra_kwargs = {'user': {'read_only': True}}

class CaretakerProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    assigned_property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all(), allow_null=True)

    class Meta:
        model = CaretakerProfile
        fields = ['id', 'user', 'assigned_property']


class PaymentSerializer(serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(queryset=TenantProfile.objects.all())

    class Meta:
        model = Payment
        fields = ['id', 'tenant', 'amount', 'due_date', 'payment_date', 'status', 'created_at', 'updated_at']


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(queryset=TenantProfile.objects.all())

    class Meta:
        model = MaintenanceRequest
        fields = ['id', 'tenant', 'description', 'request_date', 'completion_date', 'status']
