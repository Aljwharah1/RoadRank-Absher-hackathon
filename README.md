<p align="left">
  <img src="./frontend/logohdi.png" alt="RoadRank Logo" width="100" style="float:left; margin-right:10px;"/>
  <h1 style="display:inline;">RoadRank</h1>
</p>

**AI-Powered Safe Driving Prediction & Recommendation System**

---

## 🚩 Problem  

Road safety remains a critical challenge, with thousands of accidents occurring annually due to unsafe driving behaviors. Traditional methods of assessing driver safety are often reactive, addressing issues only after accidents occur.

There is a need for a proactive system that can:
- Analyze driving behavior patterns in real-time
- Predict accident probability before incidents happen
- Provide personalized recommendations to improve driving safety
- Motivate drivers to maintain safe driving habits through gamification

**RoadRank** was built to address this challenge by leveraging machine learning to predict accident probability and provide actionable insights for safer driving.

---

## 💡 Solution  

**RoadRank** uses machine learning to analyze driving behavior and predict accident probability, providing drivers with a personalized Safe Driving Index (HDI).

**How it works:**  
1. **Data Collection:** Gathers driving behavior data from the last 30 days.
2. **Behavior Analysis:** Processes speed patterns, violations, and driving consistency.
3. **Accident Prediction:** Uses XGBoost model to estimate accident probability for the current month.
4. **HDI Calculation:** Generates a Safe Driving Index score from 0 to 100.
5. **Smart Recommendations:** Provides personalized tasks and suggestions to improve driving safety.
6. **Rewards & Motivation:** Gamifies safe driving through levels, rewards, and achievements.

---

## 🗂️ Project Structure 

```bash
ROADRANK-ABSHER-HACKATHON/
│
├── Model/                           # Machine learning model and training
│   ├── XGBoost.ipynb                # Model training notebook
│   ├── encoders.joblib              # Feature encoders
│   └── xgboost_model.joblib         # Trained XGBoost model
│
├── backend/                         # Backend API and server logic
│   └── main.py                      # FastAPI application entry point
│
├── data/                            # Training and testing datasets
│   ├── Riyadh Roadway Environment.xlsx
│   ├── Traffic Accident Statistics.xlsx
│   └── Trip Summary.xlsx
│
├── frontend/                        # User interface
│   ├── HDI.html                     # Interactive UI prototype
│   └── logohdi.png                  # RoadRank logo
│
└── README.md                        # Project documentation
```

---

## 🚗 Key Features  

- **30-Day Driving Behavior Analysis** — Comprehensive evaluation of recent driving patterns
- **Accident Probability Prediction** — ML-powered risk assessment using XGBoost
- **HDI (Safe Driving Index)** — Personalized score from 0 to 100
- **Smart Recommendation Engine** — AI-generated suggestions based on driving behavior
- **Interactive UI Prototype** featuring:
  - HDI main gauge visualization
  - Real-time accident probability display
  - Violations tracking and history
  - Personalized tasks & recommendations
  - Rewards and leveling system
  - Detailed driving indicators dashboard

---

## 🧠 Machine Learning Model  

We trained an **XGBoost regression model** using:  
- Historical accident data from Riyadh
- Synthetic driver behavior patterns
- Roadway environment characteristics

### **Why XGBoost?**

We selected XGBoost due to its:
- **High performance on structured/tabular data** — Ideal for our driving behavior dataset
- **Ability to model non-linear relationships** — Captures complex driving behavior patterns
- **Robustness against missing or skewed data** — Handles real-world data imperfections
- **Minimal need for extensive hyperparameter tuning** — Efficient development cycle
- **Strong interpretability** — Feature importance metrics help explain predictions

### **Key Features Used in the Model**

The model was trained on behavioral and environmental signals strongly correlated with accident risk, including:

- **Average driving speed** — Overall speed patterns
- **Speed variance & extreme speeding frequency** — Consistency and risk-taking behavior
- **Harsh braking events** — Sudden stops indicating reactive driving
- **Trip duration & distance** — Exposure to road risks
- **Night-time driving ratio** — Higher-risk time periods
- **Violation count (past month)** — Historical rule-breaking behavior
- **Road environment risk level** — Infrastructure and traffic conditions

