# AI Synthetic Workforce - Backend

Django REST API backend for the AI Synthetic Workforce application.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

### 1. Create Virtual Environment

```bash
# Navigate to Backend directory
cd Backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the `Backend/` directory with the following variables:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### 4. Database Setup

```bash
cd workforce_backend

# Run migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

Server will be available at: `http://localhost:8000`

Admin panel: `http://localhost:8000/admin`

## Project Structure

```
Backend/
├── workforce_backend/          # Django project
│   ├── manage.py              # Django management script
│   ├── app/                   # Main Django app
│   │   ├── models.py          # Database models
│   │   ├── views.py           # API views
│   │   ├── admin.py           # Admin configuration
│   │   └── migrations/        # Database migrations
│   ├── workforce_backend/
│   │   ├── settings.py        # Project settings
│   │   ├── urls.py            # URL routing
│   │   ├── wsgi.py            # WSGI configuration
│   │   └── asgi.py            # ASGI configuration
│   └── db.sqlite3             # SQLite database
└── requirements.txt           # Python dependencies
```

## Common Commands

### Create New App
```bash
python manage.py startapp app_name
```

### Make Migrations
```bash
python manage.py makemigrations
```

### Apply Migrations
```bash
python manage.py migrate
```

### Run Tests
```bash
python manage.py test
```

### Collect Static Files (Production)
```bash
python manage.py collectstatic
```

## API Documentation

- Base URL: `http://localhost:8000/api/`
- Admin: `http://localhost:8000/admin/`

## Troubleshooting

### Virtual Environment Issues
- Make sure virtual environment is activated before running commands
- Reinstall dependencies if you encounter import errors

### Database Issues
- Delete `db.sqlite3` and run `python manage.py migrate` again to reset the database
- Check migrations folder for conflicts

### Port Already in Use
```bash
python manage.py runserver 8001
```

## Contributing

- Follow PEP 8 style guide
- Create migrations for database changes
- Test before pushing to repository

## License

This project is part of AI Synthetic Workforce
