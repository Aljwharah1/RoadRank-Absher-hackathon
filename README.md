# RoadRank — HDI (Safe Driving Prediction & Recommendation System)

A full-stack prototype for safe driving prediction using XGBoost. Drivers complete tasks through an interactive dashboard to improve their HDI (Safe Driving Index) score, with progress persisted to Excel.

---

## 📌 Overview

HDI analyzes driving behavior and predicts accident probability using an XGBoost regression model. The system provides:
- **Real-time HDI score** (0–100 scale) based on recent driving metrics
- **Interactive task system** — drivers complete tasks to improve their score
- **Data persistence** — task completions are saved to `data/Trip Summary.xlsx`
- **Personalized recommendations** based on predicted behavior

---

## 🚗 Key Features

- **Driving behavior analysis** for the last 30 days
- **Accident probability prediction** using XGBoost (RMSE: 5.27, MAE: 2.71, R²: 0.974)
- **HDI (Safe Driving Index)** — a score from 0 to 100
- **Smart recommendation engine** based on model output
- **Interactive UI prototype** featuring:
  - HDI gauge and accident probability display
  - Task list with points and completion status
  - Violations overview
  - Rewards and progress tracking
  - Real-time notifications

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ and a virtual environment (project uses `.venv`)

### 1. Start the Backend Server

```powershell
cd C:\Users\HP\RoadRank-Absher-hackathon
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     ✓ Model loaded from .../xgboost_model.joblib
INFO:     Application startup complete.
```

### 2. Open the Frontend

Open in your browser:
```
file:///c:/Users/HP/RoadRank-Absher-hackathon/frontend/HDI.html
```

### 3. Test Task Completion

Navigate to the **"المهام"** (Tasks) tab and click a checkbox to complete a task. You should see:
- ✓ Checkbox marks as complete
- Score improves (points-based)
- Green notification: "تم إكمال المهمة! حصلت على X نقاط"
- New row added to `data/Trip Summary.xlsx`

---

## 📊 API Summary

### Core Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/health` | Check server status and model load state |
| `POST` | `/predict` | Predict score from driving metrics |
| `POST` | `/complete-task` | Mark a task complete, update metrics, recalculate score |
| `GET` | `/driver/{driver_id}` | Retrieve driver record and predicted score |
| `GET` | `/driver/{driver_id}/tasks` | List all tasks for a driver |
| `GET` | `/drivers` | List sample driver IDs from the dataset |

### Example Requests (PowerShell)

```powershell
# Get driver and predicted score
Invoke-RestMethod -Uri 'http://localhost:8000/driver/DRV001' -Method GET | ConvertTo-Json -Depth 5

# Complete a task
Invoke-RestMethod -Uri 'http://localhost:8000/complete-task' -Method POST `
  -ContentType 'application/json' `
  -Body '{
    "driver_id": "DRV001",
    "task_id": "awareness_video",
    "task_title": "مشاهدة فيديو توعوي إلزامي",
    "points_earned": 5
  }' | ConvertTo-Json -Depth 5
```

Interactive API docs available at: `http://localhost:8000/docs` (Swagger UI)

---

## 🧠 Machine Learning Model

### Model Type
- **Algorithm**: XGBoost Regressor
- **Target**: Safe Driving Score (0–100)
- **Training Data**: Accident data + synthetic driver behavior + roadway environment

### Model Performance
- **RMSE**: 5.27
- **MAE**: 2.71
- **R² Score**: 0.974

### Features (17 total)
- `driver_id`, `driver_category`, `driver_category_ar` (categorical)
- `avg_speed`, `max_speed`, `speeding_percentage` (speed metrics)
- `harsh_brakes_count`, `harsh_accels_count`, `lane_changes_count` (behavior)
- `avg_congestion`, `avg_visibility` (environment)
- `road_type`, `actual_driver_type`, `time_of_day`, `weather` (context)
- `recommendation`, `recommendation_ar` (model output/feedback)

---

## 🎯 Task System

### Available Tasks

1. **Awareness Video** (5 points)
   - Title: "مشاهدة فيديو توعوي إلزامي"
   - Improves: harsh brakes & acceleration

