import base64
import json
import urllib.request
import zlib

mermaid_code = """
flowchart TD
    classDef default fill:#ffffff,stroke:#000000,stroke-width:1.5px,color:#000000,font-family:sans-serif;
    classDef dashed fill:#ffffff,stroke:#000000,stroke-width:1.5px,stroke-dasharray: 4 4;
    
    UI([Web Dashboard UI])
    
    DI[/"Data Input Layer
    • User Lifestyle Data
    • Sleep Duration, Exercise
    • Calorie Intake, Hydration"/]
    
    DP["Data Preprocessing
    • Normalization, Cleansing
    • Feature Extraction"]
    
    subgraph ML_Sub_Layer ["Machine Learning Prediction Layer"]
        direction LR
        LR[Linear Regression]
        DT[Decision Tree]
        RF[Random Forest]
    end
    
    RA["Risk Analysis
    • Deviation Scoring
    • Feature Correlation & Trends"]
    
    RC{"Risk Classification"}
    
    RL["Risk Levels:
    Low | Moderate | High"]
    
    Dash["Health Analytics Dashboard
    • BMI, BMR, TDEE, Sleep
    • Exercise, Risk Levels"]
    
    Rec["Recommendation Engine
    • Personalized Action Plans
    • Health Records & Logs"]
    
    DB[("Database")]

    UI --> DI
    DI --> DP
    DP --> LR & DT & RF
    
    LR & DT & RF --> RA
    LR & DT & RF --> RC
    
    RC --> RL
    
    RA --> Dash
    RA --> Rec
    RL --> Dash
    RL --> Rec
    
    Dash --> DB
    Rec --> DB
"""

# Mermaid encoding requires creating a JSON with the code, then base64 encoding it
j = json.dumps({"code": mermaid_code, "mermaid": {"theme": "default"}})
b64 = base64.b64encode(j.encode('utf-8')).decode('utf-8')

url = f"https://mermaid.ink/img/{b64}"
output_path = r"c:\Users\abhin\Downloads\health cur\pic ieee.png"

try:
    print(f"Downloading from {url}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
        out_file.write(response.read())
    print(f"Successfully saved diagram to {output_path}")
except Exception as e:
    print(f"Failed to download image: {e}")
