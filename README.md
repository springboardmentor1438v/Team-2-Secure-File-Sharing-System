<<<<<<< HEAD
Secure File Sharing System

Infosys Springboard Internship Project – 8 Weeks

A secure web-based file sharing and management system developed as part of the Infosys Springboard Internship.

Project Description

Secure File Sharing System (SecureFS) is a web-based application designed to securely upload, store, organize, manage and share files between registered users.

The system provides authenticated access to users and allows them to manage their own files and folders. Users can share files with other registered users with controlled permissions such as View and Download.

The system also provides administrative features through an Admin Dashboard, where administrators can manage users, change user roles, monitor all files and view activity logs.

The backend is developed using FastAPI and the application data is stored in MySQL using SQLAlchemy.

Objectives

Provide secure user authentication.

Protect user passwords using password hashing.

Provide JWT-based authentication for protected APIs.

Allow users to upload and manage files.

Organize files using folders.

Allow users to share files with other registered users.

Provide controlled sharing permissions.

Support file expiry dates and download limits.

Maintain activity logs for important system operations.

Provide an Admin Dashboard for system administration.

Provide user and role management.

Provide centralized monitoring of files and activities.

Tech Stack

Backend

Python 3.10

FastAPI

Uvicorn

SQLAlchemy

PyMySQL

Python-dotenv

Database

MySQL 8.0

MySQL Workbench

Authentication and Security

JWT Authentication

OAuth2 Password Authentication

Password Hashing using bcrypt

Role-Based Access Control

Protected API endpoints

Frontend

HTML5

CSS3

JavaScript

Bootstrap

Font Awesome

Google Fonts

System Architecture

The application follows a client-server architecture.

                    USER / ADMIN
                         |
                         ↓
              FRONTEND APPLICATION
             HTML + CSS + JavaScript
                         |
                         ↓
                  REST API REQUEST
                         |
                         ↓
              FASTAPI BACKEND
                         |
          +--------------+--------------+
          |                             |
          ↓                             ↓
   AUTHENTICATION                 AUTHORIZATION
   JWT + OAuth2                   USER / ADMIN
   Password Hashing               Permission Checks
          |                             |
          +--------------+--------------+
                         |
                         ↓
                 APPLICATION ROUTES
                         |
       +-----------------+------------------+
       |                 |                  |
       ↓                 ↓                  ↓
     Users             Files             Folders
       |                 |                  |
       ↓                 ↓                  ↓
    Sharing         File Versions       Ownership
       |
       ↓
                ACTIVITY LOGGING
                         |
                         ↓
                  MYSQL DATABASE

Project Structure

secure-file-sharing-system/
│
├── app/
│   ├── config/
│   ├── database/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── security/
│   ├── services/
│   ├── utils/
│   └── main.py
│
├── frontend/
│   ├── assets/
│   ├── css/
│   ├── js/
│   └── pages/
│
├── tests/
├── uploads/
├── .env
├── .gitignore
├── requirements.txt
└── README.md

Features

1. User Registration

New users can create an account using username, email and password.

The system checks whether the username or email already exists before creating the account.

2. User Login

Registered users can log in using their email and password.

During login:

The user submits email and password.

The backend searches for the user.

The password is verified against the stored password hash.

A JWT access token is generated after successful authentication.

The token is returned to the frontend.

3. Password Hashing

Passwords are never stored directly as plain text.

User Password
      ↓
Password Hashing
      ↓
Secure Password Hash
      ↓
MySQL Database

4. JWT Authentication

JWT is used to protect authenticated API endpoints.

Email + Password
       ↓
Authentication
       ↓
JWT Access Token
       ↓
Frontend
       ↓
Protected API Request

The token is sent using:

Authorization: Bearer <access_token>

5. User Profile

Authenticated users can access:

User ID

Username

Email

Role

Example:

{
    "id": 2,
    "username": "venu",
    "email": "venu@gmail.com",
    "role": "ADMIN"
}

File Management

6. File Upload

Authenticated users can upload files to the system.

Select Folder
      ↓
Select File
      ↓
Upload Request
      ↓
FastAPI Backend
      ↓
File Storage
      ↓
Database Record

7. My Files

Users can view files that belong to them.

Operations include:

Download

Rename

Delete

Share

View Versions

8. File Download

Authenticated users can download files through protected API endpoints.

9. File Rename

Users can rename their files through the application.

10. File Delete

Users can delete their files after confirmation. The backend verifies ownership before deletion.

Folder Management

11. Folder Creation

Users can create folders to organize their files.

My Files
│
├── Documents
├── Projects
├── Images
└── Reports

12. Folder Rename

Users can rename their own folders. The backend checks folder ownership before updating the folder name.

13. Folder Delete

Users can delete folders. A folder cannot be deleted if files are still present inside it.

File Sharing

14. Share Files

Users can share their files with other registered users.

The sender selects:

File

Recipient

Permission

Expiry date

Download limit

15. Sharing Permissions

SecureFS supports controlled permissions such as:

VIEW - The recipient can access the shared file according to the application's view permission.