These features help the model understand nuanced driver behavior patterns and their correlation with accident probability.

### **Model Performance**
- **RMSE:** 5.27  
- **MAE:** 2.71  
- **R² Score:** 0.974  

These results demonstrate strong predictive accuracy and reliability in estimating accident probability based on recent driving behavior.

---

## 🗂️ Data Pipeline  

1. **Data Ingestion** — Collect driving behavior and accident data
2. **Data Cleaning** — Handle missing values and outliers
3. **Feature Engineering** — Extract meaningful driving patterns
4. **Encoding & Normalization** — Prepare data for model training
5. **Dataset Merging** — Combine multiple data sources
6. **Model Training** — Train XGBoost on historical data
7. **Prediction** — Estimate accident probability
8. **HDI Generation** — Calculate Safe Driving Index
9. **UI Integration** — Send results to frontend

---

## 🧩 Recommendation System  

The intelligent recommendation engine analyzes model output to generate personalized driving improvement suggestions:

- **Speed Management** — Reduce excessive speeding behavior
- **Task Completion** — Complete specific actions to raise HDI score
- **Risk Avoidance** — Identify and avoid high-risk driving patterns
- **Violation Resolution** — Pay outstanding traffic violations
- **Consistency Improvement** — Maintain safe driving habits over time
- **Behavior Correction** — Address specific unsafe driving behaviors

### **Example Recommendation**

To make the system clearer and more realistic, here's how recommendations work in practice:

**Example:** If the model detects frequent hard braking, the system recommends:

> *"Maintain a safer following distance and avoid sudden stops this week to improve your HDI score."*

This personalized feedback helps drivers understand exactly what behaviors to modify for safer driving.

---

## 🖥️ Prototype UI  

The interactive user interface includes:

- **HDI Gauge** — Visual representation of safe driving score
- **Accident Probability Display** — Real-time risk assessment
- **Violations Overview** — Track and manage traffic violations
- **Rewards & Levels** — Gamification elements to motivate safe driving
- **Personalized Tasks** — Actionable recommendations
- **Driving Indicators** — Detailed metrics and analytics
- **Clean & User-Friendly Design** — Intuitive navigation and experience

---

## 🚀 Getting Started

You can run **RoadRank** using the following methods:

---

### ⚙️ Run Directly with FastAPI

1️⃣ **Install dependencies**
```bash
pip install -r requirements.txt
```

2️⃣ **Start the FastAPI application**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

> Then open http://localhost:8000 in your browser.

---


### 🧠 Note
- Ensure you have the trained model files (`xgboost_model.joblib` and `encoders.joblib`) in the `Model/` directory
- Update configuration settings in `backend/main.py` as needed

---

## 🚀 Future Enhancements

- **Model Improvement** — Enhance XGBoost accuracy with additional behavioral features and real-time data patterns
- **Real-time Integration** — Connect with Absher API for live driving data collection and instant feedback
- **Advanced Rewards System** — Expand gamification with achievements, leaderboards, and social challenges
- **Mobile Application** — Develop native iOS and Android apps for seamless user experience
- **Multi-city Support** — Extend coverage beyond Riyadh to other cities across Saudi Arabia
- **Predictive Maintenance** — Add vehicle health monitoring and maintenance recommendations
- **Driver Coaching** — Implement AI-powered personalized coaching and training modules
- **Insurance Integration** — Partner with insurance providers for premium discounts based on HDI scores
- **Fleet Management** — Expand system for commercial fleet monitoring and management
- **Advanced Analytics** — Add comprehensive reporting dashboard for driving behavior trends

---

## 📊 Technical Stack

- **Machine Learning:** XGBoost, Scikit-learn, Pandas, NumPy
- **Backend:** FastAPI, Python
- **Frontend:** HTML, CSS, JavaScript
- **Model Persistence:** Joblib
- **Data Processing:** Excel, CSV

---

## 👥 Team Members

- **Aljwharah Almousa** 
- **Joud Binjebrin**
- **Nouf Bin Huwaidi**
- **Ruwaa Surrati**

---

