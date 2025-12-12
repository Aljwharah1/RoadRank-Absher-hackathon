from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import joblib
import pandas as pd
from pathlib import Path
import numpy as np
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(title="RoadRank Prediction API", version="1.0.0")

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained model and encoders
model_path = Path(__file__).parent.parent / "Model" / "xgboost_model.joblib"
encoders_path = Path(__file__).parent.parent / "Model" / "encoders.joblib"
data_path = Path(__file__).parent.parent / "data"

try:
    model = joblib.load(model_path)
    encoders = joblib.load(encoders_path)
    print(f"✓ Model loaded from {model_path}")
except Exception as e:
    print(f"✗ Failed to load model: {e}")
    model = None
    encoders = {}
# Define request body schemas
class PredictionRequest(BaseModel):
    driver_id: str
    avg_speed: float
    harsh_brakes_count: int
    harsh_accel_count: int
    lane_deviation: float
    max_speed: float
    trip_duration: float
    distance_driven: float
    night_driving_hours: float
    number_of_passengers: int
    traffic_congestion_km: float
    weather_condition: int
    traffic_violations: int
    accidents_count: int
    phone_usage: int
    road_quality: int
    time_of_day: int

class TaskCompletionRequest(BaseModel):
    driver_id: str
    task_id: str
    task_title: str
    points_earned: int = 5
    road_quality: int = 3
    time_of_day: int = 2


