from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('tenant', 'Tenant'),
        ('caretaker', 'Caretaker'),
        ('property_manager', 'Property Manager'),
        ('landlord', 'Landlord'),
        ('admin', 'Admin'),
    ]

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=12, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    def __str__(self):
        return f"{self.email} ({self.role})"


class Property(models.Model):
    TYPE_CHOICES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='residential')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.type}) - {self.owner.email}"


class Unit(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('under maintenance', 'Under Maintenance'),
    ]
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='units')
    unit_number = models.CharField(max_length=50)
    size = models.CharField(max_length=50, blank=True, null=True)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    class Meta:
        unique_together = ('property', 'unit_number')

    def __str__(self):
        return f"{self.unit_number} - {self.property.name} ({self.status})"


class TenantUnit(models.Model):
    tenant = models.ForeignKey("TenantProfile", on_delete=models.CASCADE)
    unit = models.ForeignKey("Unit", on_delete=models.CASCADE)
    move_in_date = models.DateField(null=True, blank=True)
    move_out_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("tenant", "unit")

    def __str__(self):
        return f"{self.tenant.user.email} -> {self.unit.unit_number}"


class TenantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tenant_profile')
    units = models.ManyToManyField(Unit, through=TenantUnit, related_name='tenants')

    def __str__(self):
        unit_list = ", ".join([u.unit_number for u in self.units.all()])
        return f"{self.user.email} - Units: {unit_list if unit_list else 'No Units Assigned'}"


class ManagerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')
    managed_properties = models.ManyToManyField(Property, related_name='managers', blank=True)

    def __str__(self):
        property_list = ", ".join([p.name for p in self.managed_properties.all()])
        return f"{self.user.email} - Managed Properties: {property_list if property_list else 'None'}"


class CaretakerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='caretaker_profile')
    assigned_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='caretakers', null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.assigned_property.name if self.assigned_property else 'No Property Assigned'}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue'),
    ]
    tenant = models.ForeignKey(TenantProfile, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.tenant.user.email} - {self.amount} ({self.status})"


class MaintenanceRequest(models.Model):
    tenant = models.ForeignKey(TenantProfile, on_delete=models.CASCADE, related_name='maintenance_requests')
    description = models.TextField()
    request_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('open', 'Open'), ('in_progress', 'In Progress'), ('closed', 'Closed')],
        default='open'
    )

    def __str__(self):
        unit_list = ", ".join([u.unit_number for u in self.tenant.units.all()])
        return f"Request by {self.tenant.user.email} for units {unit_list} - {self.status}"

