import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

# Recovery Template Content
recovery_content = """{% extends 'base.html' %}

{% block title %}Recovery & Stability Analysis - Health Recommendation System{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-md-12">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="{% url 'analytics' %}">Analytics</a></li>
                <li class="breadcrumb-item active" aria-current="page">Recovery & Stability</li>
            </ol>
        </nav>
        <h2 class="text-white">
            <i class="bi bi-arrow-clockwise"></i> Recovery & Stability Prediction
        </h2>
        <p class="text-white-50">Predicts how quickly you recover from setbacks and analyzes behavior consistency</p>
    </div>
</div>

<div class="row">
    <div class="col-md-12 mb-4">
        <div class="card shadow">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h5 class="card-title mb-0">Analysis Results</h5>
                    <form method="post" action="{% url 'analytics_recovery' %}">
                        {% csrf_token %}
                        {% if not has_sufficient_data %}
                        <button type="submit" class="btn btn-primary" disabled>
                            <i class="bi bi-magic"></i> Generate Analysis
                        </button>
                        {% else %}
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-magic"></i> Generate Analysis
                        </button>
                        {% endif %}
                    </form>
                </div>

                {% if not has_sufficient_data %}
                    <div class="alert alert-warning">
                        <i class="bi bi-info-circle"></i> 
                        Insufficient data. Add more health entries to generate this analysis.
                    </div>
                {% endif %}

                {% if recovery_analysis %}
                    <div id="results" class="fade-in">
                        <div class="row mb-4">
                            <div class="col-md-3 mb-3">
                                <div class="stat-card h-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                                    <h3>{{ recovery_analysis.recovery_days|floatformat:1 }}</h3>
                                    <p>Recovery Days</p>
                                    <small>Est. days to bounce back</small>
                                </div>
                            </div>
                            <div class="col-md-3 mb-3">
                                <div class="stat-card h-100" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                                    <h3>{{ recovery_analysis.stability_score|floatformat:1 }}%</h3>
                                    <p>Stability Score</p>
                                    <small>Behavior consistency</small>
                                </div>
                            </div>
                            <div class="col-md-3 mb-3">
                                <div class="stat-card h-100" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                                    <h3>{{ recovery_analysis.consistency_score|floatformat:2 }}</h3>
                                    <p>Consistency</p>
                                    <small>Data tracking score</small>
                                </div>
                            </div>
                            <div class="col-md-3 mb-3">
                                <div class="stat-card h-100" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                                    <h3>{{ recovery_analysis.streak_days }}</h3>
                                    <p>Current Streak</p>
                                    <small>Days in a row</small>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card bg-light border-0 mb-4">
                            <div class="card-body">
                                <h5 class="card-title">Risk Assessment</h5>
                                <div class="d-flex align-items-center mb-2">
                                    <span class="me-2">Current Risk Level:</span>
                                    <span class="badge rounded-pill px-3 py-2 fs-6 {% if recovery_analysis.risk_level == 'Low' %}bg-success{% elif recovery_analysis.risk_level == 'Medium' %}bg-warning{% else %}bg-danger{% endif %}">
                                        {{ recovery_analysis.risk_level }}
                                    </span>
                                </div>
                                <p class="text-muted small mb-0">Based on your recent consistency and stability metrics.</p>
                            </div>
                        </div>

                        <h5 class="mb-3"><i class="bi bi-lightbulb"></i> Recommendations</h5>
                        <ul class="list-group list-group-flush border rounded">
                            {% for rec in recovery_analysis.recommendations %}
                            <li class="list-group-item d-flex align-items-start">
                                <i class="bi bi-check-circle-fill text-success me-3 mt-1"></i>
                                <span>{{ rec }}</span>
                            </li>
                            {% endfor %}
                        </ul>
                    </div>
                {% else %}
                    {% if has_sufficient_data %}
                    <div class="text-center py-5">
                        <i class="bi bi-arrow-clockwise text-muted" style="font-size: 4rem;"></i>
                        <h4 class="mt-3 text-muted">No analysis generated yet</h4>
                        <p class="text-muted">Click "Generate Analysis" to see your recovery prediction.</p>
                    </div>
                    {% endif %}
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# Correlation Template Content
correlation_content = """{% extends 'base.html' %}

