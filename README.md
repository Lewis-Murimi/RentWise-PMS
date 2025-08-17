# RentWise – Property Management System (Backend)

RentWise is a Django-based backend application for managing properties, tenants, caretakers, and payments. It provides RESTful APIs using Django REST Framework with role-based access control, allowing different users to access only the data they are authorized to see.

---

## **Project Overview**

RentWise is designed to help landlords, managers, caretakers, and tenants manage properties efficiently. Key features include:

- Tenant management (multiple units per tenant)
- Property management (residential and commercial)
- Unit management with status tracking (available, occupied, under maintenance)
- Caretaker assignment to properties
- Payment tracking and status updates
- Maintenance request management
- Role-based access control for tenants, landlords, managers, and caretakers

---

## **Technologies Used**

- Python 3.x  
- Django 4.x  
- Django REST Framework (DRF)  
- PostgreSQL (or any other relational database)  
- JWT Authentication (planned for next iteration)

---

## **User Roles**

- **Tenant:** Access only assigned units, payments, and maintenance requests  
- **Caretaker:** Manage one assigned property and its maintenance requests  
- **Landlord:** Manage multiple properties, tenants, units, payments  
- **Manager:** Oversee multiple properties and related data  
- **Admin:** Full access to manage users and data

---

## **Project Structure**

- `core/` – Main Django app containing models, serializers, views, and URLs
- `models.py` – Defines User, Property, Unit, TenantProfile, CaretakerProfile, Payment, and MaintenanceRequest
- `serializers.py` – Serializers for all models to handle API requests
- `views.py` – DRF ViewSets with role-based access control
- `urls.py` – API endpoint routing
- `settings.py` – Project configuration (including REST Framework settings)

---

## **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/users/` | GET, POST, PUT, DELETE | Manage users (Admin only) |
| `/api/properties/` | GET, POST, PUT, DELETE | Manage properties (Landlord/Manager) |
| `/api/units/` | GET, POST, PUT, DELETE | Manage units within properties |
| `/api/tenants/` | GET, POST, PUT, DELETE | Manage tenant profiles |
| `/api/caretakers/` | GET, POST, PUT, DELETE | Manage caretaker profiles |
| `/api/payments/` | GET, POST, PUT, DELETE | Manage tenant payments |
| `/api/maintenance/` | GET, POST, PUT, DELETE | Manage maintenance requests |

> Note: Access is restricted based on user role.

---
