# New Advanced Features Documentation

## Overview

Three powerful new ML-powered analytics features have been added to the Personalized Health Recommendation System:

1. **Behavior Recovery & Stability Prediction Engine**
2. **Behavior-Cause Correlation Engine (Root-Cause Analysis)**
3. **Personalized Habit Sensitivity Analyzer**

---

## 1. Behavior Recovery & Stability Prediction Engine

### Purpose
Predicts how quickly users can recover from health setbacks and analyzes the stability of their health behaviors.

### Features
- **Recovery Time Prediction**: Uses ML to predict days needed to recover from setbacks (1-14 days)
- **Stability Scoring**: Calculates behavior stability score (0-100%)
- **Consistency Analysis**: Measures how consistent users are with data entry
- **Adherence Tracking**: Tracks how well users follow recommendations
- **Streak Monitoring**: Tracks consecutive days of health tracking
- **Risk Level Assessment**: Classifies users as Low/Medium/High risk

### ML Models Used
- **Random Forest Regressor**: For recovery time prediction
- **Gradient Boosting Classifier**: For stability classification

### Metrics Calculated
- Consistency Score (0-1)
- Adherence Rate (0-1)
- Streak Days
- Missed Days
- Recovery Days (predicted)

### Access
Navigate to: **Analytics** → **Behavior Recovery & Stability Prediction**

---

## 2. Behavior-Cause Correlation Engine

### Purpose
Identifies correlations between user behaviors and health outcomes to find root causes of health changes.

### Features
- **Root-Cause Identification**: Identifies primary causes of weight/health changes
- **Correlation Analysis**: Calculates correlation coefficients between behaviors and outcomes
- **Behavior Insights**: Provides insights for sleep, exercise, and calorie intake
- **Pattern Recognition**: Detects patterns in health data
- **Actionable Recommendations**: Suggests specific actions based on correlations

### ML Models Used
- **Random Forest Regressor**: For impact prediction
- **Statistical Correlation**: Pearson correlation analysis using scipy

### Insights Provided
- Sleep hours correlation with weight changes
- Exercise minutes correlation with outcomes
- Calorie intake correlation analysis
- Data consistency impact

### Access
Navigate to: **Analytics** → **Behavior-Cause Correlation Engine**

---

## 3. Personalized Habit Sensitivity Analyzer

### Purpose
Analyzes which health habits are fragile (easily broken) vs resilient (well-established) and their impact on health goals.

### Features
- **Fragility Analysis**: Identifies habits that are easily broken
- **Resilience Scoring**: Measures how well-established habits are
- **Impact Assessment**: Ranks habits by their health impact (0-100%)
- **Habit Categorization**: Classifies habits as fragile or resilient
- **High-Impact Identification**: Highlights habits with the most impact
- **Personalized Recommendations**: Provides specific advice for each habit

### ML Models Used
- **Random Forest Classifier**: For fragility prediction
- **Gradient Boosting Regressor**: For impact scoring

### Habits Analyzed
- **Diet Tracking**: Calorie and nutrition tracking habits
- **Exercise Routine**: Workout consistency and frequency
- **Sleep Schedule**: Sleep tracking and consistency

### Metrics for Each Habit
- Fragility Score (0-100%)
- Impact Score (0-100%)
- Frequency (% of days tracked)
- Duration (days since habit started)
- Consistency Score

### Access
Navigate to: **Analytics** → **Personalized Habit Sensitivity Analyzer**

---

## How to Use

### Prerequisites
- Complete your health profile
- Add at least 7-10 health data entries for accurate analysis

### Steps

1. **Navigate to Analytics Page**
   - Click "Analytics" in the navigation menu
   - Or go to: `/analytics/`

2. **Generate Analyses**
   - Click "Generate Analysis" buttons for each feature
   - Wait for ML models to process your data
   - View insights and recommendations

3. **Review Insights**
   - Recovery & Stability: Check your recovery time and stability score
   - Correlation Analysis: Review root causes and behavior insights
   - Habit Sensitivity: Identify fragile vs resilient habits

4. **Take Action**
   - Follow personalized recommendations
   - Focus on high-impact habits
   - Strengthen fragile habits
   - Address root causes identified

---

## Technical Details

### Data Requirements
- **Recovery & Stability**: Minimum 7 data points
- **Correlation Analysis**: Minimum 10 data points
- **Habit Sensitivity**: Minimum 7 data points

### Model Training
- Models are pre-trained with synthetic data
- Models can be retrained with real user data for better accuracy
- Model files are saved in `recommendation/ml_models/`

### Database Models
- `RecoveryStabilityAnalysis`: Stores recovery and stability predictions
- `BehaviorCorrelationAnalysis`: Stores correlation insights
- `HabitSensitivityAnalysis`: Stores habit sensitivity analysis

### API Endpoints
- `/api/generate-recovery-analysis/` - Generate recovery analysis
- `/api/generate-correlation-analysis/` - Generate correlation analysis
- `/api/generate-habit-analysis/` - Generate habit analysis

---

## Benefits

1. **Predictive Insights**: Know how quickly you'll recover from setbacks
2. **Root-Cause Understanding**: Understand why health changes occur
3. **Habit Optimization**: Focus on habits that matter most
4. **Personalized Guidance**: Get specific recommendations for your situation
5. **Data-Driven Decisions**: Make informed choices based on ML analysis

---

## Example Insights

### Recovery & Stability
- "You typically recover from setbacks in 4.2 days"
- "Your behavior stability is 72% (Low Risk)"
- "Maintain your current routine and track progress"

### Correlation Analysis
- "When you sleep less than 7 hours, your weight increases"
- "Regular exercise is a key factor in your weight management"
- "Calorie intake is a primary driver of weight changes"

### Habit Sensitivity
- "Diet Tracking: Fragile (65%) - Increase frequency"
- "Exercise Routine: Resilient (35%) - Well-established"
- "Sleep Schedule: High Impact (85%) - Focus area"

---

## Future Enhancements

- Real-time habit tracking
- Predictive health risk modeling
- Integration with wearable devices
- Advanced neural network models
- Multi-user comparison and benchmarking


