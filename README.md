# Team-2-Secure-File-Sharing-System
# Secure File Sharing System

A high-performance, enterprise-grade secure file-sharing backend built with **FastAPI**, **SQLAlchemy**, and **MySQL**, featuring **AES-256 (Fernet) encryption at rest**, fine-grained role-based access control, time-limited and download-limited sharing links, and tamper-evident security audit logging.

---

## 🌟 Key Features

| **Week 1** | **Project Foundation & Database Architecture** | Modular FastAPI setup, SQLAlchemy engine & connection pooling, centralized settings, database health check, CORS middleware. | `FastAPI`, `SQLAlchemy`, `PyMySQL`, `Pydantic Settings`, `app/main.py`, `app/database/` |
| **Week 2** | **Authentication & Role-Based Access Control (RBAC)** | User schema & model, Bcrypt password hashing, stateless JWT token authentication, user registration, login, profile inspection, and admin guard rails. | `Passlib (Bcrypt)`, `python-jose`, `JWT`, `app/models/user.py`, `app/security/`, `app/dependencies/auth.py` |
| **Week 3** | **Core File Management & Storage Architecture** | File metadata model, isolated storage directory management, 10MB quota validation, authenticated file listing, and secure deletion with disk cleanup. | `FastAPI UploadFile`, `app/models/file.py`, `app/services/file_service.py`, `app/routes/file_routes.py` |
### 🔐 1. End-to-End File Security & AES-256 Encryption (Week 4)
- **Encryption at Rest**: Files uploaded to the server are immediately encrypted using **Fernet (AES-128 in CBC mode with HMAC-SHA256 authenticated encryption)** before touching disk storage.
- **Unique Per-File Keys**: Each uploaded file is assigned its own cryptographically generated encryption key. Keys are managed securely and decoupled from the raw file payloads.
- **In-Memory Decryption**: Authorized downloads decrypt data on-the-fly in memory. Plaintext bytes are never stored on the physical file system.

### 👥 2. Enhanced Sharing & Access Control (Week 5)
- **Granular Permissions**: Share files with specific users under `VIEW` or `DOWNLOAD` access levels.
- **Expiring Links**: Set time-to-live (`expires_at`) timestamps on shares; expired shares are automatically rejected.
- **Download Quotas**: Enforce maximum download limits (`download_limit`); access is revoked once the quota is reached.
- **Share Revocation**: File owners can view active shares (`GET /files/{file_id}/shares`) and revoke access instantly (`DELETE /files/{file_id}/share/{share_id}`).

### 📊 3. Security Activity Logging & Audit Trail (Week 6)
- **Centralized Event Tracking**: All authentication and file access events are logged (`LOGIN_SUCCESS`, `LOGIN_FAILED`, `FILE_UPLOADED`, `FILE_DOWNLOADED`, `FILE_DELETED`, `FILE_SHARED`, `SHARE_REVOKED`, `UNAUTHORIZED_ACCESS`).
- **IP & User Tracking**: Logs capture actor user ID, client IP address, action status, and affected resources.
- **Dedicated Admin Log Queries**: Admins can query full audit trails, failed logins, and unauthorized access attempts.

### 🛡️ 4. Dashboards & User Management (Week 7)
- **User Dashboard (`GET /dashboard`)**: Real-time storage usage statistics, file counts, outgoing/incoming shares, and recent activity history.
- **Admin Dashboard (`GET /admin/dashboard`)**: System-wide metrics including total registered users, total files, storage utilization, active vs. expired shares, total downloads, and security event summaries.
- **User Management**: Admins can list all users (`GET /users`) and deactivate malicious or suspended accounts (`PUT /users/{user_id}/deactivate`).

### 🧪 5. Comprehensive Test Suite (Week 8)
- Automated unit and integration tests covering Authentication, File Management, Granular Sharing & Permissions, and Admin & Audit Logging.
- Uses in-memory SQLite and FastAPI `TestClient` for isolated testing without altering production databases.

---

## 🏗️ Architecture & Project Structure