DOWNLOAD - The recipient is allowed to download the shared file.

16. Share Expiry

A file share can have an expiry date. After the expiry period, the shared access can no longer be used according to the application's sharing rules.

17. Download Limit

The sender can specify a download limit.

Download Limit = 5

The application also supports:

Download Limit = 0

for unlimited downloads where configured.

18. Shared With Me

Users can view files that other users have shared with them.

19. My Shared Files

Users can view and manage files that they have shared with other users.

Management includes:

Permission

Expiry date

Download limit

File Version Management

20. File Versions

SecureFS maintains information about different versions of files.

Version information includes:

Version number

Stored filename

Upload date/time

Activity Logging

21. Activity Logs

The system records important activities performed within the application.

Examples include:

User registration

Successful login

Failed login

File operations

File sharing

Role changes

Unauthorized access attempts

Activity information can include:

User

Action

Resource type

Resource ID

Description

Status

Timestamp

Example:

LOGIN_SUCCESS
ROLE_CHANGED
USER_REGISTERED
LOGIN_FAILED
UNAUTHORIZED_ACCESS

Admin Dashboard

22. Admin Dashboard

SecureFS provides a separate dashboard for administrators.

Admin Dashboard
│
├── Dashboard
├── My Files
├── Upload
├── Folders
├── Shared With Me
├── My Shared Files
│
├── All Files
├── User Management
├── Activity Logs
│
└── Logout

User Management

23. User Management

Administrators can view registered users.

The administrator can:

View users

View user details

Change user roles

Delete users according to the implemented administrative controls

24. Role Management

The system supports two main roles:

USER
ADMIN

Administrators can change another user's role.

The backend verifies administrator privileges before allowing role changes.

An administrator cannot change their own role through the implemented role-change operation.

All Files

25. Admin All Files

Administrators can view files across the system.

The All Files section provides:

File ID

Filename

Owner

Upload date

Administrators can also perform administrative file operations according to the implemented permissions.

Security

26. Security Features

SecureFS uses multiple security mechanisms.

Password Hashing

JWT Authentication

OAuth2 Password Authentication

Role-Based Access Control

Protected Routes

Ownership Validation

Activity Logging

API Architecture

The backend is organized using FastAPI routers.

User Routes
      ↓
Authentication / Profile

File Routes
      ↓
Upload / Download / Rename / Delete / Versions

Folder Routes
      ↓
Create / List / Rename / Delete

Share Routes
      ↓
Share / Manage Shared Files

Activity Routes
      ↓
Activity Logs

Dashboard Routes
      ↓
Admin Operations

Password Routes
      ↓
Password-related Operations

Important API Endpoints

Authentication

Method

Endpoint

Description

POST

/register

Register a new user

POST

/login

Login and generate JWT

GET

/profile

Get current user profile

General

Method

Endpoint

Description

GET

/

Welcome message

GET

/health

Health check

Files

Method

Endpoint

Description

GET

/files

Get user's files

POST

/upload

Upload a file

GET

/download/{id}

Download a file

PUT

/rename/{id}

Rename a file

DELETE

/delete/{id}

Delete a file

GET

/versions/{id}

Get file versions

Folders

Method

Endpoint

Description

POST

/folders

Create folder

GET

/folders

Get user's folders

PUT

/folders/{id}

Rename folder

DELETE

/folders/{id}

Delete folder

Sharing

Method

Endpoint

Description

POST

/share

Share a file

GET

/my-shares

Get files shared by the user

GET

/shared

Get files shared with the user

Dashboard

Method

Endpoint

Description

GET

/dashboard/all-users

Get all users

GET

/dashboard/all-files

Get all files

PUT

/dashboard/change-role/{user_id}

Change user role

DELETE

/dashboard/delete-file/{file_id}

Delete file administratively

Database

SecureFS uses MySQL 8.0 as the application database.

SQLAlchemy is used as the ORM for database operations.

Main entities include:

User
File
Folder
Share
ActivityLog
File Version

Relationships include:

User
 │
 ├── Files
 ├── Folders
 ├── Shares
 └── Activity Logs

File
 │
 ├── Folder
 ├── Shares
 └── Versions

Environment Configuration

Database configuration is stored in the .env file.

Example:

DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=********
DB_NAME=secure_file_sharing

The actual .env file should never be uploaded to GitHub.

It is included in .gitignore.

.gitignore

venv/
.env
__pycache__/
*.pyc
.vscode/
security/key.key
uploads/

Setup Instructions

1. Clone the Repository

git clone <repository-url>
cd secure-file-sharing-system

2. Create Virtual Environment

python -m venv venv

3. Activate Virtual Environment

Windows PowerShell

.env\Scripts\Activate.ps1

4. Install Dependencies

pip install -r requirements.txt

5. Configure MySQL

Create the database:

CREATE DATABASE secure_file_sharing;

Configure .env:

DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=secure_file_sharing

6. Start the Backend

uvicorn app.main:app --reload

Application URL:

http://127.0.0.1:8000

Swagger API Documentation

