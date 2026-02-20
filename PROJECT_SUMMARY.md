# Personalized Health Recommendation System - Project Summary

## 🎯 Project Overview

This is a **complete web-based Personalized Health Recommendation System** built with Django and Machine Learning. The system provides AI-powered personalized recommendations for diet, exercise, and sleep based on individual user profiles and health data.

## 📋 Project Details

### Goal
To create an intelligent health recommendation platform that analyzes user health data and generates personalized diet plans, exercise routines, and sleep schedules using machine learning models.

### Key Features Implemented

1. **User Management**
   - User registration and authentication
   - Secure login/logout system
   - User profile management

2. **Health Profile System**
   - Comprehensive health data collection (age, weight, height, BMI)
   - Activity level tracking
   - Health goals setting (weight loss, muscle gain, maintenance, wellness)
   - Dietary preferences and restrictions
   - Medical conditions tracking

3. **Diet Recommendations (ML-Powered)**
   - Calculates BMR (Basal Metabolic Rate) and TDEE (Total Daily Energy Expenditure)
   - Predicts optimal daily calorie intake using Random Forest Regressor
   - Generates macronutrient distribution (proteins, carbs, fats)
   - Creates personalized meal plans based on dietary preferences
   - Considers allergies and restrictions

4. **Exercise Recommendations (ML-Powered)**
   - Determines fitness level (beginner, intermediate, advanced)
   - Uses Decision Tree Classifier for exercise type selection
   - Generates customized workout plans
   - Adapts to user's available time and goals
   - Provides exercise frequency recommendations

5. **Sleep Recommendations (ML-Powered)**
   - Predicts optimal sleep duration using Linear Regression
   - Calculates optimal bedtime and wake-up times
   - Provides sleep schedule based on sleep cycles
   - Offers personalized sleep hygiene tips

6. **Health Data Tracking**
   - Daily weight tracking
   - Sleep hours logging
   - Exercise minutes recording
   - Calories consumed tracking
   - Progress visualization with charts

7. **Dashboard & Analytics**
   - Real-time health metrics display (BMI, BMR, TDEE)
   - Progress charts (weight trends, sleep trends)
   - Recent health data table
   - Active recommendations display

## 🛠️ Technology Stack

### Backend
- **Django 4.2.7** - Web framework
- **Django REST Framework** - API development
- **SQLite** - Database (development)

### Machine Learning
- **scikit-learn 1.3.2** - ML algorithms
  - Random Forest Regressor (Diet)
  - Decision Tree Classifier (Exercise)
  - Linear Regression (Sleep)
- **pandas 2.1.3** - Data processing
- **numpy 1.24.3** - Numerical computations
- **joblib 1.3.2** - Model persistence

### Frontend
- **HTML5, CSS3, JavaScript** - Core web technologies
- **Bootstrap 5.3.0** - Responsive UI framework
- **Bootstrap Icons** - Icon library
- **Chart.js 4.4.0** - Data visualization

## 📁 Project Structure

```
health-recommendation-system/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── SETUP.md                  # Setup instructions
├── PROJECT_SUMMARY.md        # This file
├── start.bat                 # Windows startup script
├── .gitignore               # Git ignore rules
│
├── health_app/              # Main Django project
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py              # WSGI config
│   └── asgi.py              # ASGI config
│
├── recommendation/          # Main application
│   ├── __init__.py
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── urls.py              # App URL routing
│   ├── admin.py             # Admin configuration
│   ├── utils.py             # Helper functions
│   ├── migrations/          # Database migrations
│   └── ml_models/           # ML model implementations
│       ├── diet_model.py
│       ├── exercise_model.py
│       └── sleep_model.py
│
└── templates/               # HTML templates
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── setup_profile.html
    ├── dashboard.html
    └── recommendations.html
```

## 🚀 How to Run

### Quick Start (Windows)
1. Double-click `start.bat`
2. Open http://127.0.0.1:8000/ in browser

### Manual Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run migrations: `python manage.py migrate`
3. Start server: `python manage.py runserver`
4. Access: http://127.0.0.1:8000/

## 📊 ML Models Details

### Diet Model
- **Algorithm**: Random Forest Regressor
- **Input Features**: Age, weight, height, activity level, gender, health goal
- **Output**: Optimal daily calorie intake
- **Additional**: Macronutrient distribution calculation, meal plan generation

### Exercise Model
- **Algorithm**: Decision Tree Classifier
- **Input Features**: Fitness level, goal, available time, age, BMI
- **Output**: Exercise type and recommendations
- **Additional**: Workout frequency, exercise selection

### Sleep Model
- **Algorithm**: Linear Regression
- **Input Features**: Age, activity level, BMI, exercise minutes
- **Output**: Optimal sleep duration
- **Additional**: Sleep schedule calculation, sleep tips

## 🎨 UI Features

- **Modern Gradient Design** - Beautiful color schemes
- **Responsive Layout** - Works on all devices
- **Interactive Charts** - Progress visualization
- **Real-time Updates** - AJAX-based data submission
- **User-friendly Forms** - Easy data entry
- **Card-based Layout** - Clean and organized

## 📈 Future Enhancements

Potential improvements for the project:
- Integration with fitness trackers (Fitbit, Apple Health)
- Mobile app development (React Native/Flutter)
- Advanced ML models (Neural Networks)
- Real-time health monitoring
- Community features
- Nutrition database integration
- Email notifications
- Export reports (PDF)

## ✅ Project Completion Status

- ✅ User authentication system
- ✅ Health profile management
- ✅ ML models implementation
- ✅ Diet recommendations
- ✅ Exercise recommendations
- ✅ Sleep recommendations
- ✅ Health data tracking
- ✅ Dashboard with analytics
- ✅ Progress visualization
- ✅ Modern UI/UX
- ✅ API endpoints
- ✅ Documentation

## 📝 Notes

- The ML models are trained with synthetic data initially
- Models can be retrained with real user data for better accuracy
- Database uses SQLite for development (can be upgraded to PostgreSQL)
- All sensitive data should use environment variables in production
- Static files are served via Django (use CDN/nginx in production)

## 👨‍💻 Development

This project is ready for:
- Final year project submission
- Further development and enhancement
- Production deployment (with proper security measures)
- Integration with additional features

---

**Project Status**: ✅ Complete and Ready to Use