def prepare_for_predict(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure DataFrame columns are numeric-friendly for the XGBoost model.
    Attempt to use loaded `encoders` for known columns; otherwise
    coerce object/category columns to integer codes.
    """
    df2 = df.copy()
    try:
        if isinstance(encoders, dict) and encoders:
            for col, enc in encoders.items():
                if col in df2.columns:
                    try:
                        # Try encoder.transform; handle 1d/2d outputs
                        vals = df2[col].astype(str).values
                        transformed = enc.transform(vals.reshape(-1, 1)) if hasattr(enc, 'n_features_in_') else enc.transform(vals)
                        # If sparse or has toarray, convert
                        if hasattr(transformed, 'toarray'):
                            arr = transformed.toarray()
                        else:
                            arr = transformed
                        arr = np.asarray(arr)
                        if arr.ndim == 2 and arr.shape[1] == 1:
                            df2[col] = arr.ravel()
                        elif arr.ndim == 2 and arr.shape[1] > 1:
                            # Collapse multi-col encoding into single code by argmax
                            df2[col] = arr.argmax(axis=1)
                        else:
                            df2[col] = arr.ravel()
                    except Exception:
                        df2[col] = pd.Categorical(df2[col]).codes
        else:
            # Fallback: convert object/category columns to integer codes
            for col in df2.select_dtypes(include=['object', 'category']).columns:
                df2[col] = pd.Categorical(df2[col]).codes
    except Exception:
        # As a last resort, coerce any non-numeric to categorical codes
        for col in df2.columns:
            if not pd.api.types.is_numeric_dtype(df2[col]):
                df2[col] = pd.Categorical(df2[col]).codes
    return df2

# Serve frontend HTML
@app.get("/")
async def root():
    frontend_path = Path(__file__).parent.parent / "frontend" / "HDI.html"
    if frontend_path.exists():
        return FileResponse(str(frontend_path), media_type="text/html")
    else:
        return {
            "message": "RoadRank Prediction API",
            "version": "1.0.0",
            "endpoints": {
                "predict": "/predict",
                "health": "/health"
            }
        }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }

@app.post("/predict")
async def predict(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Map form fields to model's expected features
        # These are derived from the form inputs
        input_data = {
            'driver_id': 1 if request.driver_id == 'DRV001' else 0,  # Convert driver_id to numeric
            'driver_category': 1,  # Default category
            'driver_category_ar': 1,  # Default Arabic category
            'avg_speed': request.avg_speed,
            'max_speed': request.max_speed,
            'harsh_brakes_count': request.harsh_brakes_count,
            'harsh_accels_count': request.harsh_accel_count,  # Map harsh_accel_count to harsh_accels_count
            'lane_changes_count': int(request.lane_deviation * 10),  # Derive from lane deviation
            'speeding_percentage': (request.max_speed - 100) / 100 * 100 if request.max_speed > 100 else 0,  # Calculate speeding %
            'avg_congestion': request.traffic_congestion_km / 10,  # Normalize congestion
            'avg_visibility': request.weather_condition * 30,  # Map weather to visibility (1-3 -> 30-90)
            'road_type': request.road_quality,  # Map road_quality to road_type
            'actual_driver_type': 2,  # Default driver type
            'time_of_day': request.time_of_day,
            'weather': request.weather_condition,
            'recommendation': 1,  # Default recommendation
            'recommendation_ar': 1  # Default Arabic recommendation
        }
        
        # Convert to DataFrame with proper order
        feature_order = ['driver_id', 'driver_category', 'driver_category_ar', 'avg_speed', 'max_speed',
                        'harsh_brakes_count', 'harsh_accels_count', 'lane_changes_count', 'speeding_percentage',
                        'avg_congestion', 'avg_visibility', 'road_type', 'actual_driver_type', 'time_of_day',
                        'weather', 'recommendation', 'recommendation_ar']
        
        input_df = pd.DataFrame([input_data])[feature_order]
        # Prepare input and make prediction
        prepared = prepare_for_predict(input_df)
        pred_score = None
        if model is not None:
            try:
                pred_score = float(model.predict(prepared)[0])
            except Exception:
                pred_score = None
        
        return {
            "success": True,
            "safe_driving_score": pred_score,
            "input_features": request.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

@app.post("/complete-task")
async def complete_task(request: TaskCompletionRequest):
    """
    Mark a task as completed for a driver.
    Updates the Excel data and recalculates the driver's score.
    """
    try:
        # Load the trip summary data
        trip_file = data_path / "Trip Summary.xlsx"
        df_trips = pd.read_excel(trip_file)
        
        # Find the driver's record
        driver_records = df_trips[df_trips['driver_id'].astype(str) == request.driver_id]
        
        if driver_records.empty:
            raise HTTPException(status_code=404, detail=f"Driver {request.driver_id} not found")
        
        # Update the task completion in the Excel file
        # Add a new record with the completed task
        new_record = driver_records.iloc[0].copy()
        
        # Improve metrics based on task completion
        # Tasks improve specific driving behaviors
        task_improvements = {
            'awareness_video': {'harsh_brakes_count': -1, 'harsh_accel_count': -1},
            'safety_guidelines': {'harsh_brakes_count': -2, 'traffic_violations': -1},
            'license_renewal': {'avg_speed': -5},
            'vehicle_inspection': {'max_speed': -10},
            'insurance_renewal': {'traffic_violations': -1},
            'vehicle_update': {'avg_speed': -3}
        }
        
        improvements = task_improvements.get(request.task_id, {})
        
        for metric, improvement in improvements.items():
            if metric in new_record:
                new_record[metric] = max(0, new_record[metric] + improvement)
        
        # Add task completion metadata
        new_record['task_completed'] = request.task_title
        new_record['completion_date'] = datetime.now().strftime('%Y-%m-%d')
        new_record['points_earned'] = request.points_earned

        # Recalculate score with updated data BEFORE appending, then persist it
        prediction_input = {
            'driver_id': 1,
            'driver_category': new_record.get('driver_category', 1),
            'driver_category_ar': new_record.get('driver_category_ar', 1),
            'avg_speed': float(new_record.get('avg_speed', 80)),
            'max_speed': float(new_record.get('max_speed', 120)),
            'harsh_brakes_count': int(new_record.get('harsh_brakes_count', 0)),
            'harsh_accels_count': int(new_record.get('harsh_accel_count', 0)) if new_record.get('harsh_accel_count', None) is not None else int(new_record.get('harsh_accels_count', 0)),
            'lane_changes_count': int(new_record.get('lane_changes_count', 0)),
            'speeding_percentage': float(new_record.get('speeding_percentage', 0)),
            'avg_congestion': float(new_record.get('traffic_congestion_km', 5) / 10) if new_record.get('traffic_congestion_km', None) is not None else float(new_record.get('avg_congestion', 0)),
            'avg_visibility': int(new_record.get('weather_condition', 3) * 30) if new_record.get('weather_condition', None) is not None else int(new_record.get('avg_visibility', 90)),
            'road_type': int(new_record.get('road_quality', 3)),
            'actual_driver_type': 2,
            'time_of_day': int(new_record.get('time_of_day', 2)),
            'weather': int(new_record.get('weather_condition', 3)),
            'recommendation': 1,
            'recommendation_ar': 1
        }

        feature_order = ['driver_id', 'driver_category', 'driver_category_ar', 'avg_speed', 'max_speed',
                        'harsh_brakes_count', 'harsh_accels_count', 'lane_changes_count', 'speeding_percentage',
                        'avg_congestion', 'avg_visibility', 'road_type', 'actual_driver_type', 'time_of_day',
                        'weather', 'recommendation', 'recommendation_ar']

        input_df = pd.DataFrame([prediction_input])[feature_order]
        prepared = prepare_for_predict(input_df)
        new_score = None
        if model is not None:
            try:
                new_score = float(model.predict(prepared)[0])
            except Exception:
                new_score = None

        # Persist the new score into the new record before appending
        if new_score is not None:
            new_record['safe_driving_score'] = new_score

        # Append to Excel and save
        df_trips = pd.concat([df_trips, pd.DataFrame([new_record])], ignore_index=True)
        df_trips.to_excel(trip_file, index=False)

        return {
            "success": True,
            "message": f"Task '{request.task_title}' completed successfully!",
            "points_earned": request.points_earned,
            "new_score": new_score,
            "score_improvement": (new_score - float(driver_records.iloc[0].get('safe_driving_score', 70))) if new_score is not None else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Task completion failed: {str(e)}")

@app.get("/driver/{driver_id}/tasks")
async def get_driver_tasks(driver_id: str):
    """
    Get the list of tasks for a specific driver.
    """
    try:
        # Define available tasks
        tasks = [
            {
                'id': 'awareness_video',
                'title': 'مشاهدة فيديو توعوي إلزامي',
                'subtitle': 'بناءً على سلوك القيادة: "مخاطر السرعة الزائدة"',
                'icon': 'bi-play-circle-fill',
                'duration': '5 دقائق',
                'points': 5,
                'status': 'pending'
            },
            {
                'id': 'license_renewal',
                'title': 'تجديد رخصة القيادة',
                'subtitle': 'تنتهي بعد 45 يوم',
                'icon': 'bi-person-vcard-fill',
                'duration': 'قريباً',
                'points': 10,
                'status': 'completed'
            },
            {
                'id': 'vehicle_inspection',
                'title': 'فحص دوري للمركبة',
                'subtitle': 'مطلوب خلال 15 يوم',
                'icon': 'bi-gear-fill',
                'duration': 'قريباً',
                'points': 8,
                'status': 'pending'
            },
            {
                'id': 'insurance_renewal',
                'title': 'تجديد التأمين',
                'subtitle': 'تم التجديد بنجاح',
                'icon': 'bi-shield-fill-check',
                'duration': 'مكتمل',
                'points': 5,
                'status': 'completed'
            },
            {
                'id': 'vehicle_update',
                'title': 'تحديث بيانات المركبة',
                'subtitle': 'تحديث معلومات الملكية',
                'icon': 'bi-car-front-fill',
                'duration': 'مطلوب',
                'points': 3,
                'status': 'pending'
            }
        ]
        
        return {
            "driver_id": driver_id,
            "tasks": tasks,
            "total_available_points": sum(t['points'] for t in tasks if t['status'] == 'pending')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get tasks: {str(e)}")


@app.get("/driver/{driver_id}")
async def get_driver(driver_id: str):
    """
    Return driver metrics from the Trip Summary.xlsx and a predicted safe driving score.
    """
    try:
        trip_file = data_path / "Trip Summary.xlsx"
        df_trips = pd.read_excel(trip_file)

        driver_records = df_trips[df_trips['driver_id'].astype(str) == driver_id]
        # If direct match fails, try matching against common national/id columns
        if driver_records.empty:
            possible_cols = [c for c in df_trips.columns if c.lower() in ('national_id','id_number','user_id','driver_national_id','nationalid')]
            for col in possible_cols:
                driver_records = df_trips[df_trips[col].astype(str) == driver_id]
                if not driver_records.empty:
                    break
        if driver_records.empty:
            # try partial/hash match if driver_id is numeric and driver_id column contains hashes
            # fallback: try to match last 4 digits
            try:
                if driver_id.isdigit() and len(driver_id) >= 4:
                    tail = driver_id[-4:]
                    driver_records = df_trips[df_trips['driver_id'].astype(str).str.endswith(tail)]
            except Exception:
                pass
        if driver_records.empty:
            raise HTTPException(status_code=404, detail=f"Driver {driver_id} not found")

        record = driver_records.iloc[0].to_dict()

        # Build prediction input similarly to other endpoints
        prediction_input = {
            'driver_id': 1,
            'driver_category': record.get('driver_category', 1),
            'driver_category_ar': record.get('driver_category_ar', 1),
            'avg_speed': float(record.get('avg_speed', 80)),
            'max_speed': float(record.get('max_speed', 120)),
            'harsh_brakes_count': int(record.get('harsh_brakes_count', 0)),
            'harsh_accels_count': int(record.get('harsh_accel_count', 0)) if record.get('harsh_accel_count', None) is not None else int(record.get('harsh_accels_count', 0)),
            'lane_changes_count': int(record.get('lane_changes_count', 0)),
            'speeding_percentage': float(record.get('speeding_percentage', 0)),
            'avg_congestion': float(record.get('traffic_congestion_km', 5) / 10) if record.get('traffic_congestion_km', None) is not None else float(record.get('avg_congestion', 0)),
            'avg_visibility': int(record.get('weather_condition', 3) * 30) if record.get('weather_condition', None) is not None else int(record.get('avg_visibility', 90)),
            'road_type': int(record.get('road_quality', 3)),
            'actual_driver_type': 2,
            'time_of_day': int(record.get('time_of_day', 2)),
            'weather': int(record.get('weather_condition', 3)),
            'recommendation': 1,
            'recommendation_ar': 1
        }

        feature_order = ['driver_id', 'driver_category', 'driver_category_ar', 'avg_speed', 'max_speed',
                        'harsh_brakes_count', 'harsh_accels_count', 'lane_changes_count', 'speeding_percentage',
                        'avg_congestion', 'avg_visibility', 'road_type', 'actual_driver_type', 'time_of_day',
                        'weather', 'recommendation', 'recommendation_ar']

        input_df = pd.DataFrame([prediction_input])[feature_order]
        prepared = prepare_for_predict(input_df)
        pred_score = None
        if model is not None:
            try:
                pred_score = float(model.predict(prepared)[0])
            except Exception:
                pred_score = None

        # Return the original record plus predicted score
        return {
            'driver_id': driver_id,
            'record': record,
            'predicted_score': pred_score
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load driver: {str(e)}")


@app.get('/drivers')
async def list_drivers(limit: int = 20):
    """Return a small sample of drivers (driver_id and common id columns) to help map frontend IDs."""
    try:
        trip_file = data_path / "Trip Summary.xlsx"
        df_trips = pd.read_excel(trip_file)

        cols = ['driver_id'] + [c for c in df_trips.columns if c.lower() in ('national_id','id_number','user_id','driver_national_id','nationalid')]
        if not cols:
            # fallback to first 5 columns
            cols = list(df_trips.columns[:5])

        sample = df_trips[cols].head(limit).to_dict(orient='records')
        return {'count': len(sample), 'columns': cols, 'sample': sample}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to list drivers: {str(e)}")