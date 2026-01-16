# COMSOC Repository System

A modern, fully functional, secured document repository management system built with Django, PostgreSQL, and Bootstrap 5.

## Features

### Authentication
- User registration (sign up)
- Login/logout functionality
- Password reset flow
- Secure password hashing with Django's built-in authentication
- Session security with HTTP-only cookies

### Authorization & Role Management
- Role-based access control (RBAC) with three default roles:
  - **Admin**: Full system access, can manage users and roles
  - **Manager**: Can manage documents and access most features
  - **User**: Basic document access
- Admin UI for assigning roles to users
- Role-based document access control

### Dashboard
- Landing page after login with summary metrics
- Document count statistics
- Recent uploads tracking
- Documents by classification breakdown
- Recent activity log (for admins/managers)

### Document Repository
- **Upload documents** with metadata (title, description, category, tags)
- **Document segregation** enforced server-side:
  - By classification (Public, Internal, Confidential, Restricted)
  - By owner
  - Shared documents support
- **Search and filter** documents by:
  - Title/filename
  - Tags/category
  - Owner
  - Date range
  - Classification level
- **View/download** documents with authorization checks
- **CRUD operations** for document metadata (subject to permissions)

### Reports
- **Document Inventory Report**: Filterable list of all accessible documents
- **Activity Report**: Audit log of user actions
- **CSV Export**: Both reports can be exported to CSV

### Security Features
- CSRF protection (Django built-in)
- Input validation on all forms
- Secure file upload handling:
  - File size validation (10MB limit)
  - File type validation (PDF, Word, Excel, Text, Images)
  - Protected media storage (not directly accessible)
- Audit logging for sensitive actions:
  - Login/logout
  - Registration
  - Password reset
  - Role changes
  - Document upload/view/download/update/delete
- **Security Patches Applied**: All dependencies updated to patched versions
  - Django 5.1.14 LTS (fixes SQL injection and DoS vulnerabilities)
  - Gunicorn 22.0.0 (fixes HTTP request smuggling)
  - Pillow 10.3.0 (fixes buffer overflow)

## Technology Stack

- **Backend**: Django 5.1.14 LTS
- **API**: Django REST Framework 3.14.0
- **Database**: PostgreSQL 16
- **Frontend**: Django Templates with Bootstrap 5
- **Forms**: django-crispy-forms with Bootstrap 5
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Docker and Docker Compose installed
- Git

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd repository-system
```

### 2. Environment Configuration

Copy the example environment file and customize if needed:

```bash
cp .env.example .env
```

Edit `.env` to set your configuration (optional for local development):

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=repository_db
DB_USER=repository_user
DB_PASSWORD=repository_pass
DB_HOST=db
DB_PORT=5432
```

### 3. Build and Start Services

Build and start the application using Docker Compose:

```bash
docker-compose up --build
```

This will:
- Start PostgreSQL database
- Build the Django application
- Run database migrations
- Collect static files
- Start the development server on http://localhost:8000

### 4. Initialize Roles and Create Superuser

In a new terminal, initialize the default roles:

```bash
docker-compose exec web python manage.py init_roles
```

Create a superuser account:

```bash
docker-compose exec web python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 5. Access the Application

- **Main Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Login Page**: http://localhost:8000/accounts/login/

## Running Tests

Run the test suite:

```bash
docker-compose exec web python manage.py test
```

Run specific test modules:

```bash
# Test authentication
docker-compose exec web python manage.py test accounts

