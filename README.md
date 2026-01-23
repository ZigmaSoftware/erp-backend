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
7. [Project Structure](#project-structure)
8. [Getting Started](#getting-started)

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
- JWT token generation (access & refresh)
- Token refresh mechanism (configured, endpoint needs implementation)
- Audit logging (login attempts, failures, successful logins) ✅ **WORKING**
- User group management
- Password hashing (PBKDF2-SHA256 with 120,000 iterations)

**Key Components**:
- `apps/authentication/views/auth.py` - Login endpoints (API & HTML form)
- `apps/authentication/services/audit_utils.py` - Security auditing (IP, User-Agent, Browser/OS detection)
- `apps/authentication/models/audit.py` - Audit log model with event tracking
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

### 10. **Documentation**

**API Documentation with drf-yasg**:
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
    path("api/docs/swagger/", schema_view.with_ui("swagger")),
    path("api/docs/redoc/", schema_view.with_ui("redoc")),
]
```

**Auto-generated OpenAPI schema** at `/api/docs/schema.json`

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

4. Token Refresh (⚠️ Endpoint needs implementation)
   ├─ POST /api/auth/refresh/ (NOT YET IMPLEMENTED)
   ├─ Include Refresh Token in request
   ├─ Validate refresh token signature & expiration
   ├─ Generate new Access Token (same user)
   ├─ Optional: Rotate refresh token
   └─ Return new tokens

5. Failed Login
   ├─ Invalid credentials detected
   ├─ AuthAuditLog created with LOGIN_FAILED event
   ├─ failure_reason: "INVALID_CREDENTIALS"
   └─ metadata: {username, ip_address, browser, os}
```

**⚠️ Note**: Refresh token endpoint is configured but not yet implemented. Token lifetime can be extended via settings.

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
│   │       │   └── __init__.py
│   │       ├── views/
│   │       │   └── auth.py               # Login/refresh endpoints
│   │       ├── serializers/
│   │       │   ├── login.py
│   │       │   ├── token.py
│   │       │   └── __init__.py
│   │       ├── services/
│   │       │   ├── token_service.py
│   │       │   ├── audit_utils.py
│   │       │   └── __init__.py
│   │       ├── templates/
│   │       │   └── auth/
│   │       ├── middleware/
│   │       │   └── jwt_auth.py
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

3. **Access API Documentation**
   - Swagger: http://localhost:8002/api/docs/swagger/
   - ReDoc: http://localhost:8002/api/docs/redoc/

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

### Known Limitations ⚠️

**Refresh Token Endpoint Not Implemented**:
- Refresh token is generated during login
- Configuration exists: `JWT_REFRESH_TOKEN_LIFETIME=604800` (7 days)
- **TODO**: Implement `POST /api/auth/refresh/` endpoint to:
  1. Accept refresh token in request body
  2. Validate token signature and expiration
  3. Generate new access token
  4. Optionally rotate refresh token
  5. Return new tokens

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

**Last Updated**: January 23, 2026  
**Version**: 1.0.0
