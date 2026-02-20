# Setup Instructions

## Quick Start Guide

### Step 1: Install Python
Make sure you have Python 3.8 or higher installed. Check by running:
```bash
python --version
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Optional)
```bash
python manage.py createsuperuser
```
This allows you to access the Django admin panel at `/admin/`

### Step 6: Run Development Server
```bash
python manage.py runserver
```

### Step 7: Access the Application
Open your browser and navigate to:
- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## First Time Setup

1. **Register a new account** at http://127.0.0.1:8000/register/
2. **Complete your health profile** - This is required to generate recommendations
3. **Generate recommendations** - Go to the Recommendations page and click "Generate" for each type
4. **Add health data** - Track your daily weight, sleep, exercise, and calories on the Dashboard

## Troubleshooting

### Issue: "django-admin not found"
- Make sure Django is installed: `pip install Django`
- Make sure your virtual environment is activated

### Issue: "ModuleNotFoundError"
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Make sure your virtual environment is activated

### Issue: "Database errors"
- Run migrations: `python manage.py migrate`
- If issues persist, delete `db.sqlite3` and run migrations again

### Issue: "Static files not loading"
- Collect static files: `python manage.py collectstatic`
- Make sure `STATIC_URL` and `STATICFILES_DIRS` are configured in settings.py

## Project Structure Overview

- `health_app/` - Main Django project configuration
- `recommendation/` - Main application with models, views, and ML models
- `templates/` - HTML templates for frontend
- `static/` - CSS, JavaScript, and images (if needed)
- `manage.py` - Django management script

## ML Models Location

The ML models are stored in:
- `recommendation/ml_models/diet_model.py`
- `recommendation/ml_models/exercise_model.py`
- `recommendation/ml_models/sleep_model.py`

Trained model files (`.pkl`) will be automatically created in `recommendation/ml_models/` when first used.

## Features to Test

1. **User Registration & Login**
2. **Profile Setup** - Enter health information
3. **Generate Recommendations** - Diet, Exercise, Sleep
4. **Add Health Data** - Track daily metrics
5. **View Dashboard** - See stats and progress
6. **View Progress Charts** - Visualize health trends

## Production Deployment Notes

For production deployment:
1. Set `DEBUG = False` in `settings.py`
2. Change `SECRET_KEY` to a secure random value
3. Use PostgreSQL instead of SQLite
4. Set up proper static file serving
5. Configure ALLOWED_HOSTS
6. Use environment variables for sensitive data
7. Set up HTTPS/SSL


