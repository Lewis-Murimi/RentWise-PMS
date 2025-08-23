# RentWise – Property Management System (Backend)

RentWise is a Django-based backend application for managing properties, tenants, caretakers, and payments. It provides RESTful APIs using Django REST Framework (DRF) with **role-based access control**, allowing different users to access only the data they are authorized to see.

---

## **Project Overview**

RentWise helps landlords, managers, caretakers, and tenants manage properties efficiently. Key features include:

- Tenant management (multiple units per tenant)
- Property management (residential and commercial)
- Unit management with status tracking (available, occupied, under maintenance)
- Caretaker and manager assignment to properties
- Payment tracking, status updates, and summaries per property/tenant
- Maintenance request management with role-based visibility
- Role-based access control for tenants, landlords, managers, caretakers, and admin
- JWT authentication for secure API access

---

## **Technologies Used**

- Python 3.x  
- Django 4.x  
- Django REST Framework (DRF)  
- PostgreSQL (or any other relational database)  
- JWT Authentication via `djangorestframework-simplejwt`

---

## **User Roles**

| Role | Permissions / Access |
|------|--------------------|
| **Tenant** | Access only assigned units, payments, and maintenance requests |
| **Caretaker** | Manage one assigned property and its maintenance requests |
| **Landlord** | Manage multiple properties, tenants, units, payments; assign/unassign managers and caretakers |
| **Manager** | Oversee multiple properties, units, tenants, payments, and maintenance requests |
| **Admin** | Full access to manage users, properties, units, and all data |

---

## **Project Structure**

- `core/` – Main Django app containing models, serializers, views, and URLs  
- `models.py` – Defines User, Property, Unit, TenantProfile, CaretakerProfile, ManagerProfile, TenantUnit, Payment, and MaintenanceRequest  
- `serializers.py` – Serializers for all models to handle API requests and role-based data representation  
- `views.py` – DRF ViewSets and APIViews implementing role-based access control  
- `urls.py` – API endpoint routing  
- `settings.py` – Project configuration including REST Framework and JWT settings  

---

## **API Endpoints**

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/users/` | GET, POST, PUT, DELETE | Manage users | Admin only |
| `/api/properties/` | GET, POST, PUT, DELETE | Manage properties | Landlord / Manager |
| `/api/units/` | GET, POST, PUT, DELETE | Manage units within properties | Landlord / Manager / Tenant (view only) |
| `/api/tenants/` | GET, POST, PUT, DELETE | Manage tenant profiles | Admin / Landlord / Manager |
| `/api/caretakers/` | GET, POST, PUT, DELETE | Manage caretaker profiles | Admin / Landlord / Manager |
| `/api/payments/` | GET, POST, PUT, DELETE | Manage tenant payments | Admin / Landlord / Manager / Tenant (view only) |
| `/api/maintenance/` | GET, POST, PUT, DELETE | Manage maintenance requests | Admin / Landlord / Manager / Caretaker / Tenant (own requests) |
| `/api/me/` | GET | Get current logged-in user and related profiles | Authenticated users |
| `/api/auth/token/` | POST | Obtain JWT token | All users |
| `/api/auth/token/refresh/` | POST | Refresh JWT token | All users |
| `/api/assign/manager/` | POST | Assign manager to a property | Landlord only |
| `/api/assign/caretaker/` | POST | Assign caretaker to a property | Landlord only |
| `/api/assign/unit/` | POST | Assign unit to tenant | Landlord / Manager / Caretaker |
| `/api/vacate/unit/` | POST | Vacate unit from tenant | Landlord only |
| `/api/unassign/caretaker/` | POST | Unassign caretaker from property | Landlord only |
| `/api/unassign/manager/` | POST | Unassign manager from property | Landlord only |
| `/api/properties/<property_id>/tenants/` | GET | List tenants in a property | Landlord / Manager |
| `/api/properties/<property_id>/units/` | GET | List units in a property | Landlord / Manager |
| `/api/properties/<property_id>/payments/` | GET | Payments summary per property | Landlord / Manager |
| `/api/properties/<property_id>/maintenance/` | GET | Maintenance requests by property | Landlord / Manager / Caretaker |
| `/api/tenants/<tenant_id>/payments/` | GET | Payments summary per tenant | Tenant (self) / Landlord / Manager |

> All endpoints enforce **role-based access control**.

---

## **Notes**

- Ensure you include the **JWT access token** in the `Authorization` header for all protected endpoints:  