# Test documents
docker-compose exec web python manage.py test documents
```

## Usage

### First Steps

1. **Register a new account** or login with the superuser account created earlier
2. **Assign roles** (Admin only):
   - Navigate to "Roles" in the navigation bar
   - Select a user and assign them a role (Admin, Manager, or User)
3. **Upload documents**:
   - Click "Upload" in the navigation bar
   - Fill in document details and select a file
   - Choose appropriate classification level
4. **Browse and search documents**:
   - Click "Documents" to view all accessible documents
   - Use filters to search by classification, category, owner, or date range

### User Roles & Permissions

#### Admin
- Full access to all documents
- Can manage user roles
- Can view all reports
- Can delete any document

#### Manager
- Access to all documents except Restricted
- Can view reports
- Can delete documents

#### User
- Access to own documents
- Access to documents shared with them
- Access to Public documents
- Can upload and manage own documents

### Document Classification Levels

- **Public**: Accessible by all authenticated users
- **Internal**: Accessible by owner, shared users, managers, and admins
- **Confidential**: Accessible by owner, shared users, and admins
- **Restricted**: Accessible only by owner and admins

## Project Structure

```
repository-system/
├── accounts/              # User authentication and role management
│   ├── models.py         # User, Role, AuditLog models
│   ├── views.py          # Authentication views
│   ├── forms.py          # Registration, login forms
│   ├── decorators.py     # Permission decorators
│   └── utils.py          # Audit logging utilities
├── documents/            # Document management
│   ├── models.py         # Document model
│   ├── views.py          # Document CRUD views
│   ├── forms.py          # Document upload/update forms
│   └── permissions.py    # Document access control
├── dashboard/            # Dashboard views
├── reports/              # Reporting functionality
├── templates/            # HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── dashboard/
│   ├── documents/
│   └── reports/
├── static/               # Static files (CSS, JS)
├── media/                # Uploaded documents
├── repository_project/   # Django project settings
│   ├── settings.py
│   └── urls.py
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker image definition
├── requirements.txt      # Python dependencies
└── manage.py             # Django management script
```

## Security Considerations

### Implemented Security Measures

1. **Authentication**: Django's robust authentication system with password hashing
2. **Session Security**: HTTP-only, SameSite cookies
3. **CSRF Protection**: Enabled by default on all forms
4. **Input Validation**: Form validation on all user inputs
5. **File Upload Security**:
   - File type validation
   - File size limits
   - Protected media storage
6. **SQL Injection Protection**: Django ORM parameterized queries
7. **XSS Protection**: Django template auto-escaping
8. **Audit Logging**: All sensitive actions are logged

### Production Deployment Recommendations

1. Set `DEBUG=False` in production
2. Use a strong `SECRET_KEY`
3. Enable HTTPS and set:
   - `SESSION_COOKIE_SECURE=True`
   - `CSRF_COOKIE_SECURE=True`
   - `SECURE_SSL_REDIRECT=True`
4. Use environment variables for sensitive data
5. Regular security updates for dependencies
6. Configure proper backup strategy for database and media files
7. Set up proper logging and monitoring
8. Use a production-grade WSGI server (already includes Gunicorn)
9. Configure a reverse proxy (Nginx/Apache)
10. Implement rate limiting

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Random string |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hostnames | `localhost,127.0.0.1` |
| `DB_NAME` | Database name | `repository_db` |
| `DB_USER` | Database user | `repository_user` |
| `DB_PASSWORD` | Database password | `repository_pass` |
| `DB_HOST` | Database host | `db` |
| `DB_PORT` | Database port | `5432` |
| `SESSION_COOKIE_SECURE` | Secure session cookies | `False` |
| `CSRF_COOKIE_SECURE` | Secure CSRF cookies | `False` |

## Troubleshooting

### Database Connection Issues

If you see database connection errors:

```bash
# Ensure database is healthy
docker-compose ps

# Restart services
docker-compose down
docker-compose up
```

### Migration Issues

If you need to reset migrations:

```bash
docker-compose exec web python manage.py migrate --fake accounts zero
docker-compose exec web python manage.py migrate
```

### Permission Denied on Media Files

Ensure proper permissions:

```bash
docker-compose exec web chmod -R 755 /app/media
```

## Development

### Making Changes

1. Make your code changes
2. Run tests: `docker-compose exec web python manage.py test`
3. Run migrations if models changed:
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```

### Adding Dependencies

1. Add package to `requirements.txt`
2. Rebuild the container:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

## License

This project is provided as-is for educational and demonstration purposes.

## Support

For issues, questions, or contributions, please open an issue in the repository.