```
secure-file-sharing-system/
├── app/
│   ├── config/
│   │   └── settings.py          # Centralized environment variables & constants
│   ├── database/
│   │   └── database.py          # SQLAlchemy engine, session maker, DB dependency
│   ├── dependencies/
│   │   └── auth.py              # Auth & admin role dependencies (get_current_user, require_admin)
│   ├── models/
│   │   ├── user.py              # User model (roles: user, admin)
│   │   ├── file.py              # File metadata & encryption key model
│   │   ├── file_share.py        # Permissions, quotas, expiration, and revocation model
│   │   └── activity_log.py      # Security audit log model
│   ├── routes/
│   │   ├── user_routes.py       # Registration, login, /me, admin user management
│   │   ├── file_routes.py       # Encrypted upload, download, list, delete, share, revoke
│   │   ├── admin_routes.py      # Security audit log exploration
│   │   └── dashboard_routes.py  # User & Admin analytics dashboards
│   ├── schemas/
│   │   ├── user.py              # Pydantic schemas for auth & users
│   │   ├── file.py              # Pydantic schemas for file responses
│   │   ├── share.py             # Pydantic schemas for sharing requests & responses
│   │   ├── activity.py          # Pydantic schemas for audit logs
│   │   └── dashboard.py         # Pydantic schemas for dashboards
│   ├── security/
│   │   ├── encryption.py        # Fernet AES-256 file encryption & decryption
│   │   ├── jwt_handler.py       # JWT creation and token validation
│   │   └── password.py          # Bcrypt password hashing & verification
│   ├── services/
│   │   ├── file_service.py      # File business logic & encryption orchestration
│   │   └── logging_service.py   # Centralized audit logging utility
│   └── main.py                  # FastAPI application entry point & router registration
├── tests/
│   ├── conftest.py              # SQLite in-memory fixtures & TestClient configuration
│   ├── test_auth.py             # Authentication & user lifecycle tests
│   ├── test_files.py            # Encrypted upload, download, and deletion tests
│   ├── test_sharing.py          # Permissions, limits, expiry, and revocation tests
│   └── test_admin.py            # Dashboard, admin role, and audit log tests
├── .env.example                 # Template for environment configuration
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Production & testing dependencies
└── README.md                    # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- MySQL Server (or MariaDB)

### 2. Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd secure-file-sharing-system
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/secure_file_sharing
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
```

### 4. Database Setup

Ensure your MySQL service is running and create the database:

```sql
CREATE DATABASE secure_file_sharing;
```

When you launch the application, SQLAlchemy will automatically create all tables (`users`, `files`, `file_shares`, `activity_logs`).

### 5. Running the Application

Start the development server with Uvicorn:

```bash
uvicorn app.main:app --reload
```

- **API Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`

---

## 📡 API Reference Summary

### Authentication & Users
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/register` | Public | Register a new user account |
| `POST` | `/login` | Public | Authenticate with credentials and receive a JWT token |
| `GET` | `/me` | Authenticated | Retrieve current user profile |
| `GET` | `/users` | Admin Only | List all registered users |
| `PUT` | `/users/{id}/deactivate` | Admin Only | Activate or deactivate a user account |

### Files & Encryption
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/upload` | Authenticated | Upload and AES-256 encrypt a file |
| `GET` | `/files` | Authenticated | List all files owned by current user |
| `GET` | `/files/{id}/download` | Owner / Shared | Decrypt and stream file payload |
| `DELETE` | `/files/{id}` | Owner Only | Delete file from disk and database |

### Sharing & Permissions
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/files/{id}/share` | Owner Only | Share file with email (permission, expiry, download limit) |
| `GET` | `/files/{id}/shares` | Owner Only | View all shares for a file |
| `DELETE` | `/files/{id}/share/{share_id}` | Owner Only | Revoke a file share |
| `GET` | `/shared-with-me` | Authenticated | View files shared with current user |

### Dashboards & Security Monitoring
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/dashboard` | Authenticated | User metrics (storage, counts, recent logs) |
| `GET` | `/admin/dashboard` | Admin Only | System-wide health & security summary |
| `GET` | `/admin/logs` | Admin Only | Full audit log stream |
| `GET` | `/admin/logs/failed-logins` | Admin Only | Filtered failed authentication logs |
| `GET` | `/admin/logs/unauthorized` | Admin Only | Filtered unauthorized access logs |

---

## 🧪 Running the Tests

The project includes unit and integration tests covering authentication, encryption, sharing limits, permissions, revocation, and admin privileges.

Run the test suite with pytest:

```bash
pytest
```

Or with verbose output:

```bash
pytest tests/ -v
```

> **Note**: Tests run against an isolated in-memory SQLite database (`sqlite:///:memory:`) using FastAPI's `TestClient`. No running MySQL instance or disk uploads are touched during testing.
