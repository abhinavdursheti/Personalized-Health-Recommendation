# Personalized Health Recommendation System

## 🎯 Project Goal

The Personalized Health Recommendation System is an intelligent web application that provides customized health recommendations for diet, exercise, and sleep routines based on individual user data. The system uses machine learning models to analyze user profiles, health metrics, lifestyle patterns, and preferences to generate personalized recommendations that adapt over time.

## ✨ Key Features

### 1. **User Profile Management**
   - User registration and authentication
   - Comprehensive health profile creation (age, weight, height, BMI, activity level)
   - Health goals setting (weight loss, muscle gain, maintenance, general wellness)
   - Medical conditions and dietary restrictions tracking

### 2. **Diet Recommendations**
   - Personalized meal plans based on:
     - Daily calorie requirements
     - Macronutrient distribution (proteins, carbs, fats)
     - Dietary preferences (vegetarian, vegan, keto, etc.)
     - Allergies and restrictions
   - Meal timing suggestions
   - Nutrient tracking and analysis

### 3. **Exercise Recommendations**
   - Customized workout plans based on:
     - Fitness level (beginner, intermediate, advanced)
     - Available equipment
     - Time availability
     - Health goals
   - Exercise intensity and duration suggestions
   - Progress tracking

### 4. **Sleep Recommendations**
   - Optimal sleep duration based on age and activity level
   - Sleep schedule suggestions
   - Sleep quality improvement tips
   - Bedtime routine recommendations

### 5. **Predictive Analytics**
   - ML models predict:
     - Weight progression trends
     - Health risk factors
     - Optimal calorie intake
     - Exercise effectiveness
   - Progress forecasting

### 6. **Dashboard & Analytics**
   - Interactive dashboard with health metrics visualization
   - Progress tracking over time
   - Recommendation history
   - Health insights and trends

### 7. **Behavior Recovery & Stability Prediction Engine** ⭐ NEW
   - Predicts recovery time from health setbacks
   - Analyzes behavior stability and consistency
   - Calculates adherence rates and streak tracking
   - Provides personalized recovery recommendations
   - Risk level assessment (Low/Medium/High)

### 8. **Behavior-Cause Correlation Engine (Root-Cause Analysis)** ⭐ NEW
   - Identifies correlations between behaviors and health outcomes
   - Root-cause analysis for weight changes
   - Correlation insights for sleep, exercise, and calories
   - Actionable recommendations based on patterns
   - Statistical correlation analysis

### 9. **Personalized Habit Sensitivity Analyzer** ⭐ NEW
   - Analyzes habit fragility vs resilience
   - Identifies which habits are easily broken vs well-established
   - Impact scoring for each habit
   - High-impact habit identification
   - Personalized recommendations for habit strengthening

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 4.2+ (Python web framework)
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **ML Libraries**: 
  - scikit-learn (Random Forest, SVM, Linear Regression)
  - pandas (data processing)
  - numpy (numerical computations)
- **API**: Django REST Framework

### Frontend
- **Framework**: HTML5, CSS3, JavaScript (Vanilla JS)
- **UI Library**: Bootstrap 5 (responsive design)
- **Charts**: Chart.js (data visualization)
- **Styling**: Modern CSS with gradients and animations

### ML Models
- **Diet Recommendation**: Random Forest Classifier + Linear Regression
- **Exercise Recommendation**: Decision Tree + Clustering
- **Sleep Recommendation**: Rule-based + Predictive Model
- **Recovery & Stability**: Random Forest Regressor + Gradient Boosting Classifier ⭐ NEW
- **Behavior Correlation**: Random Forest Regressor + Statistical Analysis ⭐ NEW
- **Habit Sensitivity**: Random Forest Classifier + Gradient Boosting Regressor ⭐ NEW

### Additional Tools
- **Data Processing**: pandas, numpy, scipy
- **Model Persistence**: joblib (save/load ML models)
- **Date Handling**: datetime, pytz
- **Statistical Analysis**: scipy (correlation analysis)

## 📁 Project Structure

```
health-recommendation-system/
├── manage.py
├── requirements.txt
├── README.md
├── health_app/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── recommendation/
│   ├── __init__.py
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── urls.py            # URL routing
│   ├── admin.py
│   ├── ml_models/         # ML model files
│   │   ├── diet_model.py
│   │   ├── exercise_model.py
│   │   └── sleep_model.py
│   ├── utils.py           # Helper functions
│   └── migrations/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── templates/
    ├── base.html
    ├── index.html
    ├── dashboard.html
    └── recommendations.html
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone/Navigate to project directory**
   ```bash
   cd "health cur"
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional, for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open browser: `http://127.0.0.1:8000/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

## 📊 How It Works

1. **User Registration**: Users create accounts and provide basic health information
2. **Profile Setup**: Users complete their health profile (metrics, goals, preferences)
3. **Data Collection**: System collects and stores user health data
4. **ML Processing**: Machine learning models analyze user data
5. **Recommendation Generation**: System generates personalized recommendations
6. **Dashboard Display**: Users view recommendations and track progress
7. **Continuous Learning**: System adapts recommendations based on user feedback and progress

## 🎨 Features in Detail

### Diet Recommendations
- Calculates BMR (Basal Metabolic Rate) and TDEE (Total Daily Energy Expenditure)
- Suggests meal plans with specific foods and portions
- Considers dietary restrictions and preferences
- Provides nutritional breakdown

### Exercise Recommendations
- Suggests workout routines based on fitness goals
- Includes exercise descriptions and instructions
- Adapts intensity based on user progress
- Tracks workout frequency and duration

### Sleep Recommendations
- Calculates optimal sleep duration
- Suggests bedtime and wake-up times
- Provides sleep hygiene tips
- Tracks sleep patterns

## 🆕 New Advanced Features

### Behavior Recovery & Stability Prediction
- **Recovery Time Prediction**: Predicts how many days it takes to recover from health setbacks
- **Stability Scoring**: Analyzes behavior stability (0-100%)
- **Consistency Tracking**: Measures data entry consistency
- **Streak Monitoring**: Tracks consecutive days of health tracking
- **Risk Assessment**: Identifies Low/Medium/High risk levels

### Behavior-Cause Correlation Engine
- **Root-Cause Analysis**: Identifies primary causes of health changes
- **Correlation Insights**: Shows relationships between behaviors and outcomes
- **Pattern Recognition**: Detects patterns in sleep, exercise, and diet
- **Actionable Insights**: Provides specific recommendations based on correlations

### Personalized Habit Sensitivity Analyzer
- **Fragility Analysis**: Identifies which habits are easily broken
- **Resilience Scoring**: Measures how well-established habits are
- **Impact Assessment**: Ranks habits by their health impact
- **Habit Strengthening**: Provides recommendations to strengthen fragile habits

## 🔮 Future Enhancements

- Integration with fitness trackers (Fitbit, Apple Health)
- Mobile app development
- Real-time health monitoring
- Community features and challenges
- Integration with nutrition databases
- Advanced ML models (Neural Networks, Deep Learning)
- Predictive health risk modeling

## 📝 License

This project is created for educational purposes as a final year project.

## 👨‍💻 Developer

Final Year Project - Personalized Health Recommendation System

