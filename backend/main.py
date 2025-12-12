from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
from pathlib import Path
import numpy as np

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

try:
    model = joblib.load(model_path)
    encoders = joblib.load(encoders_path)
    print(f"✓ Model loaded from {model_path}")
except Exception as e:
    print(f"✗ Failed to load model: {e}")
    model = None
    encoders = {}

# Define request body schema based on actual features
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

@app.get("/")
async def root():
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
        
        # Make prediction
        prediction = model.predict(input_df)
        
        return {
            "success": True,
            "safe_driving_score": float(prediction[0]),
            "input_features": request.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")