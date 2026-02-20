# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Setup Database
```bash
python manage.py migrate
```

### Step 3: Run Server
```bash
python manage.py runserver
```

Then open **http://127.0.0.1:8000/** in your browser!

---

## 📝 First Time User Flow

1. **Register** → Create account at `/register/`
2. **Setup Profile** → Complete health profile (required for recommendations)
3. **Generate Recommendations** → Go to Recommendations page and click "Generate"
4. **Track Progress** → Add daily health data on Dashboard

---

## 🎯 Key Features to Explore

- ✅ **Dashboard** - View your health metrics and progress
- ✅ **Diet Recommendations** - Get personalized meal plans
- ✅ **Exercise Recommendations** - Get customized workout plans  
- ✅ **Sleep Recommendations** - Get optimal sleep schedules
- ✅ **Health Tracking** - Log daily weight, sleep, exercise, calories
- ✅ **Progress Charts** - Visualize your health trends

---

## 🔧 Common Commands

```bash
# Create superuser (for admin access)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

---

## 📚 Documentation Files

- **README.md** - Full project documentation
- **SETUP.md** - Detailed setup instructions
- **PROJECT_SUMMARY.md** - Complete project overview
- **QUICK_START.md** - This file

---

## ⚠️ Troubleshooting

**Problem**: Module not found
**Solution**: `pip install -r requirements.txt`

**Problem**: Database errors
**Solution**: `python manage.py migrate`

**Problem**: Can't access admin
**Solution**: Create superuser with `python manage.py createsuperuser`

---

## 🎓 For Final Year Project

This project includes:
- ✅ Complete documentation
- ✅ ML models implementation
- ✅ Modern web interface
- ✅ Database models
- ✅ API endpoints
- ✅ User authentication
- ✅ Data visualization

**Ready for submission!** 🎉