2. **License Renewal** (10 points)
   - Title: "تجديد رخصة القيادة"
   - Improves: average speed

3. **Vehicle Inspection** (8 points)
   - Title: "فحص دوري للمركبة"
   - Improves: max speed

4. **Insurance Renewal** (5 points)
   - Title: "تجديد التأمين"
   - Improves: traffic violations

5. **Vehicle Update** (3 points)
   - Title: "تحديث بيانات المركبة"
   - Improves: average speed

### Task Completion Flow

When a driver completes a task:
1. **Frontend** sends POST `/complete-task` request
2. **Backend**:
   - Finds the driver in `data/Trip Summary.xlsx`
   - Applies metric improvements (task-specific)
   - Appends a new record with task metadata and timestamp
   - Runs XGBoost model with updated metrics
   - Returns new `safe_driving_score` and score improvement
3. **Frontend**:
   - Marks checkbox as complete (✓)
   - Animates score increase smoothly
   - Shows success notification with points earned
   - Updates UI display

---

## 🗂️ Data Pipeline

1. Data ingestion and cleaning
2. Feature encoding and normalization
3. Merging datasets (roadway + accident + behavior)
4. Training XGBoost model
5. Serializing model + encoders to joblib files
6. Backend loads and uses model for predictions
7. Frontend calls API to fetch scores and persist task completions to Excel  

---

## 🧩 Recommendation System

The recommendation engine generates personalized suggestions based on model output:
- Reducing speeding behavior
- Completing specific tasks to raise the HDI
- Avoiding high-risk driving patterns
- Paying outstanding violations
- Improving consistency in safe driving  

---

## � Testing & Troubleshooting

### Test Scenario 1: Single Task
1. Start backend
2. Open frontend
3. Click one pending task checkbox
4. Verify:
   - Checkbox marks as ✓
   - Score increases (~5 points)
   - Green notification appears
   - New row in Excel with timestamp

### Test Scenario 2: Multiple Tasks
1. Complete 3 different tasks
2. Verify cumulative score improvement
3. Check Excel has 3 new rows with all task data

### Test Scenario 3: Data Persistence
1. Complete a task (checkbox marks)
2. Refresh the page (F5)
3. Verify checkbox still shows as complete (from Excel)

### Common Issues

**Issue: Connection Error ("خطأ في الاتصال")**
- Ensure backend is running: `python -m uvicorn backend.main:app --reload`
- Check port 8000 is free: `netstat -ano | findstr :8000`

**Issue: Excel file locked**
- Close `data/Trip Summary.xlsx` if open in Excel
- Ensure backend has write permissions

**Issue: Task won't mark complete**
- Open browser console (F12) to see errors
- Verify `/health` endpoint responds: `Invoke-RestMethod http://localhost:8000/health`

---

## 📁 Project Structure

```
ROADRANK-ABSHER-HACKATHON/
├── backend/
│   └── main.py                    # FastAPI server (predictions, task endpoints)
├── data/
│   ├── Riyadh Roadway Environment.xlsx
│   ├── Traffic Accident Statistics.xlsx
│   └── Trip Summary.xlsx          # Driver data & task completion records
├── frontend/
│   └── HDI.html                   # Interactive dashboard
├── Model/
│   ├── xgboost_model.joblib       # Trained XGBoost regressor
│   ├── encoders.joblib            # Feature encoders (categorical mappings)
│   └── XGBoost.ipynb              # Model training notebook
└── README.md                       # This file
```

---

## 🚀 Future Enhancements

- **Database Integration**: Scale from Excel to PostgreSQL/MongoDB
- **Real-time Sync**: WebSockets for live score updates
- **Leaderboards**: Compare drivers and enable competition
- **Mobile App**: Dedicated mobile dashboard
- **Automated Tasks**: Tasks triggered by real driving events
- **Push Notifications**: Notify drivers of new tasks and score changes
- **Analytics Dashboard**: Track completion rates and impact
- **Task Categories**: Group by Safety, Maintenance, Legal, etc.

---

## 👥 Team

- Nowf
- Ruwaa
- Joud
- Aljwharah

---