{% block title %}Correlation Analysis - Health Recommendation System{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-md-12">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="{% url 'analytics' %}">Analytics</a></li>
                <li class="breadcrumb-item active" aria-current="page">Correlation</li>
            </ol>
        </nav>
        <h2 class="text-white">
            <i class="bi bi-diagram-3"></i> Behavior-Cause Correlation
        </h2>
        <p class="text-white-50">Identifies patterns and correlations (Root-Cause Analysis)</p>
    </div>
</div>

<div class="row">
    <div class="col-md-12 mb-4">
        <div class="card shadow">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h5 class="card-title mb-0">Correlation Engine Results</h5>
                    <form method="post" action="{% url 'analytics_correlation' %}">
                        {% csrf_token %}
                        {% if not has_sufficient_data %}
                        <button type="submit" class="btn btn-success" disabled>
                            <i class="bi bi-magic"></i> Run Analysis
                        </button>
                        {% else %}
                        <button type="submit" class="btn btn-success">
                            <i class="bi bi-magic"></i> Run Analysis
                        </button>
                        {% endif %}
                    </form>
                </div>

                {% if not has_sufficient_data %}
                    <div class="alert alert-warning">
                        <i class="bi bi-info-circle"></i> 
                        Insufficient data. Add more health entries to generate this analysis.
                    </div>
                {% endif %}

                {% if correlation_analysis %}
                    <div id="results" class="fade-in">
                        <h6 class="text-uppercase text-muted fw-bold mb-3">Root Causes Identified</h6>
                        <div class="row mb-4">
                            {% for cause in correlation_analysis.root_causes %}
                            <div class="col-md-4 mb-3">
                                <div class="card border-warning h-100 bg-warning bg-opacity-10">
                                    <div class="card-body d-flex align-items-center">
                                        <i class="bi bi-exclamation-triangle-fill text-warning fs-3 me-3"></i>
                                        <strong>{{ cause }}</strong>
                                    </div>
                                </div>
                            </div>
                            {% empty %}
                            <div class="col-12">
                                <p class="text-success"><i class="bi bi-check-circle"></i> No significant negative root causes detected.</p>
                            </div>
                            {% endfor %}
                        </div>
                        
                        <h6 class="text-uppercase text-muted fw-bold mb-3">Analysis Insights</h6>
                        {% for insight in correlation_analysis.insights %}
                        <div class="card mb-3 border-start border-4 {% if insight.impact == 'Positive' %}border-success{% elif insight.impact == 'Negative' %}border-danger{% else %}border-warning{% endif %}">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <h6 class="mb-0 fw-bold">{{ insight.behavior }}</h6>
                                    <span class="badge bg-secondary">Correlation: {{ insight.correlation }}</span>
                                </div>
                                <p class="mb-2">{{ insight.insight }}</p>
                                <div class="d-flex align-items-center text-muted small bg-light p-2 rounded">
                                    <i class="bi bi-lightbulb-fill text-warning me-2"></i>
                                    <span>{{ insight.recommendation }}</span>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                        
                        <p class="text-end text-muted small mt-3">
                            <i class="bi bi-info-circle"></i> 
                            Analyzed {{ correlation_analysis.data_points_analyzed }} data points
                        </p>
                    </div>
                {% else %}
                    {% if has_sufficient_data %}
                    <div class="text-center py-5">
                        <i class="bi bi-diagram-3 text-muted" style="font-size: 4rem;"></i>
                        <h4 class="mt-3 text-muted">No correlation analysis yet</h4>
                        <p class="text-muted">Click "Run Analysis" to discover hidden patterns in your health data.</p>
                    </div>
                    {% endif %}
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# Habits Template Content
habits_content = """{% extends 'base.html' %}

{% block title %}Habit Analysis - Health Recommendation System{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-md-12">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="{% url 'analytics' %}">Analytics</a></li>
                <li class="breadcrumb-item active" aria-current="page">Habits</li>
            </ol>
        </nav>
        <h2 class="text-white">
            <i class="bi bi-shield-check"></i> Habit Sensitivity Analysis
        </h2>
        <p class="text-white-50">Analyze habit fragility, resilience, and impact</p>
    </div>
</div>

<div class="row">
    <div class="col-md-12 mb-4">
        <div class="card shadow">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h5 class="card-title mb-0">Habit Analysis Results</h5>
                    <form method="post" action="{% url 'analytics_habits' %}">
                        {% csrf_token %}
                        {% if not has_sufficient_data %}
                        <button type="submit" class="btn btn-info text-white" disabled>
                            <i class="bi bi-magic"></i> Analyze Habits
                        </button>
                        {% else %}
                        <button type="submit" class="btn btn-info text-white">
                            <i class="bi bi-magic"></i> Analyze Habits
                        </button>
                        {% endif %}
                    </form>
                </div>

                {% if not has_sufficient_data %}
                    <div class="alert alert-warning">
                        <i class="bi bi-info-circle"></i> 
                        Insufficient data. Add more health entries to generate this analysis.
                    </div>
                {% endif %}

                {% if habit_analysis %}
                    <div id="results" class="fade-in">
                        
                        <!-- Fragile Habits -->
                        <div class="mb-5">
                            <h5 class="text-danger border-bottom pb-2 mb-3"><i class="bi bi-exclamation-octagon"></i> Fragile Habits (Needs Attention)</h5>
                            <div class="row">
                                {% for habit in habit_analysis.fragile_habits %}
                                <div class="col-md-6 mb-3">
                                    <div class="card border-danger h-100">
                                        <div class="card-body">
                                            <h6 class="fw-bold">{{ habit.name }}</h6>
                                            <div class="mb-2">
                                                <span class="badge bg-danger">Fragility: {{ habit.fragility_score }}%</span>
                                                <span class="badge bg-info">Impact: {{ habit.impact_score }}%</span>
                                            </div>
                                            <p class="small text-muted mb-2">Freq: {{ habit.frequency }}% | {{ habit.duration_days }} days</p>
                                            <div class="bg-light p-2 rounded small">
                                                <ul class="list-unstyled mb-0">
                                                    {% for rec in habit.recommendations %}
                                                    <li><i class="bi bi-arrow-right-short text-danger"></i> {{ rec }}</li>
                                                    {% endfor %}
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                {% empty %}
                                <div class="col-12"><p class="text-muted">No fragile habits detected. Great job!</p></div>
                                {% endfor %}
                            </div>
                        </div>

                        <!-- Resilient Habits -->
                        <div class="mb-5">
                            <h5 class="text-success border-bottom pb-2 mb-3"><i class="bi bi-check-circle"></i> Resilient Habits (Well Established)</h5>
                            <div class="row">
                                {% for habit in habit_analysis.resilient_habits %}
                                <div class="col-md-4 mb-3">
                                    <div class="card border-success h-100">
                                        <div class="card-body">
                                            <h6 class="fw-bold">{{ habit.name }}</h6>
                                            <div class="mb-2">
                                                <span class="badge bg-success">Resilient</span>
                                                <span class="badge bg-primary">Impact: {{ habit.impact_score }}%</span>
                                            </div>
                                            <p class="small text-muted mb-0">Consistent for {{ habit.duration_days }} days</p>
                                        </div>
                                    </div>
                                </div>
                                {% empty %}
                                <div class="col-12"><p class="text-muted">Keep tracking to build resilient habits.</p></div>
                                {% endfor %}
                            </div>
                        </div>
                        
                        <!-- High Impact -->
                        <div class="mb-3">
                            <h5 class="text-primary border-bottom pb-2 mb-3"><i class="bi bi-star"></i> High Impact Areas</h5>
                            <div class="row">
                                {% for habit in habit_analysis.high_impact_habits %}
                                <div class="col-md-6 mb-3">
                                    <div class="card border-primary h-100 bg-primary bg-opacity-10">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between">
                                                <h6 class="fw-bold">{{ habit.name }}</h6>
                                                <span class="badge bg-primary">Impact: {{ habit.impact_score }}%</span>
                                            </div>
                                            <p class="small mb-0 mt-2">Focusing on this habit yields the highest health returns.</p>
                                        </div>
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        </div>

                        <p class="text-end text-muted small mt-3">
                            <i class="bi bi-info-circle"></i> 
                            Total habits analyzed: {{ habit_analysis.total_habits_analyzed }}
                        </p>
                    </div>
                {% else %}
                    {% if has_sufficient_data %}
                    <div class="text-center py-5">
                        <i class="bi bi-shield-check text-muted" style="font-size: 4rem;"></i>
                        <h4 class="mt-3 text-muted">No habit analysis yet</h4>
                        <p class="text-muted">Click "Analyze Habits" to assess your behavioral patterns.</p>
                    </div>
                    {% endif %}
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# Write files
files = {
    'analytics_recovery.html': recovery_content,
    'analytics_correlation.html': correlation_content,
    'analytics_habits.html': habits_content
}

print(f"Writing templates to {TEMPLATES_DIR}...")

for filename, content in files.items():
    path = os.path.join(TEMPLATES_DIR, filename)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully wrote {filename}")
    except Exception as e:
        print(f"Error writing {filename}: {e}")

print("Template update complete.")
