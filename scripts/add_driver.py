from pathlib import Path
import pandas as pd
import joblib

trip_file = Path(__file__).parent.parent / 'data' / 'Trip Summary.xlsx'
model_file = Path(__file__).parent.parent / 'Model' / 'xgboost_model.joblib'
new_id = '1234567890'

print('Loading Excel:', trip_file)
df = pd.read_excel(trip_file)

# If driver exists, exit
if any(df['driver_id'].astype(str) == new_id):
    print('Driver already exists in sheet.')
    exit(0)

# Use first row as template if available, otherwise create minimal structure
if len(df) > 0:
    template = df.iloc[0].copy()
else:
    template = pd.Series()

# Create new record based on template
new_record = template.copy()
# Fill or overwrite important fields with sensible defaults
new_record['driver_id'] = new_id
new_record['driver_name'] = 'أحمد محمد العتيبي'
new_record['avg_speed'] = 80.0
new_record['max_speed'] = 120.0
new_record['harsh_brakes_count'] = 2
# support both possible column names
if 'harsh_accel_count' in new_record.index:
    new_record['harsh_accel_count'] = 1
else:
    new_record['harsh_accels_count'] = 1
new_record['lane_changes_count'] = 5
new_record['speeding_percentage'] = 0.0
new_record['traffic_congestion_km'] = 5.0
new_record['weather_condition'] = 3
new_record['traffic_violations'] = 0
new_record['accidents_count'] = 0
new_record['phone_usage'] = 0
new_record['road_quality'] = 3
new_record['time_of_day'] = 2
new_record['trip_duration'] = 60.0
new_record['distance_driven'] = 50.0
new_record['night_driving_hours'] = 0.0
new_record['number_of_passengers'] = 1

# Attempt to compute initial safe_driving_score using model
try:
    model = joblib.load(model_file)
    # Build prediction input similar to backend
    input_data = {
        'driver_id': 1,
        'driver_category': new_record.get('driver_category', 1),
        'driver_category_ar': new_record.get('driver_category_ar', 1),
        'avg_speed': float(new_record.get('avg_speed', 80)),
        'max_speed': float(new_record.get('max_speed', 120)),
        'harsh_brakes_count': int(new_record.get('harsh_brakes_count', 0)),
        'harsh_accels_count': int(new_record.get('harsh_accel_count', new_record.get('harsh_accels_count', 0))),
        'lane_changes_count': int(new_record.get('lane_changes_count', 0)),
        'speeding_percentage': float(new_record.get('speeding_percentage', 0)),
        'avg_congestion': float(new_record.get('traffic_congestion_km', 5) / 10),
        'avg_visibility': int(new_record.get('weather_condition', 3) * 30),
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
    import pandas as _pd
    input_df = _pd.DataFrame([input_data])[feature_order]
    pred = model.predict(input_df)
    score = float(pred[0])
    print('Predicted initial score:', score)
    new_record['safe_driving_score'] = score
except Exception as e:
    print('Model predict failed:', e)
    new_record['safe_driving_score'] = 70.0

# Append and save
new_df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
new_df.to_excel(trip_file, index=False)
print('Appended new driver and saved Excel.')
