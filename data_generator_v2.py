"""
Safe Driving Data Generator - Saudi Arabia
Generates realistic synthetic telemetry data for training AI safety models.

This module combines:
- Synthetic driver telemetry (second-by-second)
- Real road context (speed limits, congestion)
- Realistic driving behavior patterns

Author: RoadRank Team
Version: 2.0
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple, Optional
import uuid
import warnings
import json
import os

warnings.filterwarnings('ignore')

# ============================================================================
# 1. DRIVER PROFILES - Define realistic driving behaviors
# ============================================================================

DRIVER_PROFILES = {
    'safe': {
        'name_ar': 'آمن',
        'speed_variance': 2,
        'acceleration_range': (-3, 3),
        'harsh_brake_probability': 0.005,
        'lane_change_probability': 0.001,
        'speed_limit_adherence': 0.95,
        'sign_ignore_rate': 0.05,
        'congestion_patience': 0.9,
        'risk_level': 0.1
    },
    'moderate': {
        'name_ar': 'معتدل',
        'speed_variance': 5,
        'acceleration_range': (-6, 6),
        'harsh_brake_probability': 0.02,
        'lane_change_probability': 0.003,
        'speed_limit_adherence': 0.80,
        'sign_ignore_rate': 0.20,
        'congestion_patience': 0.7,
        'risk_level': 0.4
    },
    'aggressive': {
        'name_ar': 'متهور',
        'speed_variance': 8,
        'acceleration_range': (-12, 12),
        'harsh_brake_probability': 0.08,
        'lane_change_probability': 0.008,
        'speed_limit_adherence': 0.60,
        'sign_ignore_rate': 0.40,
        'congestion_patience': 0.4,
        'risk_level': 0.8
    },
    'distracted': {
        'name_ar': 'مشتت',
        'speed_variance': 10,
        'acceleration_range': (-10, 8),
        'harsh_brake_probability': 0.06,
        'lane_change_probability': 0.012,
        'speed_limit_adherence': 0.70,
        'sign_ignore_rate': 0.70,
        'congestion_patience': 0.5,
        'risk_level': 0.7
    }
}

# ============================================================================
# 2. ROAD TYPES - Define road environment characteristics
# ============================================================================

ROAD_TYPES = {
    'highway': {
        'name_ar': 'طريق سريع',
        'speed_limit': 120,
        'sign_density': 2,
        'base_congestion': 0.2,
        'avg_road_curvature': 0.05,
        'accident_risk_base': 0.15
    },
    'main_road': {
        'name_ar': 'طريق رئيسي',
        'speed_limit': 80,
        'sign_density': 5,
        'base_congestion': 0.4,
        'avg_road_curvature': 0.15,
        'accident_risk_base': 0.25
    },
    'city_street': {
        'name_ar': 'شارع داخلي',
        'speed_limit': 60,
        'sign_density': 8,
        'base_congestion': 0.6,
        'avg_road_curvature': 0.30,
        'accident_risk_base': 0.35
    },
    'residential': {
        'name_ar': 'حي سكني',
        'speed_limit': 40,
        'sign_density': 12,
        'base_congestion': 0.3,
        'avg_road_curvature': 0.25,
        'accident_risk_base': 0.20
    }
}

# ============================================================================
# 3. TIME OF DAY FACTORS - Model traffic patterns
# ============================================================================

TIME_OF_DAY_FACTORS = {
    'morning_rush': {
        'name_ar': 'ساعة الذروة الصباحية',
        'congestion_multiplier': 1.8,
        'hours': (6, 9),
        'accident_risk_multiplier': 1.3
    },
    'midday': {
        'name_ar': 'منتصف النهار',
        'congestion_multiplier': 1.0,
        'hours': (9, 15),
        'accident_risk_multiplier': 0.8
    },
    'evening_rush': {
        'name_ar': 'ساعة الذروة المسائية',
        'congestion_multiplier': 2.0,
        'hours': (15, 19),
        'accident_risk_multiplier': 1.5
    },
    'night': {
        'name_ar': 'الليل',
        'congestion_multiplier': 0.5,
        'hours': (19, 24),
        'accident_risk_multiplier': 1.2
    },
    'late_night': {
        'name_ar': 'منتصف الليل',
        'congestion_multiplier': 0.3,
        'hours': (0, 6),
        'accident_risk_multiplier': 1.4
    }
}

# ============================================================================
# 4. WEATHER CONDITIONS
# ============================================================================

WEATHER_CONDITIONS = {
    'clear': {'name_ar': 'صافي', 'visibility': 100, 'risk_multiplier': 1.0},
    'light_rain': {'name_ar': 'أمطار خفيفة', 'visibility': 70, 'risk_multiplier': 1.3},
    'heavy_rain': {'name_ar': 'أمطار غزيرة', 'visibility': 40, 'risk_multiplier': 1.6},
    'sandstorm': {'name_ar': 'عاصفة رملية', 'visibility': 20, 'risk_multiplier': 2.0},
    'fog': {'name_ar': 'ضباب', 'visibility': 30, 'risk_multiplier': 1.8}
}

# ============================================================================
# 5. TRIP GENERATOR - Generate synthetic driving telemetry
# ============================================================================

class TripGenerator:
    """
    Generates realistic, second-by-second telemetry for a single trip.
    
    Args:
        driver_type: One of ['safe', 'moderate', 'aggressive', 'distracted']
        road_type: One of ['highway', 'main_road', 'city_street', 'residential']
        time_of_day: One of the time period keys
        weather: Weather condition key
        trip_duration_minutes: Duration in minutes (random if None)
    """
    
    def __init__(self, driver_type: str, road_type: str, time_of_day: str,
                 weather: str = 'clear', trip_duration_minutes: Optional[int] = None):
        
        self.driver_type = driver_type
        self.driver_profile = DRIVER_PROFILES[driver_type]
        self.road_type = road_type
        self.road_context = ROAD_TYPES[road_type]
        self.time_of_day = time_of_day
        self.time_factor = TIME_OF_DAY_FACTORS[time_of_day]
        self.weather = weather
        self.weather_data = WEATHER_CONDITIONS[weather]
        
        # Trip metadata
        if trip_duration_minutes is None:
            self.trip_duration = random.randint(5, 60)
        else:
            self.trip_duration = trip_duration_minutes
            
        self.trip_id = str(uuid.uuid4())[:8]
        self.driver_id = str(uuid.uuid4())[:8]
        self.timestamp = datetime.now()
    
    def calculate_dynamic_congestion(self) -> float:
        """Calculate realistic congestion level (0-1 scale)."""
        base = self.road_context['base_congestion']
        multiplier = self.time_factor['congestion_multiplier']
        
        # Add randomness with autocorrelation for realism
        congestion = base * multiplier * random.uniform(0.8, 1.2)
        return min(max(congestion, 0), 1)
    
    def generate_speed_sequence(self, num_seconds: int) -> np.ndarray:
        """
        Generate realistic speed progression over time.
        Accounts for acceleration, congestion, driver behavior.
        """
        speed_limit = self.road_context['speed_limit']
        adherence = self.driver_profile['speed_limit_adherence']
        variance = self.driver_profile['speed_variance']
        
        # Target speed based on driver type and speed limit
        target_speed = speed_limit * adherence + random.uniform(-10, 15)
        target_speed = max(min(target_speed, speed_limit * 1.3), 10)
        
        speeds = np.zeros(num_seconds)
        speeds[0] = 0  # Start from rest
        
        # PHASE 1: Acceleration phase (0-30 seconds)
        accel_time = min(30, num_seconds // 4)
        for i in range(1, accel_time):
            accel = random.uniform(2, 8)
            speeds[i] = min(speeds[i-1] + accel, target_speed)
        
        # PHASE 2: Main driving phase
        congestion_history = []
        for i in range(accel_time, num_seconds - 20):
            congestion = self.calculate_dynamic_congestion()
            congestion_history.append(congestion)
            
            # Congestion reduces target speed
            congestion_penalty = (congestion * 30 * 
                                (1 - self.driver_profile['congestion_patience']))
            adjusted_target = max(target_speed - congestion_penalty, 20)
            
            # Apply speed drift with noise
            noise = np.random.normal(0, variance)
            drift = (adjusted_target - speeds[i-1]) * 0.1
            
            new_speed = speeds[i-1] + noise + drift
            speeds[i] = max(min(new_speed, speed_limit * 1.3), 0)
        
        # PHASE 3: Deceleration phase (last 20 seconds)
        if num_seconds > 20:
            for i in range(num_seconds - 20, num_seconds):
                decel = random.uniform(1, 4)
                speeds[i] = max(speeds[i-1] - decel, 0)
        
        return speeds
    
    def detect_harsh_events(self, speeds: np.ndarray) -> Tuple[List[int], List[int]]:
        """Detect harsh braking and acceleration events."""
        accelerations = np.diff(speeds)
        
        harsh_brakes = []
        harsh_accels = []
        
        # Detect harsh braking: deceleration > 10 km/h per second
        for i, accel in enumerate(accelerations):
            if accel < -10:
                harsh_brakes.append(i + 1)
            elif accel > 12:
                harsh_accels.append(i + 1)
        
        # Add probabilistic harsh brakes based on driver profile
        prob = self.driver_profile['harsh_brake_probability']
        for i in range(30, len(speeds) - 30):
            if random.random() < prob:
                harsh_brakes.append(i)
                speeds[i] = max(speeds[i] - random.uniform(15, 25), 0)
        
        return harsh_brakes, harsh_accels
    
    def generate_lane_changes(self, num_seconds: int) -> List[int]:
        """Generate lane change events."""
        lane_changes = []
        prob = self.driver_profile['lane_change_probability']
        
        for i in range(num_seconds):
            if random.random() < prob:
                lane_changes.append(i)
        
        return lane_changes
    
    def generate_trip(self) -> pd.DataFrame:
        """Generate complete trip telemetry data."""
        num_seconds = self.trip_duration * 60
        
        # Generate core telemetry
        speeds = self.generate_speed_sequence(num_seconds)
        accelerations = np.diff(speeds, prepend=0)
        harsh_brakes, harsh_accels = self.detect_harsh_events(speeds)
        lane_changes = self.generate_lane_changes(num_seconds)
        
        # Generate congestion for each second
        base_congestion = self.calculate_dynamic_congestion()
        congestions = np.random.normal(base_congestion, 0.1, num_seconds)
        congestions = np.clip(congestions, 0, 1)
        
        # Build dataframe
        data = {
            'trip_id': [self.trip_id] * num_seconds,
            'driver_id': [self.driver_id] * num_seconds,
            'second': range(num_seconds),
            'speed_kmh': speeds,
            'acceleration_kmh2': accelerations,
            'harsh_brake': [1 if i in harsh_brakes else 0 for i in range(num_seconds)],
            'harsh_accel': [1 if i in harsh_accels else 0 for i in range(num_seconds)],
            'lane_change': [1 if i in lane_changes else 0 for i in range(num_seconds)],
            'congestion_level': congestions,
            'speed_limit': [self.road_context['speed_limit']] * num_seconds,
            'sign_density': [self.road_context['sign_density']] * num_seconds,
            'road_curvature': [self.road_context['avg_road_curvature']] * num_seconds,
            'road_type': [self.road_type] * num_seconds,
            'driver_type': [self.driver_type] * num_seconds,
            'time_of_day': [self.time_of_day] * num_seconds,
            'weather': [self.weather] * num_seconds,
            'visibility': [self.weather_data['visibility']] * num_seconds,
        }
        
        df = pd.DataFrame(data)
        df['timestamp'] = [self.timestamp + timedelta(seconds=i) for i in range(num_seconds)]
        
        return df


# ============================================================================
# 6. TRIP SCORER - Calculate safe driving score
# ============================================================================

class TripScorer:
    """Calculate safe driving score and extract features for ML."""
    
    @staticmethod
    def calculate_safe_driving_score(trip_df: pd.DataFrame) -> Dict:
        """
        Calculate comprehensive safe driving score (0-100).
        Returns dictionary with score, category, and detailed metrics.
        """
        
        # Extract metrics
        total_time = len(trip_df)
        avg_speed = trip_df['speed_kmh'].mean()
        max_speed = trip_df['speed_kmh'].max()
        speed_limit = trip_df['speed_limit'].iloc[0]
        
        harsh_brakes = trip_df['harsh_brake'].sum()
        harsh_accels = trip_df['harsh_accel'].sum()
        lane_changes = trip_df['lane_change'].sum()
        
        # Calculate speeding percentage
        speeding_time = (trip_df['speed_kmh'] > speed_limit).sum()
        speeding_pct = (speeding_time / total_time) * 100
        
        # Calculate average conditions
        avg_congestion = trip_df['congestion_level'].mean()
        avg_visibility = trip_df['visibility'].mean()
        
        # SCORING FORMULA
        score = 100.0
        score -= harsh_brakes * 3.0
        score -= harsh_accels * 1.5
        score -= lane_changes * 0.5
        score -= speeding_pct * 0.8
        score -= (max_speed - speed_limit) * 0.3 if max_speed > speed_limit else 0
        
        # Bonus for driving in difficult conditions
        score += avg_congestion * 5
        if avg_visibility < 70:  # Poor visibility
            score += 3  # Bonus for careful driving in fog/rain
        
        # Normalize to 0-100
        score = max(min(score, 100), 0)
        
        # Classify driver
        if score >= 80:
            category = 'safe'
            category_ar = 'آمن'
            recommendation = 'ممتاز! استمر على هذا الأداء'
        elif score >= 50:
            category = 'moderate'
            category_ar = 'معتدل'
            recommendation = 'جيد، لكن يمكن تحسين القيادة بتقليل الفرملة الحادة'
        else:
            category = 'risky'
            category_ar = 'خطر'
            recommendation = 'يجب تحسين أسلوب القيادة فوراً - تجنب السرعة الزائدة والفرملة الحادة'
        
        return {
            'trip_id': trip_df['trip_id'].iloc[0],
            'driver_id': trip_df['driver_id'].iloc[0],
            'timestamp': trip_df['timestamp'].iloc[0],
            'safe_driving_score': round(score, 2),
            'driver_category': category,
            'driver_category_ar': category_ar,
            'trip_duration_minutes': round(total_time / 60, 2),
            'avg_speed': round(avg_speed, 2),
            'max_speed': round(max_speed, 2),
            'harsh_brakes_count': int(harsh_brakes),
            'harsh_accels_count': int(harsh_accels),
            'lane_changes_count': int(lane_changes),
            'speeding_percentage': round(speeding_pct, 2),
            'avg_congestion': round(avg_congestion, 3),
            'avg_visibility': round(avg_visibility, 1),
            'road_type': trip_df['road_type'].iloc[0],
            'actual_driver_type': trip_df['driver_type'].iloc[0],
            'time_of_day': trip_df['time_of_day'].iloc[0],
            'weather': trip_df['weather'].iloc[0],
            'recommendation': recommendation,
            'recommendation_ar': recommendation
        }


# ============================================================================
# 7. DATASET GENERATOR - Generate complete synthetic dataset
# ============================================================================

class DatasetGenerator:
    """Generate complete dataset with multiple trips."""
    
    def __init__(self, num_trips: int = 200):
        self.num_trips = num_trips
        self.all_trips_telemetry = []
        self.all_trips_summary = []
    
    def generate_dataset(self):
        """Generate the complete synthetic dataset."""
        print("\n" + "="*70)
        print("🇸🇦 Safe Driving Data Generator - Saudi Arabia")
        print("="*70)
        print(f"🚗 Generating {self.num_trips} synthetic trips...")
        print("="*70)
        
        driver_types = list(DRIVER_PROFILES.keys())
        road_types = list(ROAD_TYPES.keys())
        times_of_day = list(TIME_OF_DAY_FACTORS.keys())
        weather_conditions = list(WEATHER_CONDITIONS.keys())
        
        for i in range(self.num_trips):
            # Random selections
            driver_type = random.choice(driver_types)
            road_type = random.choice(road_types)
            time_of_day = random.choice(times_of_day)
            weather = random.choice(weather_conditions)
            
            # Generate trip
            trip_gen = TripGenerator(
                driver_type=driver_type,
                road_type=road_type,
                time_of_day=time_of_day,
                weather=weather
            )
            
            trip_df = trip_gen.generate_trip()
            
            # Calculate score
            trip_summary = TripScorer.calculate_safe_driving_score(trip_df)
            
            # Store data
            self.all_trips_telemetry.append(trip_df)
            self.all_trips_summary.append(trip_summary)
            
            if (i + 1) % 50 == 0:
                print(f"   ✓ Generated {i + 1}/{self.num_trips} trips")
        
        print("="*70)
        print("✅ Dataset generation completed successfully!")
    
    def save_to_csv(self, output_dir: Optional[str] = None) -> Tuple[str, str]:
        """
        Save telemetry and summary data to CSV files.
        
        Args:
            output_dir: Directory to save files (default: current directory)
            
        Returns:
            Tuple of (telemetry_path, summary_path)
        """
        if output_dir is None:
            output_dir = os.getcwd()
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Save detailed telemetry (second-by-second)
        full_telemetry = pd.concat(self.all_trips_telemetry, ignore_index=True)
        telemetry_path = os.path.join(output_dir, 'telemetry_data.csv')
        full_telemetry.to_csv(telemetry_path, index=False, encoding='utf-8-sig')
        print(f"\n💾 Saved: telemetry_data.csv")
        print(f"   Rows: {len(full_telemetry):,}")
        
        # 2. Save trip summaries (one row per trip)
        summary_df = pd.DataFrame(self.all_trips_summary)
        summary_path = os.path.join(output_dir, 'trip_summary.csv')
        summary_df.to_csv(summary_path, index=False, encoding='utf-8-sig')
        print(f"💾 Saved: trip_summary.csv")
        print(f"   Rows: {len(summary_df)}")
        
        return telemetry_path, summary_path
    
    def print_statistics(self):
        """Print dataset statistics."""
        summary_df = pd.DataFrame(self.all_trips_summary)
        
        print("\n" + "="*70)
        print("📊 Dataset Statistics")
        print("="*70)
        
        print("\n👥 Driver Type Distribution:")
        print(summary_df['actual_driver_type'].value_counts())
        
        print("\n🏆 Driver Category Distribution (by score):")
        print(summary_df['driver_category'].value_counts())
        
        print("\n📈 Safe Driving Score Statistics:")
        print(f"   Mean: {summary_df['safe_driving_score'].mean():.2f}")
        print(f"   Min: {summary_df['safe_driving_score'].min():.2f}")
        print(f"   Max: {summary_df['safe_driving_score'].max():.2f}")
        print(f"   Std Dev: {summary_df['safe_driving_score'].std():.2f}")
        
        print("\n🛣️  Road Type Distribution:")
        print(summary_df['road_type'].value_counts())
        
        print("\n⏰ Time of Day Distribution:")
        print(summary_df['time_of_day'].value_counts())
        
        print("\n🌤️  Weather Distribution:")
        print(summary_df['weather'].value_counts())
        
        print("\n" + "="*70)


# ============================================================================
# 8. MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Configuration
    NUM_TRIPS = 200  # Change this to generate more/fewer trips
    OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Generate dataset
    generator = DatasetGenerator(num_trips=NUM_TRIPS)
    generator.generate_dataset()
    
    # Save files
    telemetry_file, summary_file = generator.save_to_csv(output_dir=OUTPUT_DIR)
    
    # Print statistics
    generator.print_statistics()
    
    print("\n✅ Complete! Data is ready for ML model training")
    print(f"\n📁 Generated Files:")
    print(f"   1. trip_summary.csv - For direct model training")
    print(f"   2. telemetry_data.csv - For detailed analysis")
    print("\n💡 Next Steps:")
    print("   1. Load trip_summary.csv in your ML pipeline")
    print("   2. Extract features for training")
    print("   3. Train classifier (Random Forest / XGBoost)")
    print("="*70 + "\n")