FastAPI automatically provides interactive API documentation.

Open:

http://127.0.0.1:8000/docs

Swagger can be used to:

View available APIs

Test endpoints

Provide authentication credentials

Send requests

View responses

Debug backend APIs

Development Progress

Week 1 – Project Setup

Completed:

Project folder structure

FastAPI backend setup

Virtual environment

Basic API structure

Welcome API

Health Check API

Swagger UI

MySQL installation

MySQL Workbench setup

SQLAlchemy configuration

Database connectivity

.env configuration

Week 2 – Authentication

Completed:

User registration

User login

Password hashing using bcrypt

Password verification

JWT token generation

JWT verification

OAuth2 authentication

Protected /profile API

User roles

Week 3 – File Management

Completed:

File upload

File listing

File download

File rename

File deletion

File ownership

File metadata storage

Week 4 – Folder Management

Completed:

Folder creation

Folder listing

Folder rename

Folder deletion

Folder ownership

Preventing deletion of non-empty folders

Week 5 – File Sharing

Completed:

Share files with users

Select recipient

VIEW permission

DOWNLOAD permission

Expiry date

Download limit

Shared With Me

My Shared Files

Week 6 – File Versions and Activity Logs

Completed:

File version information

Version listing

Activity logging

Successful action logs

Failed action logs

Unauthorized access logs

Week 7 – Admin Dashboard

Completed:

Admin Dashboard

Admin authentication

User Management

Role management

All Files

Administrative file deletion

Activity Logs

Admin-only route protection

Week 8 – Frontend Integration and Testing

Completed:

Frontend page integration

Dashboard integration

Login page

Registration page

My Files page

Upload page

Folders page

Shared With Me page

My Shared Files page

Admin Dashboard

User Management page

Activity Logs page

Responsive UI improvements

API integration testing

Authentication testing

Authorization testing

Error handling

Testing

Authentication Testing

Valid login

Invalid email

Invalid password

Missing token

Invalid token

Authorization Testing

USER accessing ADMIN operations

ADMIN accessing administrative operations

Role changes

Ownership checks

File Testing

Upload

Download

Rename

Delete

File listing

Folder Testing

Create

Rename

Delete

Empty-folder validation

Sharing Testing

Share file

Invalid recipient

Permission selection

Expiry date

Download limit

Admin Testing

User Management

Role changes

All Files

Administrative deletion

Activity Logs

Current Storage Architecture

During development, uploaded files are currently stored using the project's local storage.

User
 ↓
Frontend
 ↓
FastAPI
 ↓
Local File Storage

MySQL stores the application's structured metadata.

For production deployment, the storage layer can be replaced or extended with cloud object storage such as Amazon S3, Google Cloud Storage or Azure Blob Storage.

Future Scope

Cloud object storage integration

Production deployment

HTTPS configuration

Email notifications

Password reset through email

File preview

Advanced search

File type validation

File size restrictions

Antivirus scanning

Encryption at rest

Multi-factor authentication

Improved audit reporting

Storage quota management

Automated backups

Database backup and recovery

Docker containerization

Advantages

Centralized file management

Secure authentication

Password hashing

JWT-based API protection

Role-based access control

Controlled file sharing

Folder organization

File version information

Download restrictions

Expiry-based sharing

Activity monitoring

Dedicated Admin Dashboard

REST API architecture

Interactive Swagger documentation

Limitations

File storage is currently local during development.

Production cloud storage has not yet been integrated.

HTTPS/production deployment configuration is not part of the current local development setup.

Advanced enterprise features such as MFA, antivirus scanning and automated backups are future enhancements.

Project Status

Current Status: Completed Development Version

✓ Authentication
✓ JWT Security
✓ Password Hashing
✓ User Profiles
✓ USER / ADMIN Roles
✓ File Upload
✓ File Download
✓ File Rename
✓ File Delete
✓ Folder Management
✓ File Sharing
✓ Sharing Permissions
✓ Expiry Dates
✓ Download Limits
✓ Shared With Me
✓ My Shared Files
✓ File Versions
✓ Activity Logs
✓ Admin Dashboard
✓ User Management
✓ Role Management
✓ All Files
✓ Protected APIs
✓ MySQL Database
✓ Frontend Integration
✓ Swagger Documentation

Conclusion

SecureFS provides a centralized platform for managing and sharing files between authenticated users.

The project combines a FastAPI backend, MySQL database, JWT authentication, password hashing and role-based authorization with a web-based frontend.

The system goes beyond basic file upload and download by providing folders, controlled file sharing, permissions, expiry dates, download limits, file versions, activity logs and administrative management.

The current version demonstrates the core requirements of a secure file-sharing application and provides a foundation for future cloud deployment and additional security enhancements.

Team

TEAM 2

Infosys Springboard Internship Project

Project: Secure File Sharing System

Duration: 8 Weeks

Technology: Python + FastAPI + MySQL + HTML/CSS/JavaScript
=======
# Team-2-Secure-File-Sharing-System
>>>>>>> ebe339e96cce524147f060ae52ba30293e6f52ae
