# ERP Backend - Microservices Architecture

A scalable, production-ready Enterprise Resource Planning (ERP) backend system built with Django, implementing microservices architecture with centralized authentication, API gateway pattern, and modular service design.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Microservices Structure](#microservices-structure)
3. [Services & Modules](#services--modules)
4. [Technologies Stack](#technologies-stack)
5. [Coding Practices & Patterns](#coding-practices--patterns)
6. [Authentication & Security](#authentication--security)
   - [JWT Token Flow](#jwt-token-flow)
   - [Role & Permission Management](#role--permission-management-)
   - [Key Security Features](#key-security-features)
7. [Project Structure](#project-structure)
8. [Getting Started](#getting-started)
9. [API Documentation Guide](#api-documentation-guide--swagger--redoc)
10. [Logging & Monitoring](#logging--monitoring)
11. [Contributing](#contributing)
12. [Troubleshooting](#troubleshooting)
13. [Future Enhancements](#future-enhancements)

---

## Architecture Overview

This project follows a **Microservices Architecture** pattern with the following key components:

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Client / Frontend                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              API Gateway (Port 8000)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ CORS Middleware                                        │ │
│  │ JWT Authentication Middleware                         │ │
│  │ Request Logging & Routing                             │ │
│  └────────────────────────────────────────────────────────┘ │
│                     │                                        │
│  ┌────────────────┬─┴──────────────────┬─────────────────┐ │
│  │ Public Routes  │ Proxy Routes       │ Auth Routes    │ │
│  │ /api/auth/     │ /api/master/*      │ (passthrough)  │ │
│  └────────────────┴────────────────────┴─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
         │                          │
         │ Routes                   │ Routes
         ▼                          ▼
┌─────────────────────────────┐  ┌──────────────────────────────┐
│   Auth Service (Port 8001)  │  │ Master Service (Port 8002)   │
│  ┌───────────────────────┐  │  │  ┌────────────────────────┐ │
│  │ User Authentication   │  │  │  │ Master Data Mgmt       │ │
│  │ JWT Token Generation  │  │  │  │ ├─ Geographic Masters  │ │
│  │ Token Refresh         │  │  │  │ │  ├─ Country          │ │
│  │ Audit Logging         │  │  │  │ │  ├─ State            │ │
│  │                       │  │  │  │ │  ├─ District         │ │
│  │ DB: PostgreSQL        │  │  │  │ │  ├─ City             │ │
│  └───────────────────────┘  │  │  │ │  └─ Plant/Site       │ │
│                             │  │  │ ├─ Equipment Masters  │ │
│                             │  │  │ │  └─ Equipment Type   │ │
│                             │  │  │ │                      │ │
│                             │  │  │ │ DB: MySQL            │ │
│                             │  │  │ └────────────────────────┘ │
└─────────────────────────────┘  └──────────────────────────────┘
         │                                   │
         └──────────────────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   Common Library       │
                    │ ┌───────────────────┐ │
                    │ │ JWT Encoder       │ │
                    │ │ JWT Decoder       │ │
                    │ │ Shared Utilities  │ │
                    │ └───────────────────┘ │
                    └───────────────────────┘
```

### Key Architectural Principles

1. **Separation of Concerns**: Each service handles a specific domain
2. **API Gateway Pattern**: Single entry point for all client requests
3. **Stateless Services**: Services don't maintain client session state
4. **Shared Authentication**: Centralized JWT token management
5. **Scalability**: Services can be deployed independently
6. **Database per Service**: Each service maintains its own data store

---

## Microservices Structure

### 1. **API Gateway** (`/api_gateway`)
**Purpose**: Single entry point for all client requests

**Responsibilities**:
- Request routing to appropriate microservice
- JWT authentication & authorization
- CORS handling
- Request/response logging
- Rate limiting (extensible)
- Error handling and standardization

**Key Components**:
- `middleware/jwt_auth.py` - JWT validation middleware
- `views/proxy.py` - Request forwarding to services
- `settings.py` - Gateway configuration

**Runtime**: Port 8000

---

### 2. **Auth Service** (`/auth_service`)
**Purpose**: User authentication and JWT token management

**Responsibilities**:
- User login/authentication (API & HTML form)
- JWT token generation (access & refresh) ✅ **WORKING**
- Token refresh mechanism with validation ✅ **IMPLEMENTED**
- Audit logging (login attempts, failures, successful logins) ✅ **WORKING**
- User group management
- Password hashing (PBKDF2-SHA256 with 120,000 iterations)
- Role and permission management ✅ **NEW**
- User-to-role assignment ✅ **NEW**

**Key Components**:
- `apps/authentication/views/auth.py` - Login endpoints (API & HTML form)
- `apps/authentication/views/permission_and_role.py` - Role/permission endpoints ✅ **NEW**
- `apps/authentication/views/user.py` - User management endpoints ✅ **ENHANCED**
- `apps/authentication/services/audit_utils.py` - Security auditing (IP, User-Agent, Browser/OS detection)
- `apps/authentication/services/token_service.py` - JWT token operations
- `apps/authentication/models/audit.py` - Audit log model with event tracking
- `apps/authentication/models/permissions.py` - Permission models (proxy, managed=False) ✅ **NEW**
- `apps/authentication/models/user_role.py` - UserRole model ✅ **NEW**
- `apps/authentication/models/user_profile.py` - User profile extension
- `apps/authentication/serializers/permission_and_role.py` - Role/permission serializers ✅ **NEW**
- `config/hashers.py` - PBKDF2-SHA256 password hasher with explicit iteration count

**Database**: MySQL/MariaDB (`auth_service_db`)
**Runtime**: Port 8001

**Security Features**:
- RSA-256 (RS256) JWT signing with private key (stored in `keys/dev_private.pem`)
- PBKDF2-SHA256 password hashing with 120,000 iterations
- Audit logs for all authentication events (stored in MySQL database)
- Client IP extraction (with X-Forwarded-For proxy support)
- User-Agent and browser/OS detection
- Failed login attempt logging with metadata
- Successful login tracking with user context
- Role-based access control (RBAC) with granular permissions ✅ **NEW**
- User-role mapping with inheritance ✅ **NEW**

---

### 3. **Master Service** (`/master-service`)
**Purpose**: Master data management for ERP system

**Responsibilities**:
- Geographic master data (Country, State, District, City)
- Organizational structure (Plant, Site, Ward, Zone)
- Equipment type masters
- Data validation and consistency
- Soft delete implementation
- Audit trail (created_by, updated_by, timestamps)

**Key Components**:

#### Common Master Module (`apps/common_master/`)
- **Models**: Geographic and organizational hierarchies
  - `Continent` → `Country` → `State` → `District` → `City`
  - `Plant`, `Site`, `Ward`, `Zone`
- **Views**: RESTful CRUD endpoints
- **Serializers**: Data validation and transformation
- **Validators**: Business rule enforcement (e.g., unique_name_validator)
- **Middleware**: JWT authentication for internal requests

#### Equipment Master Module (`apps/em_master/`)
- **Models**: Equipment classification and types
- **Services**: Equipment lookup and filtering
- **Serializers**: Equipment data serialization
- **Views**: Equipment endpoint handlers

**Database**: MySQL
**Runtime**: Port 8002

**Database Features**:
- Base model inheritance with common fields:
  - `unique_id` - System-generated identifier
  - `is_active` - Logical status
  - `is_deleted` - Soft delete flag
  - `created_at`, `updated_at` - Timestamps
  - `created_by`, `updated_by` - User tracking
- Foreign key relationships with PROTECT constraints
- Relational integrity

---

### 4. **Common Library** (`/common_lib`)
**Purpose**: Shared utilities and cross-service components

**Responsibilities**:
- JWT encoding/decoding logic
- Shared exceptions and error handling
- Utility functions
- Constants and enums

**Key Modules**:

#### JWT Module (`erp_jwt/`)
- **encoder.py**: Creates access and refresh tokens
  - Access Token: 1-hour lifetime
  - Refresh Token: Long-lived (configurable)
  - Payload includes: user_id, username, groups, issuer, type
  - Uses RSA private key from `auth_service/keys/`
  
- **decoder.py**: Validates and decodes tokens
  - Verifies signature using public key
  - Checks token expiration
  - Validates issuer and algorithm
  - Custom exceptions: `JWTExpiredError`, `JWTInvalidError`

**Security Features**:
- Public/Private key pair for asymmetric cryptography
- Algorithm enforcement (RS256 only)
- Issuer validation
- Defensive key loading

---

## Services & Modules

### Module Organization Pattern

#### Standard Generic Structure
For simple services, the basic structure would be:

```
service-name/
├── manage.py                 # Django management script
├── requirements.txt          # Service dependencies
├── config/
│   ├── settings.py          # All settings in single file
│   ├── urls.py              # URL routing
│   ├── asgi.py              # ASGI application
│   └── wsgi.py              # WSGI application
├── apps/
│   └── app-name/
│       ├── models/          # Database models
│       ├── views/           # API endpoints
│       ├── serializers/     # DRF serializers
│       ├── services/        # Business logic
│       ├── middleware/      # Custom middleware
│       ├── validators/      # Custom validators
│       └── urls.py          # App-level routing
└── keys/                    # Cryptographic keys (auth_service only)
```

#### Production-Ready Structure (Used in This Project)
For multi-environment deployments, settings are organized by environment:

```
service-name/
├── manage.py                 # Django management script
├── requirements.txt          # Service dependencies
├── config/
│   ├── settings/            # Environment-specific settings
│   │   ├── __init__.py
│   │   ├── base.py          # Shared config (installed apps, middleware)
│   │   ├── dev.py           # Development overrides (DEBUG, DB, logging)
│   │   ├── prod.py          # Production overrides (security, caching)
│   │   └── test.py          # Test environment (in-memory DB)
│   ├── urls.py              # URL routing (shared)
│   ├── asgi.py              # ASGI application
│   ├── wsgi.py              # WSGI application
│   ├── hashers.py           # Custom password hashers (auth_service)
│   └── __init__.py
├── apps/
│   └── app-name/
│       ├── models/          # Database models
│       │   └── __init__.py
│       ├── views/           # REST API endpoints
│       │   └── __init__.py
│       ├── serializers/     # DRF serializers
│       │   └── __init__.py
│       ├── services/        # Business logic (reusable)
│       │   └── __init__.py
│       ├── middleware/      # Custom middleware
│       │   └── __init__.py
│       ├── validators/      # Custom validators
│       │   └── __init__.py
│       ├── authentication/  # Auth handlers
│       │   └── __init__.py
│       ├── templates/       # HTML templates (minimal, dev/testing only)
│       │   └── app-name/
│       ├── migrations/      # Database migrations
│       ├── urls.py          # App-level routing
│       └── __init__.py
├── shared/                  # Shared utilities (master-service only)
│   ├── base_models.py       # Abstract base classes
│   ├── utils.py             # Common functions
│   └── __init__.py
├── uploads/                 # File uploads (if needed)
├── migrations/              # Database migrations
├── keys/                    # Cryptographic keys (auth_service only)
│   ├── dev_private.pem      # Development RSA private key
│   ├── dev_public.pem       # Development RSA public key
│   └── prod_public.pem      # Production RSA public key
└── __init__.py
```

#### Key Differences

| Aspect | Generic | Production-Ready (This Project) |
|--------|---------|--------------------------------|
| **Settings** | Single `settings.py` | `settings/` folder with env-specific files |
| **Usage** | `python manage.py runserver` | `export DJANGO_SETTINGS_MODULE=config.settings.dev` |
| **Database** | Hardcoded or env var | Environment-specific in dev.py, prod.py |
| **Logging** | Basic | Can be different per environment |
| **Scalability** | Limited | Easily deployable to staging/production |

#### Design Philosophy: API-First (No Templates)

**This project is designed as API-first for React/frontend consumption**:

- ✅ **REST endpoints** return JSON only
- ✅ **All business logic** in services layer
- ✅ **Serializers** handle data validation and transformation
- ✅ **Templates minimal** (only for authentication testing/HTML form login)
- ✅ **Frontend agnostic** - React, Vue, Angular, mobile apps can consume the same APIs
- ✅ **Stateless responses** - no server-side rendering

**Template Usage** (Minimal - Development/Testing Only):
```python
# auth_service/apps/authentication/templates/auth/
├── login.html              # HTML form for manual testing
└── login_success.html      # Token display after form login
```

**Production API Responses** (JSON):
```bash
# Login endpoint returns JSON
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Response
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "admin",
    "groups": ["administrators"]
  }
}
```

**Frontend Integration Example** (React):
```javascript
// Frontend stores tokens in localStorage/context
const response = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});

const { access_token, refresh_token } = await response.json();

// All subsequent requests include the token
fetch('http://localhost:8000/api/master/countries/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

### Service Communication

**Internal Service-to-Service Communication**:
- Services communicate via HTTP REST APIs
- Authentication via JWT tokens in Authorization header
- Context headers passed through proxy:
  - `X-User-Id`: Current user ID
  - `X-Username`: Current username
  - `X-Groups`: User group memberships

**Example Flow**:
```
Client
  ↓
API Gateway (validates JWT)
  ↓
Adds X-User-Id, X-Username, X-Groups headers
  ↓
Master Service (validates headers, performs operation)
  ↓
Response back through Gateway
```

---

## Technologies Stack

### Backend Framework
- **Django 4.x** - Web framework
- **Django REST Framework (DRF)** - REST API development
- **drf-yasg** - Swagger/OpenAPI documentation

### Databases
- **MySQL/MariaDB** - Auth Service (user authentication, audit logs)
  - Database: `auth_service_db`
  - Configured via: `auth_service/config/settings/dev.py`
  - phpMyAdmin compatible
  - Uses native Django auth tables + custom audit log table
- **MySQL/MariaDB** - Master Service (master data, equipment data)
  - Database: `master_service_db`
  - Configured via: `master-service/config/settings/dev.py`
  - phpMyAdmin compatible

### Authentication & Security
- **PyJWT** - JWT token creation and validation
- **cryptography** - RSA key handling
- **python-decouple** - Environment variable management
- **python-dotenv** - .env file support
- **mysqlclient** - MySQL/MariaDB database driver
- **PBKDF2-SHA256** - Password hashing (built-in Django)

### API & Communication
- **requests** - HTTP client for inter-service communication
- **django-cors-headers** - CORS handling
- **asgiref** - ASGI utilities

### Development Tools
- **setuptools** - Package distribution
- **wheel** - Binary package format

### Key Dependencies

**Root Requirements** (`requirements.txt`):
```
Django
djangorestframework
PyJWT
python-decouple
python-dotenv
requests
django-cors-headers
mysqlclient
cryptography
```

### Environment Configuration

Services use environment variables for configuration (defaults in `config/settings/dev.py`):

```bash
# Auth Service
JWT_ALGORITHM=RS256                                    # Default: RS256
JWT_ISSUER=auth_service                               # Default: auth_service
JWT_PRIVATE_KEY_PATH=/path/to/keys/dev_private.pem    # RSA private key for signing
JWT_PUBLIC_KEY_PATH=/path/to/keys/dev_public.pem      # RSA public key for verification
DJANGO_SECRET_KEY=dev-only-secret                      # Session/CSRF secret

# Database (MySQL/MariaDB)
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=auth_service_db or master_service_db
DATABASE_USER=root                                     # phpMyAdmin accessible
DATABASE_PASSWORD=admin@123
DATABASE_HOST=127.0.0.1
DATABASE_PORT=3306

# API Gateway
JWT_PUBLIC_KEY_PATH=/path/to/keys/dev_public.pem
JWT_ALGORITHM=RS256
JWT_ISSUER=auth_service
```

---

## Coding Practices & Patterns

### 1. **Model Design**

**Base Model Inheritance**:
```python
class BaseMaster(models.Model):
    unique_id = models.CharField(
        max_length=40,
        unique=True,
        null=True,
        default=None,
        editable=False,
    )  # System-generated identifier
    is_active = models.BooleanField(default=True)      # Logical status
    is_deleted = models.BooleanField(default=False)    # Soft delete flag
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    updated_at = models.DateTimeField(auto_now=True)      # Update timestamp
    created_by = models.CharField(max_length=40, null=True)  # User tracking
    updated_by = models.CharField(max_length=40, null=True)  # User tracking
    
    class Meta:
        abstract = True
```

**Benefits**:
- Consistent audit trails across all entities
- Soft delete capability (logical deletion)
- Automatic timestamp management
- User tracking for compliance

**Example Model**:
```python
class City(BaseMaster):
    continent_id = models.ForeignKey(Continent, on_delete=models.PROTECT)
    country_id = models.ForeignKey(Country, on_delete=models.PROTECT)
    state_id = models.ForeignKey(State, on_delete=models.PROTECT)
    district_id = models.ForeignKey(District, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.state_id.name})"
    
    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
```

**Key Patterns**:
- Foreign keys use `to_field="unique_id"` for custom identifiers
- `on_delete=models.PROTECT` prevents accidental deletions
- Override `delete()` for soft delete behavior (logical deletion)
- Related names enable reverse lookups
- All models stored in MySQL/MariaDB with phpMyAdmin access

**Soft Delete Implementation**:
```python
def delete(self, *args, **kwargs):
    """Logical deletion: mark as deleted instead of removing from DB"""
    self.is_deleted = True
    self.is_active = False
    self.save(update_fields=["is_deleted", "is_active"])
```

---

### 2. **Serializer Pattern (DRF)**

**Validation at Serializer Level**:
```python
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    
    def validate_username(self, value):
        if not value.strip():
            raise serializers.ValidationError("Username cannot be empty")
        return value
    
    def validate(self, data):
        # Cross-field validation
        return data
```

**Benefits**:
- Input validation before business logic
- Automatic type conversion
- Error message standardization
- Nested serialization support

---

### 3. **View Design (APIView Pattern)**

**Authentication-Aware Views**:
```python
class LoginView(APIView):
    authentication_classes = []  # No auth required for login
    permission_classes = []      # Public endpoint
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Business logic
        user = authenticate(username=..., password=...)
        
        if not user:
            return Response(
                {"error": "INVALID_CREDENTIALS"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        # Success response
        return Response({
            "access_token": token,
            "user": {...}
        }, status=status.HTTP_200_OK)
```

**Best Practices**:
- Explicit `authentication_classes` and `permission_classes`
- Use DRF `Response` for consistent serialization
- Proper HTTP status codes
- Standardized error responses

---

### 4. **Middleware Pattern**

**JWT Authentication Middleware**:
```python
class JWTAuthenticationMiddleware:
    EXACT_EXCLUDED_PATHS = {"/api/auth/login/", "/api/auth/refresh/"}
    PREFIX_EXCLUDED_PATHS = ("/api/master/api/docs/",)
    
    def __call__(self, request):
        # Skip auth for public paths
        if request.path in EXACT_EXCLUDED_PATHS:
            return self.get_response(request)
        
        # Extract and validate token
        auth_header = request.headers.get("Authorization")
        token = auth_header.split(" ")[1]
        
        try:
            payload = decode_token(token, expected_type="access")
        except JWTExpiredError:
            return JsonResponse({"detail": "Token expired"}, status=401)
        
        # Attach payload to request
        request.jwt_payload = payload
        return self.get_response(request)
```

**Pattern Benefits**:
- Centralized authentication
- Path-based exclusions (public endpoints)
- Clean error handling
- Request enrichment (jwt_payload)

---

### 5. **Service Layer Pattern**

**Business Logic Separation**:
```python
# services/audit_utils.py
def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def get_user_agent(request):
    """Extract User-Agent"""
    return request.META.get('HTTP_USER_AGENT', '')

def parse_browser_os(user_agent):
    """Parse browser and OS from User-Agent"""
    # Implementation
    return browser, os
```

**Audit Service Usage**:
```python
AuthAuditLog.objects.create(
    user=user,
    event_type="LOGIN_SUCCESS",
    ip_address=get_client_ip(request),
    user_agent=get_user_agent(request),
    browser=browser,
    os=os,
    metadata={"username": user.username},
)
```

**Benefits**:
- Reusable business logic
- Testable functions
- Single responsibility
- Easy to maintain

**Audit Implementation**:
```python
# All login attempts are logged to AuthAuditLog table
AuthAuditLog.objects.create(
    user=user,                                         # Null for failed attempts
    event_type="LOGIN_SUCCESS" or "LOGIN_FAILED",    # Event classification
    ip_address=get_client_ip(request),                # Client IP extraction
    user_agent=get_user_agent(request),               # Browser info
    browser=parse_browser_os(user_agent)[0],          # Browser name
    os=parse_browser_os(user_agent)[1],               # OS name
    failure_reason="INVALID_CREDENTIALS",            # For failed attempts
    metadata={"username": username},                  # Additional context
    created_at=auto_now_add                           # Timestamp
)
```

**Audit Log Indexes**:
- `event_type` - Filter by login success/failure
- `created_at` - Time-based queries

---

### 6. **API Gateway Proxy Pattern**

**Request Forwarding with Context**:
```python
class MasterServiceProxy(View):
    def dispatch(self, request, *args, **kwargs):
        # Route to service
        path = request.path.replace("/api/master/", "")
        url = f"http://127.0.0.1:8002/{path}"
        
        # Build headers
        headers = {
            "X-User-Id": str(request.jwt_payload.get("sub")),
            "X-Username": request.jwt_payload.get("username"),
            "X-Groups": ",".join(request.jwt_payload.get("groups", [])),
        }
        
        # Forward request
        response = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.GET,
            data=request.body,
        )
        
        return JsonResponse(response.json())
```

**Pattern Benefits**:
- Single entry point
- User context propagation
- Service isolation
- Easy to add cross-cutting concerns

---

### 7. **Error Handling**

**Custom Exceptions**:
```python
class JWTDecodeError(Exception):
    """Base JWT decode error"""

class JWTExpiredError(JWTDecodeError):
    """Token expired"""

class JWTInvalidError(JWTDecodeError):
    """Token invalid or tampered"""
```

**Usage in Middleware**:
```python
try:
    payload = decode_token(token, expected_type="access")
except JWTExpiredError:
    return JsonResponse({"detail": "Token expired"}, status=401)
except JWTInvalidError:
    return JsonResponse({"detail": "Invalid token"}, status=401)
```

**Benefits**:
- Domain-specific exceptions
- No framework leakage
- Consistent error handling
- Clean try-catch blocks

---

### 8. **URL Routing Pattern**

**Service URLs**:
```python
# auth_service/apps/authentication/urls.py
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
]

# master-service/apps/common_master/urls.py
urlpatterns = [
    path('countries/', CountryView.as_view()),
    path('states/', StateView.as_view()),
    path('cities/', CityView.as_view()),
]
```

**Gateway Routing**:
```python
# api_gateway/gateway/urls.py
urlpatterns = [
    path('api/auth/', include('auth_service.apps.authentication.urls')),
    path('api/master/', MasterServiceProxy.as_view()),
]
```

---

### 9. **Settings Management**

**Environment-Based Settings**:
```python
# settings/base.py (shared config)
INSTALLED_APPS = [...]
MIDDLEWARE = [...]
DATABASES = {...}

# settings/dev.py (development)
from .base import *
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# settings/prod.py (production)
from .base import *
DEBUG = False
ALLOWED_HOSTS = ["example.com"]
```

**Usage**:
```bash
export DJANGO_SETTINGS_MODULE=config.settings.dev
python manage.py runserver
```

---

### 10. **Documentation** ✅ **Interactive API Docs**

**API Documentation with drf-yasg (Swagger & ReDoc)**:

The system provides **two powerful ways** to explore and understand the API:

#### **Swagger UI - Interactive Testing** 🎯
- Best for: Testing API endpoints directly from the browser
- Features: Try-it-out button, request/response visualization, parameter exploration
- Format: Human-friendly UI with interactive forms
- Use case: Quick testing, learning endpoints, debugging

#### **ReDoc - Beautiful Documentation** 📖
- Best for: Reading comprehensive API documentation
- Features: Clean, searchable, organized by tags, excellent for understanding specs
- Format: Markdown-based, right-side response examples
- Use case: Understanding API design, exploring data models, onboarding new developers
- Why useful:
  - ✅ Cleaner visual layout than Swagger
  - ✅ Better for mobile/tablet viewing
  - ✅ Excellent for learning API structure
  - ✅ Searchable documentation
  - ✅ Download OpenAPI spec option
  - ✅ Perfect for sharing with non-technical stakeholders

```python
# config/urls.py
schema_view = get_schema_view(
    openapi.Info(
        title="Master Service API",
        default_version="v1",
        description="Master and equipment data endpoints",
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path("api/docs/swagger/", schema_view.with_ui("swagger")),  # Interactive testing
    path("api/docs/redoc/", schema_view.with_ui("redoc")),      # Beautiful docs
    path("api/docs/schema.json", schema_view.without_ui(...)),   # Raw OpenAPI spec
]
```

**Available Endpoints** (All services):

| Service | Swagger UI | ReDoc | OpenAPI Schema |
|---------|-----------|-------|---|
| **Auth Service** (8001) | [http://localhost:8001/swagger/](http://localhost:8001/swagger/) | [http://localhost:8001/redoc/](http://localhost:8001/redoc/) | [http://localhost:8001/swagger.json](http://localhost:8001/swagger.json) |
| **Master Service** (8002) | [http://localhost:8002/api/docs/swagger/](http://localhost:8002/api/docs/swagger/) | [http://localhost:8002/api/docs/redoc/](http://localhost:8002/api/docs/redoc/) | [http://localhost:8002/api/docs/schema.json](http://localhost:8002/api/docs/schema.json) |
| **API Gateway** (8000) | ⚠️ No docs | ⚠️ No docs | Routes to auth/master services |

**Quick Links for Development**:
```
Authentication Service:
  Swagger:  http://0.0.0.0:8001/swagger/ or http://127.0.0.1:8001/swagger/
  ReDoc:    http://0.0.0.0:8001/redoc/ or http://127.0.0.1:8001/redoc/

Master Data Service:
  Swagger:  http://0.0.0.0:8002/api/docs/swagger/ or http://127.0.0.1:8002/api/docs/swagger/
  ReDoc:    http://0.0.0.0:8002/api/docs/redoc/ or http://127.0.0.1:8002/api/docs/redoc/
```

**How to Use ReDoc for Documentation**:
1. Open ReDoc in your browser
2. Use the search feature (Ctrl+F) to find specific endpoints
3. Click on endpoint to see full details: method, parameters, request body, response
4. View request/response examples on the right side
5. Understand data models and relationships
6. Download/export OpenAPI specification for external tools

---

## Authentication & Security

### JWT Token Flow

```
1. User Login
   ├─ POST /api/auth/login/ (API endpoint)
   ├─ GET /api/auth/login_page/ → POST (HTML form)
   ├─ Username + Password
   ├─ Credentials validated against Django auth tables (MySQL)
   ├─ IP/User-Agent extracted and logged to AuthAuditLog
   ├─ Password verified using PBKDF2-SHA256 (120K iterations)
   └─ Return 401 or proceed to token generation

2. Token Generation
   ├─ Create Access Token (1 hour TTL - default 3600s)
   ├─ Create Refresh Token (7 days - default 604800s, configurable)
   ├─ Sign with Private Key (RSA-256)
   ├─ Payload: {sub, username, groups, iat, exp, iss, type}
   └─ Return tokens to client + audit log (LOGIN_SUCCESS)

3. Authenticated Requests
   ├─ Client includes: Authorization: Bearer <access_token>
   ├─ API Gateway validates signature with Public Key
   ├─ Checks expiration and issuer
   ├─ Extracts user context (id, username, groups)
   └─ Forwards to service with X-User-Id, X-Username, X-Groups headers

4. Token Refresh ✅ **IMPLEMENTED**
   ├─ POST /api/auth/refresh/ - Full implementation
   ├─ GET /api/auth/refresh/ - Alternative method
   ├─ Include Refresh Token in request body
   ├─ Validate refresh token signature & expiration
   ├─ Generate new Access Token (same user)
   ├─ Return new access token + original refresh token
   └─ User context preserved (id, username, groups)

5. Failed Login
   ├─ Invalid credentials detected
   ├─ AuthAuditLog created with LOGIN_FAILED event
   ├─ failure_reason: "INVALID_CREDENTIALS"
   └─ metadata: {username, ip_address, browser, os}
```

**✅ Refresh Token**: Fully implemented with both GET and POST methods. Validates token signature, expiration, and user existence. Returns new access token while keeping original refresh token for further rotations.

### Token Refresh Implementation ✅ **NEW**

The refresh token endpoint is fully implemented and production-ready:

**Endpoint Details**:
- **URL**: `POST /api/auth/refresh/` or `GET /api/auth/refresh/`
- **Authentication**: Not required (refresh token validates itself)
- **Content-Type**: application/json

**Request Format**:
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response Format**:
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "admin",
    "groups": ["administrators"]
  }
}
```

**Validation Logic**:
1. ✅ Extracts refresh token from request body
2. ✅ Decodes and validates token signature using public key
3. ✅ Checks token expiration (default 604800 seconds = 7 days)
4. ✅ Verifies token type is "refresh"
5. ✅ Looks up user by ID from token payload
6. ✅ Generates new access token (1 hour TTL)
7. ✅ Returns both tokens with user context

**Error Handling**:
- `400 BAD REQUEST` - Missing refresh_token in request
- `401 UNAUTHORIZED` - Token expired, invalid signature, or user not found

**Example Usage**:
```bash
# Get initial tokens via login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Response includes access_token and refresh_token
# When access_token expires, refresh it:

curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"eyJhbGciOi..."}'

# New access_token ready to use
```

**Configuration**:
- Access Token TTL: `JWT_ACCESS_TOKEN_LIFETIME` (default: 3600 seconds = 1 hour)
- Refresh Token TTL: `JWT_REFRESH_TOKEN_LIFETIME` (default: 604800 seconds = 7 days)
- Both configurable via environment variables in `auth_service/config/settings/base.py`

### Role & Permission Management ✅ **NEW**

The system now includes a comprehensive role-based access control (RBAC) system:

**Role Management**:
- Create, read, update, soft delete user roles
- Each role is a distinct entity with unique name validation
- Soft delete capability (logical deletion with `is_active` flag)
- Support for role descriptions and metadata
- Endpoints:
  - `GET /api/auth/roles/` - List all roles with filtering
  - `POST /api/auth/roles/` - Create new role
  - `GET /api/auth/roles/{id}/` - Retrieve role details
  - `PUT /api/auth/roles/{id}/` - Update role
  - `DELETE /api/auth/roles/{id}/` - Soft delete role

**Permission Model**:
- Proxy models (no database tables) for defining permissions
- CRUD permissions for each entity:
  - **Geographic Masters**: Country, State, District, City, Continent
  - **Organizational Masters**: Plant, Site, Ward, Zone
  - **Equipment Masters**: Equipment Type
- Permission format: `master_{entity}_{action}` (e.g., `master_country_create`)
- Centralized permission list at `GET /api/auth/permissions/`
- Master-specific permissions grouped by entity at `GET /api/auth/permissions/master/`

**Group Permission Assignment**:
- Link permissions to Django Groups (roles)
- Many-to-many relationship via `auth_group_permissions` table
- Endpoints:
  - `GET /api/auth/group-permissions/` - List all groups with permissions
  - `POST /api/auth/group-permissions/` - Assign permissions to group
  - `GET /api/auth/group-permissions/groups/` - List available groups (dropdown)
  - `GET /api/auth/group-permissions/permissions/` - List available permissions
  - `GET /api/auth/group-permissions/by-group/{group_id}/` - Get permissions for specific group
  - `DELETE /api/auth/group-permissions/remove/{group_id}/` - Remove all permissions from group

**User-Role Assignment**:
- Users are assigned to roles (UserRole → Group mapping)
- Users inherit all permissions from their assigned groups
- Multiple roles per user supported
- User creation includes role assignment

**Example Workflow**:
```bash
# 1. Create a role
POST /api/auth/roles/
{
  "name": "manager",
  "description": "Department manager role",
  "is_active": true
}

# 2. Get available master permissions
GET /api/auth/permissions/master/

# 3. Assign permissions to the role
POST /api/auth/group-permissions/
{
  "group_id": 1,
  "permission_ids": [1, 2, 3, 4]  # Create, read, update, delete country
}

# 4. Create user and assign role
POST /api/auth/users/
{
  "username": "john_manager",
  "password": "secure_pass",
  "email": "john@example.com",
  "role_ids": ["role-uuid"]  # Auto-assign permissions
}
```

### Key Security Features

1. **Password Hashing (Auth Service)**
   - Algorithm: PBKDF2-SHA256
   - Iterations: 120,000 (explicit in `config/hashers.py`)
   - Django built-in validators:
     - UserAttributeSimilarityValidator
     - MinimumLengthValidator
     - CommonPasswordValidator
     - NumericPasswordValidator
   - Fallback hashers: Argon2, BCrypt-SHA256

2. **RSA-256 (Asymmetric Cryptography)**
   - Private key signs tokens (auth_service only, stored in `keys/dev_private.pem`)
   - Public key validates tokens (all services, stored in `keys/dev_public.pem`)
   - Keys never exposed in settings or version control

3. **JWT Validation**
   - Signature verification (RS256 only, symmetric algorithms blocked)
   - Expiration checking (404-day default)
   - Issuer validation (`auth_service`)
   - Algorithm enforcement
   - Token type validation (`access` vs `refresh`)

4. **Audit Logging** ✅ **WORKING**
   - **All login attempts logged** to `auth_audit_log` table (MySQL)
   - Success tracking: `LOGIN_SUCCESS` events
   - Failure tracking: `LOGIN_FAILED` events with `INVALID_CREDENTIALS` reason
   - Client context captured:
     - IP address (with X-Forwarded-For proxy support)
     - User-Agent string
     - Browser name (parsed from User-Agent)
     - Operating system (parsed from User-Agent)
   - Indexed by: `event_type`, `created_at` for fast queries
   - Metadata field for extensibility (JSON)
   - **Accessible via phpMyAdmin** for manual inspection

5. **Database Layer** ✅ **MySQL/MariaDB**
   - Authentication tables (Django's built-in)
   - Audit log table (`auth_audit_log`)
   - Master service tables with soft delete
   - All phpMyAdmin compatible
   - Connection pooling via `CONN_MAX_AGE: 60`

6. **Soft Delete**
   - Data never truly deleted
   - Logical deletion with `is_deleted` flag
   - Audit trail preserved
   - Compliance-friendly

7. **CORS Security**
   - Whitelist allowed origins
   - CSRF protection via middleware (safe with JWT bearer tokens)
   - Authorization header exposure configured

8. **Role-Based Access Control (RBAC)** ✅ **NEW**
   - Granular permission system with CRUD operations per entity
   - Django Group integration for role-permission mapping
   - User-to-role assignment with permission inheritance
   - Master data permission control (Country, State, City, Plant, Site, Equipment, etc.)
   - Extensible permission model for new entities
   - Audit trail for role and permission changes

---

## API Endpoints Reference ✅ **NEW**

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| POST | `/api/auth/login/` | User login (JSON API) | No |
| GET | `/api/auth/login_page/` | Login HTML form | No |
| POST | `/api/auth/refresh/` | Refresh access token (JSON body) | No |
| GET | `/api/auth/refresh/` | Refresh access token (query/body) | No |

### Permission Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/api/auth/permissions/` | List all system permissions | Yes |
| GET | `/api/auth/permissions/?codename={pattern}` | Filter permissions by codename | Yes |
| GET | `/api/auth/permissions/master/` | Get master permissions grouped by entity | Yes |

### Role Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/api/auth/roles/` | List all roles with filtering & search | Yes |
| GET | `/api/auth/roles/?is_active=true&ordering=name` | Get active roles sorted by name | Yes |
| GET | `/api/auth/roles/?search=manager&ordering=name` | Search roles by name pattern | Yes |
| POST | `/api/auth/roles/` | Create new role | Yes |
| GET | `/api/auth/roles/{id}/` | Get role details | Yes |
| PUT | `/api/auth/roles/{id}/` | Update role | Yes |
| DELETE | `/api/auth/roles/{id}/` | Soft delete (deactivate) role | Yes |
| DELETE | `/api/auth/roles/{id}/?hard_delete=true` | Hard delete role | Yes |

### Group-Permission Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/api/auth/group-permissions/` | List all groups with their permissions | Yes |
| POST | `/api/auth/group-permissions/` | Assign permissions to group | Yes |
| GET | `/api/auth/group-permissions/groups/` | List available groups (dropdown) | Yes |
| GET | `/api/auth/group-permissions/permissions/` | List available permissions (multi-select) | Yes |
| GET | `/api/auth/group-permissions/by-group/{group_id}/` | Get permissions for specific group | Yes |
| DELETE | `/api/auth/group-permissions/remove/{group_id}/` | Remove all permissions from group | Yes |

### User Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/api/auth/users/` | List all users | Yes |
| POST | `/api/auth/users/` | Create user with role assignment | Yes |
| GET | `/api/auth/users/{id}/` | Get user details | Yes |
| PUT | `/api/auth/users/{id}/` | Update user | Yes |
| DELETE | `/api/auth/users/{id}/` | Delete user | Yes |

---

## Project Structure

```
erp-backend/
├── README.md                              # This file
├── requirements.txt                       # Root dependencies
│
├── api_gateway/                           # API Gateway Service
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── gateway/
│   │   ├── middleware/
│   │   │   └── jwt_auth.py               # JWT authentication
│   │   ├── views/
│   │   │   └── proxy.py                  # Service proxy
│   │   └── urls.py
│   └── static/
│
├── auth_service/                          # Authentication Service
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   └── prod.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── hashers.py
│   ├── apps/
│   │   └── authentication/
│   │       ├── models/
│   │       │   ├── audit.py              # Audit log model
│   │       │   ├── permissions.py        # Permission proxy models (NEW)
│   │       │   ├── user_role.py          # UserRole model (NEW)
│   │       │   ├── user_profile.py       # User profile extension
│   │       │   └── __init__.py
│   │       ├── views/
│   │       │   ├── auth.py               # Login/refresh endpoints
│   │       │   ├── permission_and_role.py # Role/permission endpoints (NEW)
│   │       │   ├── user.py               # User management endpoints (NEW)
│   │       │   └── __init__.py
│   │       ├── serializers/
│   │       │   ├── login.py
│   │       │   ├── token.py
│   │       │   ├── permission_and_role.py # Role/permission serializers (NEW)
│   │       │   ├── user.py               # User serializers (NEW)
│   │       │   └── __init__.py
│   │       ├── services/
│   │       │   ├── token_service.py
│   │       │   ├── audit_utils.py
│   │       │   └── __init__.py
│   │       ├── templates/
│   │       │   └── auth/
│   │       ├── middleware/
│   │       │   └── jwt_auth.py
│   │       ├── migrations/
│   │       ├── urls.py
│   │       └── __init__.py
│   ├── keys/                             # JWT signing keys
│   │   ├── dev_public.pem
│   │   ├── dev_private.pem
│   │   └── prod_public.pem
│   └── migrations/
│
├── master-service/                        # Master Data Service
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   ├── prod.py
│   │   │   └── test.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── common_master/                # Geographic & org structure
│   │   │   ├── models/
│   │   │   │   ├── continent.py
│   │   │   │   ├── country.py
│   │   │   │   ├── state.py
│   │   │   │   ├── district.py
│   │   │   │   ├── city.py
│   │   │   │   ├── plant.py
│   │   │   │   ├── site.py
│   │   │   │   ├── ward.py
│   │   │   │   ├── zone.py
│   │   │   │   └── __init__.py
│   │   │   ├── views/
│   │   │   │   ├── continent.py
│   │   │   │   ├── country.py
│   │   │   │   ├── state.py
│   │   │   │   ├── city.py
│   │   │   │   ├── plant.py
│   │   │   │   ├── site.py
│   │   │   │   └── __init__.py
│   │   │   ├── serializers/
│   │   │   │   ├── continent_serializer.py
│   │   │   │   ├── country_serializer.py
│   │   │   │   ├── state_serializer.py
│   │   │   │   ├── city_serializer.py
│   │   │   │   ├── plant.py
│   │   │   │   ├── site.py
│   │   │   │   └── __init__.py
│   │   │   ├── validators/
│   │   │   │   ├── unique_name_validator.py
│   │   │   │   └── __init__.py
│   │   │   ├── middleware/
│   │   │   │   └── jwt_auth.py
│   │   │   ├── services.py
│   │   │   ├── urls.py
│   │   │   └── __init__.py
│   │   │
│   │   └── em_master/                   # Equipment Master
│   │       ├── models/
│   │       │   ├── equipment_typemaster.py
│   │       │   └── __init__.py
│   │       ├── views/
│   │       │   └── __init__.py
│   │       ├── serializers/
│   │       │   ├── equipment_typemaster_serializer.py
│   │       │   └── __init__.py
│   │       ├── validators/
│   │       │   └── __init__.py
│   │       ├── middleware/
│   │       │   └── jwt_auth.py
│   │       ├── services.py
│   │       ├── urls.py
│   │       └── __init__.py
│   │
│   ├── shared/
│   │   ├── base_models.py                # Abstract base model
│   │   └── utils.py
│   │
│   ├── migrations/
│   └── uploads/
│       └── equipmentmastertype/
│
├── common_lib/                             # Shared Libraries
│   ├── __init__.py
│   ├── erp_jwt/
│   │   ├── encoder.py                    # JWT creation
│   │   ├── decoder.py                    # JWT validation
│   │   └── __init__.py
│   └── utils/
│       ├── helpers.py
│       └── __init__.py
│
└── __init__.py
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- MySQL/MariaDB 5.7+ (for both auth_service and master-service)
- phpMyAdmin (optional, for database inspection)
- pip and virtualenv

### Installation

1. **Clone and Setup**
   ```bash
   cd /mnt/projects/erp-backend
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify JWT Keys** (already in `auth_service/keys/`)
   ```bash
   # Check keys exist
   ls -la auth_service/keys/
   # Output should show: dev_private.pem, dev_public.pem
   
   # To regenerate (if needed):
   openssl genrsa -out auth_service/keys/dev_private.pem 2048
   openssl rsa -in auth_service/keys/dev_private.pem -pubout -out auth_service/keys/dev_public.pem
   ```

4. **Setup Auth Service**
   ```bash
   cd auth_service
   export DJANGO_SETTINGS_MODULE=config.settings.dev
   python manage.py migrate                    # Create tables in MySQL
   python manage.py createsuperuser            # Create admin user for testing
   python manage.py runserver 8001
   ```

5. **Setup Master Service**
   ```bash
   cd master-service
   export DJANGO_SETTINGS_MODULE=config.settings.dev
   python manage.py migrate                    # Create tables in MySQL
   python manage.py runserver 8002
   ```

6. **Run API Gateway**
   ```bash
   cd api_gateway
   python manage.py runserver 8000
   ```

### Testing Role & Permission Management ✅ **NEW**

**1. Get All Permissions**
```bash
curl -X GET http://localhost:8000/api/auth/permissions/ \
  -H "Authorization: Bearer <access_token>"
```

**2. Get Master Permissions Grouped by Entity**
```bash
curl -X GET http://localhost:8000/api/auth/permissions/master/ \
  -H "Authorization: Bearer <access_token>"

# Response shows permissions grouped by entity (country, state, city, etc.)
```

**3. Create a New Role**
```bash
curl -X POST http://localhost:8000/api/auth/roles/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "manager",
    "description": "Department Manager Role",
    "is_active": true
  }'
```

**4. List Roles with Filtering**
```bash
# Get active roles, ordered by name
curl -X GET "http://localhost:8000/api/auth/roles/?is_active=true&ordering=name" \
  -H "Authorization: Bearer <access_token>"

# Search by name pattern
curl -X GET "http://localhost:8000/api/auth/roles/?search=admin&ordering=name" \
  -H "Authorization: Bearer <access_token>"
```

**5. Get Available Groups for Permission Assignment**
```bash
curl -X GET http://localhost:8000/api/auth/group-permissions/groups/ \
  -H "Authorization: Bearer <access_token>"
```

**6. Assign Permissions to a Role**
```bash
curl -X POST http://localhost:8000/api/auth/group-permissions/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": 1,
    "permission_ids": [1, 2, 3, 4]
  }'
```

**7. Get Permissions Assigned to a Role**
```bash
curl -X GET "http://localhost:8000/api/auth/group-permissions/by-group/1/" \
  -H "Authorization: Bearer <access_token>"
```

**8. Create User with Role Assignment**
```bash
curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_manager",
    "password": "SecurePass@123",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role_ids": ["12345678-1234-5678-1234-567812345678"]
  }'
```

**9. Remove All Permissions from a Role**
```bash
curl -X DELETE "http://localhost:8000/api/auth/group-permissions/remove/1/" \
  -H "Authorization: Bearer <access_token>"
```

### Testing Token Refresh ✅ **NEW**

**1. Login and Get Tokens**
```bash
RESPONSE=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

# Extract tokens (bash jq required)
ACCESS_TOKEN=$(echo $RESPONSE | jq -r '.access_token')
REFRESH_TOKEN=$(echo $RESPONSE | jq -r '.refresh_token')

echo "Access Token: $ACCESS_TOKEN"
echo "Refresh Token: $REFRESH_TOKEN"
```

**2. Verify Access Token Works**
```bash
curl -X GET http://localhost:8000/api/master/countries/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**3. Simulate Token Expiration and Refresh**
```bash
# Wait or the access token will expire in 1 hour
# Then refresh it:

curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}"

# Response includes new access_token
```

**4. Test Error Handling - Missing Token**
```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{}'

# Response: {"error": "refresh_token is required"} (400 BAD REQUEST)
```

**5. Test Error Handling - Invalid Token**
```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"invalid_token_here"}'

# Response: {"error": "Invalid refresh token"} (401 UNAUTHORIZED)
```

### Testing the Flow

1. **Login**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123"}'
   ```

2. **Use Token**
   ```bash
   curl -X GET http://localhost:8000/api/master/countries/ \
     -H "Authorization: Bearer <access_token>"
   ```

3. **Access Interactive API Documentation** ✅
   
   Choose your preferred documentation style:
   
   **Option A: Swagger UI** (Interactive Testing)
   - Auth Service: http://localhost:8001/swagger/
   - Master Service: http://localhost:8002/api/docs/swagger/
   - Features: Try-out buttons, request/response visualization, parameter forms
   
   **Option B: ReDoc** (Beautiful Documentation) 📖 *Recommended for learning*
   - Auth Service: http://localhost:8001/redoc/
   - Master Service: http://localhost:8002/api/docs/redoc/
   - Features: Cleaner layout, searchable, excellent for understanding API design, mobile-friendly
   - Why use ReDoc:
     - ✅ Better organized and easier to navigate
     - ✅ Perfect for reading comprehensive documentation
     - ✅ Excellent for onboarding new developers
     - ✅ Mobile/tablet friendly
     - ✅ Search functionality for finding endpoints
   
   **Option C: Raw OpenAPI Schema**
   - Auth Service: http://localhost:8001/swagger.json
   - Master Service: http://localhost:8002/api/docs/schema.json
   - Use for: Importing into Postman, code generation, external tools

### Testing Audit Logging

```bash
# 1. Attempt failed login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrongpassword"}'

# 2. Check audit log in MySQL (via phpMyAdmin or CLI)
mysql -u root -p auth_service_db
SELECT * FROM auth_audit_log ORDER BY created_at DESC LIMIT 5;

# Output should show:
# - event_type: LOGIN_FAILED
# - failure_reason: INVALID_CREDENTIALS
# - ip_address, user_agent, browser, os populated
# - metadata: {"username": "admin"}

# 3. Login with correct credentials and check success log
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"correctpassword"}'

# 4. Verify in audit log
SELECT event_type, user_id, ip_address, browser, os, created_at 
FROM auth_audit_log 
ORDER BY created_at DESC LIMIT 5;
```

---

## API Documentation Guide ✅ **Swagger & ReDoc**

### Why Two Documentation Formats?

**Swagger UI** and **ReDoc** serve different purposes and audiences:

| Feature | Swagger UI | ReDoc |
|---------|-----------|-------|
| **Purpose** | Interactive testing | Reading documentation |
| **Best For** | Developers testing APIs | Understanding API design |
| **UI Style** | Form-based, detailed controls | Clean, markdown-based |
| **Testing** | ✅ Try-it-out buttons | ❌ No direct testing |
| **Mobile** | ⚠️ Decent | ✅ Excellent |
| **Learning Curve** | Steep with complex specs | Gentle, intuitive |
| **Search** | ⚠️ Limited | ✅ Fast search |
| **Data Models** | Mixed with endpoints | Organized separately |
| **Share with Non-Devs** | ❌ Too technical | ✅ Perfect |

### Using ReDoc for Documentation 📖

**Why ReDoc is excellent for understanding the API**:

1. **Clean Visual Layout**
   - Endpoints on left, description in center, examples on right
   - No cluttered forms or input fields
   - Perfect for reading specifications

2. **Searchable Documentation**
   - Ctrl+F to find endpoints quickly
   - Search by endpoint name, parameter, or description
   - Perfect for large APIs with 50+ endpoints

3. **Organized by Tags**
   - Endpoints grouped by feature (Auth, Roles, Permissions, etc.)
   - Easy to navigate related functionality
   - Understand API architecture at a glance

4. **Excellent Request/Response Examples**
   - Real-world example on right side
   - Shows request body and response
   - Learn by example

5. **Mobile-Friendly**
   - Perfect on tablets, phones, or small screens
   - No scrolling complex forms
   - Share on any device

6. **Perfect for Onboarding**
   - Non-technical stakeholders can understand API
   - Product managers see what's available
   - New developers learn structure quickly

7. **Download & Share**
   - Export OpenAPI specification
   - Use for code generation
   - Import into Postman/Insomnia

### Quick Comparison: When to Use What

**Use Swagger UI when you want to**:
- ✅ Test an endpoint immediately
- ✅ Send actual requests and see responses
- ✅ Debug API behavior
- ✅ Experiment with parameters
- ✅ Verify authentication works

**Use ReDoc when you want to**:
- ✅ Understand API structure
- ✅ Learn endpoint details
- ✅ Find a specific endpoint
- ✅ Read comprehensive documentation
- ✅ Onboard new team members
- ✅ Share with non-developers
- ✅ Plan API integration

### All Documentation Endpoints

**Auth Service (Port 8001)**:
```
Interactive Testing:
  POST   /swagger/                    (Swagger UI - try endpoints)

Beautiful Documentation:
  GET    /redoc/                      (ReDoc - read docs)

Raw Specification:
  GET    /swagger.json                (OpenAPI JSON format)
  GET    /swagger.yaml                (OpenAPI YAML format)
```

**Master Service (Port 8002)**:
```
Interactive Testing:
  GET    /api/docs/swagger/           (Swagger UI - try endpoints)

Beautiful Documentation:
  GET    /api/docs/redoc/             (ReDoc - read docs)

Raw Specification:
  GET    /api/docs/schema.json        (OpenAPI JSON format)
  GET    /api/docs/schema.yaml        (OpenAPI YAML format)
```

### Accessing Documentation

**In Browser** (Recommended):
```
# Auth Service ReDoc
http://localhost:8001/redoc/

# Master Service ReDoc
http://localhost:8002/api/docs/redoc/

# Or use IP address
http://0.0.0.0:8001/redoc/
http://0.0.0.0:8002/api/docs/redoc/
```

**In Terminal** (Get raw spec):
```bash
# Get OpenAPI JSON
curl http://localhost:8001/swagger.json | jq

# Get OpenAPI YAML
curl http://localhost:8001/swagger.yaml

# Save for external tools
curl http://localhost:8002/api/docs/schema.json > openapi.json
```

**Import into Postman/Insomnia**:
1. Open Postman/Insomnia
2. Import → Link → Paste endpoint URL:
   - `http://localhost:8001/swagger.json` (Auth Service)
   - `http://localhost:8002/api/docs/schema.json` (Master Service)
3. All endpoints auto-populate with descriptions, parameters, and examples

---

### Known Limitations ⚠️ & Future Enhancements

**Completed Features** ✅:
- JWT token generation (access & refresh)
- Token refresh mechanism with full validation
- Login audit logging (success & failure)
- Role-based access control (RBAC)
- Permission management system
- User-role assignment
- Group-permission linking
- Soft delete implementation
- PBKDF2-SHA256 password hashing
- CORS security
- Swagger/OpenAPI documentation

**Future Enhancements** (TODO):
1. **Permission Enforcement at Endpoints**: Add authorization decorators to enforce role-based access at master service endpoints
2. **Token Blacklisting for Logout**: Implement logout functionality by blacklisting used tokens
3. **Refresh Token Rotation**: Optionally rotate refresh tokens on each refresh for enhanced security
4. **Master Service JWT Validation**: Master service should validate JWT from context headers (currently trusts API Gateway)
5. **Multi-Factor Authentication (MFA)**: Add OTP or 2FA for enhanced security
6. **Advanced Permission Queries**: Optimize UserRole ↔ Group linking for complex permission checks
7. **Rate Limiting**: Add rate limiting to prevent brute force attacks
8. **API Key Authentication**: Support API key-based authentication for service-to-service communication

**Ready for Production** ✅:
- Role & Permission Management System
- User-Role Assignment
- Token Generation & Refresh (both access and refresh tokens)
- Audit Logging
- CORS Security
- Soft Delete Implementation
- Swagger/OpenAPI Documentation

---

## Performance & Scalability

### Horizontal Scaling
- Each service can be deployed independently
- Load balancer in front of API Gateway
- Database connection pooling
- Stateless services enable easy replication

### Optimization Strategies
1. **Database Indexing**: Unique IDs, frequently queried fields
2. **Caching**: Redis integration for token blacklisting (extensible)
3. **Async Tasks**: Celery for heavy audit logging (extensible)
4. **Connection Pooling**: psycopg2 and mysqlclient support
5. **Pagination**: Implemented in serializers for large datasets

---

## Deployment

### Docker Support (Ready to Add)
- Create Dockerfile for each service
- docker-compose.yml for local development
- Environment-specific configurations

### Production Checklist
- [ ] Update DEBUG = False
- [ ] Set ALLOWED_HOSTS to production domains
- [ ] Configure production DATABASE_URLs
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Setup log aggregation
- [ ] Configure monitoring and alerts
- [ ] Use production-grade server (Gunicorn/Uvicorn)
- [ ] Setup database backups
- [ ] Configure CI/CD pipeline

---

## Logging & Monitoring

### Built-in Logging
- Django request logging
- Authentication audit logs
- Error tracking

### Extensibility
- Structured logging with `structlog` (ready to integrate)
- Sentry for error tracking
- Prometheus metrics for monitoring

---

## Contributing

### Code Standards
1. Follow PEP 8 naming conventions
2. Use type hints where applicable
3. Write docstrings for complex functions
4. Add unit tests for business logic
5. Maintain consistent error handling

### Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - Feature branches
- `hotfix/*` - Production fixes

---

## Troubleshooting

### Common Issues

**1. JWT Token Validation Fails**
- Ensure public key path is correct
- Verify JWT_ISSUER matches token issuer
- Check token hasn't expired

**2. Service Communication Fails**
- Verify all services are running
- Check firewall rules
- Review proxy URL configuration

**3. Database Connection Errors**
- Verify database server is running
- Check connection credentials in settings
- Ensure database exists and is accessible

**4. CORS Errors**
- Check CORS_ALLOWED_ORIGINS in API Gateway
- Verify frontend origin is whitelisted
- Check Authorization header exposure settings

---

## Future Enhancements

1. **Async Support**: Implement Celery for background tasks
2. **Caching Layer**: Redis for session and token caching
3. **API Versioning**: Structured versioning strategy
4. **Rate Limiting**: Request throttling and DDoS protection
5. **GraphQL Support**: Alternative to REST API
6. **Microservice Mesh**: Service discovery and load balancing
7. **Distributed Tracing**: OpenTelemetry integration
8. **WebSocket Support**: Real-time updates for master data changes

---

## License

[Add your license information here]

---

## Contact & Support

For issues, questions, or contributions, please contact the development team.

---

**Last Updated**: January 29, 2026  
**Version**: 1.3.0  
**Latest Changes**: 
- ✅ Comprehensive API Documentation Guide (Swagger & ReDoc)
- ✅ Detailed ReDoc explanation and use cases
- ✅ All documentation endpoints documented
- ✅ Comparison tables for Swagger vs ReDoc
- ✅ Instructions for importing into Postman/Insomnia
- ✅ Token Refresh Endpoint Implementation (Full)
- ✅ Complete token validation and error handling

**Version**: 1.2.0  
**Latest Changes**: 
- ✅ Token Refresh Endpoint Implementation (Full)
- ✅ GET & POST methods for token refresh
- ✅ Comprehensive token validation logic
- ✅ Error handling for expired/invalid tokens
- ✅ Complete API documentation updated
- ✅ Testing examples for all endpoints
- ✅ Production-ready status confirmed
