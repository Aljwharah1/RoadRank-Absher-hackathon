# RoadRank-
# HDI – Safe Driving Prediction & Recommendation System  
A Machine Learning–Powered Safe Driving Index (HDI)

---

## 📌 Overview  
HDI is a system designed to analyze driving behavior and estimate the likelihood of accidents within the current month using an XGBoost predictive model.  
The system provides personalized recommendations to help users improve their safe driving score, supported by an interactive user interface.

---

## 🚗 Key Features  
- **Driving behavior analysis for the last 30 days**  
- **Accident probability prediction using XGBoost**  
- **HDI (Safe Driving Index)** — a score from 0 to 100  
- **Smart recommendation engine** based on model output  
- **Interactive UI Prototype**, featuring:
  - HDI main gauge  
  - Accident probability display  
  - Violations tab  
  - Tasks & recommendations  
  - Rewards tab  
  - Driving indicators  

---

## 🧠 Machine Learning Model  

We trained an XGBoost regression model using:  
- Accident data  
- Synthetic driver behavior data  
- Roadway environment data  

### **Model Performance**
- **RMSE:** 5.27  
- **MAE:** 2.71  
- **R² Score:** 0.974  

These results show that the model is highly capable of predicting accident probability based on recent driving behavior.

---

## 🗂️ Data Pipeline  
1. Data ingestion and cleaning  
2. Feature encoding and normalization  
3. Merging datasets  
4. Training the XGBoost model  
5. Accident probability prediction  
6. Generating the HDI score  
7. Sending output to the prototype UI  

---

## 🧩 Recommendation System  
The recommendation engine uses the model’s output to generate personalized suggestions, such as:  
- Reducing speeding behavior  
- Completing specific tasks to raise the HDI  
- Avoiding high‑risk driving patterns  
- Paying outstanding violations  
- Improving consistency in safe driving  

---

## 🖥️ Prototype UI  
The interactive UI includes:  
- HDI gauge and accident probability  
- Violations overview  
- Rewards and levels  
- Personalized tasks  
- Driving indicators  
- Clean and user-friendly design  

---

## 🚀 Future Work (Roadmap – Next 2 Weeks)  

### **Week 1**  
- Improving XGBoost model accuracy  
- Enhancing the recommendation engine logic  
- UI/UX refinements based on initial testing  

### **Week 2**  
- Connecting all indicators to the backend  
- Developing an advanced reward/leveling system  
- Preparing a 70% complete prototype  
- Initial integration testing with Absher API (conceptual)  

---

## 📁 Project Structure

ROADRANK-ABSHER-HACKATHON/
│
├── backend/
│ └── main.py
│
├── data/
│ ├── Riyadh Roadway Environment.xlsx
│ ├── Traffic Accident Statistics.xlsx
│ └── Trip Summary.xlsx
│
├── frontend/
│ └── HDI.html
│
├── Model/
│ ├── encoders.joblib
│ ├── xgboost_model.joblib
│ └── XGBoost.ipynb
│
└── README.md
---

## 👥 Team  
- Nowf  
- Ruwaa  
- Joud  
- Aljwharah  

---