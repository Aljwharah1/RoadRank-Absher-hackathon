"""
مولد بيانات القيادة الآمنة - السعودية
يولد بيانات واقعية لتدريب نموذج الذكاء الاصطناعي
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple
import uuid
import warnings
warnings.filterwarnings('ignore')

# ============================
# 1. إعدادات أنواع السائقين
# ============================

DRIVER_PROFILES = {
    'آمن': {
        'speed_variance': 2,
        'acceleration_range': (-3, 3),
        'harsh_brake_probability': 0.005,
        'lane_change_probability': 0.001,
        'speed_limit_adherence': 0.95,
        'sign_ignore_rate': 0.05,
        'congestion_patience': 0.9
    },
    'معتدل': {
        'speed_variance': 5,
        'acceleration_range': (-6, 6),
        'harsh_brake_probability': 0.02,
        'lane_change_probability': 0.003,
        'speed_limit_adherence': 0.80,
        'sign_ignore_rate': 0.20,
        'congestion_patience': 0.7
    },
    'متهور': {
        'speed_variance': 8,
        'acceleration_range': (-12, 12),
        'harsh_brake_probability': 0.08,
        'lane_change_probability': 0.008,
        'speed_limit_adherence': 0.60,
        'sign_ignore_rate': 0.40,
        'congestion_patience': 0.4
    },
    'مشتت': {
        'speed_variance': 10,
        'acceleration_range': (-10, 8),
        'harsh_brake_probability': 0.06,
        'lane_change_probability': 0.012,
        'speed_limit_adherence': 0.70,
        'sign_ignore_rate': 0.70,
        'congestion_patience': 0.5
    }
}

# ============================
# 2. إعدادات أنواع الطرق
# ============================

ROAD_TYPES = {
    'طريق سريع': {
        'speed_limit': 120,
        'sign_density': 2,
        'base_congestion': 0.2,
        'english': 'HIGHWAY'
    },
    'طريق رئيسي': {
        'speed_limit': 80,
        'sign_density': 5,
        'base_congestion': 0.4,
        'english': 'MAIN_ROAD'
    },
    'شارع داخلي': {
        'speed_limit': 60,
        'sign_density': 8,
        'base_congestion': 0.6,
        'english': 'CITY_STREET'
    },
    'حي سكني': {
        'speed_limit': 40,
        'sign_density': 12,
        'base_congestion': 0.3,
        'english': 'RESIDENTIAL'
    }
}

# ============================
# 3. إعدادات أوقات اليوم
# ============================

TIME_OF_DAY_FACTORS = {
    'ساعة الذروة الصباحية': {
        'congestion_multiplier': 1.8, 
        'hours': (6, 9),
        'english': 'MORNING_RUSH'
    },
    'منتصف النهار': {
        'congestion_multiplier': 1.0, 
        'hours': (9, 15),
        'english': 'MIDDAY'
    },
    'ساعة الذروة المسائية': {
        'congestion_multiplier': 2.0, 
        'hours': (15, 19),
        'english': 'EVENING_RUSH'
    },
    'الليل': {
        'congestion_multiplier': 0.5, 
        'hours': (19, 24),
        'english': 'NIGHT'
    },
    'منتصف الليل': {
        'congestion_multiplier': 0.3, 
        'hours': (0, 6),
        'english': 'LATE_NIGHT'
    }
}

# ============================
# 4. حالات الطقس
# ============================

WEATHER_CONDITIONS = {
    'صافي': 'CLEAR',
    'أمطار خفيفة': 'LIGHT_RAIN',
    'أمطار غزيرة': 'HEAVY_RAIN',
    'عاصفة رملية': 'SANDSTORM',
    'ضباب': 'FOG'
}

# ============================
# 5. مولد الرحلات
# ============================

class TripGenerator:
    def __init__(self, driver_type: str, road_type: str, time_of_day: str, 
                 weather: str = 'صافي', trip_duration_minutes: int = None):
        self.driver_type_arabic = driver_type
        self.driver_profile = DRIVER_PROFILES[driver_type]
        self.road_type_arabic = road_type
        self.road_context = ROAD_TYPES[road_type]
        self.time_of_day_arabic = time_of_day
        self.weather_arabic = weather
        
        # مدة الرحلة العشوائية بين 5-60 دقيقة
        if trip_duration_minutes is None:
            self.trip_duration = random.randint(5, 60)
        else:
            self.trip_duration = trip_duration_minutes
            
        self.trip_id = str(uuid.uuid4())[:8]
        self.driver_id = str(uuid.uuid4())[:8]
        
    def calculate_congestion_level(self) -> float:
        """حساب مستوى الازدحام الديناميكي"""
        base = self.road_context['base_congestion']
        
        multiplier = TIME_OF_DAY_FACTORS[self.time_of_day_arabic]['congestion_multiplier']
        
        # إضافة عشوائية
        congestion = base * multiplier * random.uniform(0.8, 1.2)
        return min(max(congestion, 0), 1)
    
    def generate_speed_sequence(self, num_seconds: int) -> np.ndarray:
        """توليد تسلسل السرعة الواقعي"""
        speed_limit = self.road_context['speed_limit']
        adherence = self.driver_profile['speed_limit_adherence']
        variance = self.driver_profile['speed_variance']
        
        # السرعة المستهدفة حسب نوع السائق
        target_speed = speed_limit * adherence + random.uniform(-10, 15)
        
        speeds = np.zeros(num_seconds)
        speeds[0] = 0  # البداية من السكون
        
        # مرحلة التسارع (0-30 ثانية)
        accel_time = min(30, num_seconds // 4)
        for i in range(1, accel_time):
            accel = random.uniform(2, 8)
            speeds[i] = min(speeds[i-1] + accel, target_speed)
        
        # مرحلة القيادة الرئيسية
        for i in range(accel_time, num_seconds - 20):
            congestion = self.calculate_congestion_level()
            
            # الازدحام يقلل السرعة
            congestion_penalty = congestion * 30 * (1 - self.driver_profile['congestion_patience'])
            adjusted_target = max(target_speed - congestion_penalty, 20)
            
            # إضافة تشويش والانجراف نحو السرعة المستهدفة
            noise = np.random.normal(0, variance)
            drift = (adjusted_target - speeds[i-1]) * 0.1
            
            new_speed = speeds[i-1] + noise + drift
            speeds[i] = max(min(new_speed, speed_limit * 1.3), 0)
        
        # مرحلة التباطؤ (آخر 20 ثانية)
        if num_seconds > 20:
            for i in range(num_seconds - 20, num_seconds):
                decel = random.uniform(1, 4)
                speeds[i] = max(speeds[i-1] - decel, 0)
        
        return speeds
    
    def detect_harsh_events(self, speeds: np.ndarray) -> Tuple[List[int], List[int]]:
        """كشف أحداث الفرملة والتسارع الحاد"""
        accelerations = np.diff(speeds)
        
        harsh_brakes = []
        harsh_accels = []
        
        # فرملة حادة: تباطؤ > 10 كم/س في الثانية
        for i, accel in enumerate(accelerations):
            if accel < -10:
                harsh_brakes.append(i + 1)
            elif accel > 12:
                harsh_accels.append(i + 1)
        
        # إضافة فرملات حادة احتمالية حسب نوع السائق
        prob = self.driver_profile['harsh_brake_probability']
        for i in range(30, len(speeds) - 30):
            if random.random() < prob:
                harsh_brakes.append(i)
                speeds[i] = max(speeds[i] - random.uniform(15, 25), 0)
        
        return harsh_brakes, harsh_accels
    
    def generate_lane_changes(self, num_seconds: int) -> List[int]:
        """توليد أحداث تغيير المسار"""
        lane_changes = []
        prob = self.driver_profile['lane_change_probability']
        
        for i in range(num_seconds):
            if random.random() < prob:
                lane_changes.append(i)
        
        return lane_changes
    
    def generate_trip(self) -> pd.DataFrame:
        """توليد بيانات الرحلة الكاملة"""
        num_seconds = self.trip_duration * 60
        
        # توليد البيانات الأساسية
        speeds = self.generate_speed_sequence(num_seconds)
        accelerations = np.diff(speeds, prepend=0)
        
        harsh_brakes, harsh_accels = self.detect_harsh_events(speeds)
        lane_changes = self.generate_lane_changes(num_seconds)
        
        # حساب الازدحام لكل ثانية
        base_congestion = self.calculate_congestion_level()
        congestions = np.random.normal(base_congestion, 0.1, num_seconds)
        congestions = np.clip(congestions, 0, 1)
        
        # بناء جدول البيانات
        data = {
            'معرف_الرحلة': [self.trip_id] * num_seconds,
            'معرف_السائق': [self.driver_id] * num_seconds,
            'الثانية': range(num_seconds),
            'السرعة_كم_س': speeds,
            'التسارع_كم_س2': accelerations,
            'فرملة_حادة': [1 if i in harsh_brakes else 0 for i in range(num_seconds)],
            'تسارع_حاد': [1 if i in harsh_accels else 0 for i in range(num_seconds)],
            'تغيير_مسار': [1 if i in lane_changes else 0 for i in range(num_seconds)],
            'مستوى_الازدحام': congestions,
            'حد_السرعة': [self.road_context['speed_limit']] * num_seconds,
            'كثافة_اللوحات': [self.road_context['sign_density']] * num_seconds,
            'نوع_الطريق': [self.road_type_arabic] * num_seconds,
            'نوع_السائق': [self.driver_type_arabic] * num_seconds,
            'وقت_اليوم': [self.time_of_day_arabic] * num_seconds,
            'الطقس': [self.weather_arabic] * num_seconds
        }
        
        df = pd.DataFrame(data)
        return df

# ============================
# 6. حساب مؤشر القيادة الآمنة
# ============================

class TripScorer:
    @staticmethod
    def calculate_safe_driving_score(trip_df: pd.DataFrame) -> Dict:
        """حساب مؤشر القيادة الآمنة والمميزات"""
        
        # استخراج المميزات
        total_time = len(trip_df)
        avg_speed = trip_df['السرعة_كم_س'].mean()
        max_speed = trip_df['السرعة_كم_س'].max()
        speed_limit = trip_df['حد_السرعة'].iloc[0]
        
        harsh_brakes = trip_df['فرملة_حادة'].sum()
        harsh_accels = trip_df['تسارع_حاد'].sum()
        lane_changes = trip_df['تغيير_مسار'].sum()
        
        # حساب نسبة السرعة الزائدة
        speeding_time = (trip_df['السرعة_كم_س'] > speed_limit).sum()
        speeding_pct = (speeding_time / total_time) * 100
        
        # حساب متوسط الازدحام
        avg_congestion = trip_df['مستوى_الازدحام'].mean()
        
        # معادلة حساب النقاط
        score = 100
        score -= harsh_brakes * 3
        score -= harsh_accels * 1.5
        score -= lane_changes * 0.5
        score -= speeding_pct * 0.8
        score -= (max_speed - speed_limit) * 0.3 if max_speed > speed_limit else 0
        
        # مكافأة على القيادة في ظروف صعبة
        score += avg_congestion * 5
        
        # تحديد النقاط بين 0-100
        score = max(min(score, 100), 0)
        
        # تصنيف السائق
        if score >= 80:
            category = 'آمن'
            recommendation = 'ممتاز! استمر على هذا الأداء'
        elif score >= 50:
            category = 'معتدل'
            recommendation = 'جيد، لكن يمكن تحسين القيادة بتقليل الفرملة الحادة'
        else:
            category = 'خطر'
            recommendation = 'يجب تحسين أسلوب القيادة فوراً - تجنب السرعة الزائدة والفرملة الحادة'
        
        return {
            'معرف_الرحلة': trip_df['معرف_الرحلة'].iloc[0],
            'معرف_السائق': trip_df['معرف_السائق'].iloc[0],
            'مؤشر_القيادة_الآمنة': round(score, 2),
            'تصنيف_السائق': category,
            'مدة_الرحلة_دقيقة': round(total_time / 60, 2),
            'متوسط_السرعة': round(avg_speed, 2),
            'أقصى_سرعة': round(max_speed, 2),
            'عدد_الفرملات_الحادة': harsh_brakes,
            'عدد_التسارعات_الحادة': harsh_accels,
            'عدد_تغييرات_المسار': lane_changes,
            'نسبة_السرعة_الزائدة': round(speeding_pct, 2),
            'متوسط_الازدحام': round(avg_congestion, 3),
            'نوع_الطريق': trip_df['نوع_الطريق'].iloc[0],
            'نوع_السائق_الفعلي': trip_df['نوع_السائق'].iloc[0],
            'وقت_اليوم': trip_df['وقت_اليوم'].iloc[0],
            'الطقس': trip_df['الطقس'].iloc[0],
            'التوصية': recommendation
        }

# ============================
# 7. مولد قاعدة البيانات
# ============================

class DatasetGenerator:
    def __init__(self, num_trips: int = 200):
        self.num_trips = num_trips
        self.all_trips_telemetry = []
        self.all_trips_summary = []
    
    def generate_dataset(self):
        """توليد قاعدة البيانات الكاملة مع عدة رحلات"""
        print(f"🚗 جاري توليد {self.num_trips} رحلة صناعية...")
        print("="*60)
        
        driver_types = list(DRIVER_PROFILES.keys())
        road_types = list(ROAD_TYPES.keys())
        times_of_day = list(TIME_OF_DAY_FACTORS.keys())
        weather_conditions = list(WEATHER_CONDITIONS.keys())
        
        for i in range(self.num_trips):
            # اختيارات عشوائية
            driver_type = random.choice(driver_types)
            road_type = random.choice(road_types)
            time_of_day = random.choice(times_of_day)
            weather = random.choice(weather_conditions)
            
            # توليد الرحلة
            trip_gen = TripGenerator(
                driver_type=driver_type,
                road_type=road_type,
                time_of_day=time_of_day,
                weather=weather
            )
            
            trip_df = trip_gen.generate_trip()
            
            # حساب المؤشر
            trip_summary = TripScorer.calculate_safe_driving_score(trip_df)
            
            # حفظ البيانات
            self.all_trips_telemetry.append(trip_df)
            self.all_trips_summary.append(trip_summary)
            
            if (i + 1) % 50 == 0:
                print(f"   ✓ تم توليد {i + 1}/{self.num_trips} رحلة")
        
        print("="*60)
        print("✅ اكتمل توليد البيانات بنجاح!")
    
    def save_to_csv(self, output_dir: str = '/Users/aljawharah/RoadRank-Absher-hackathon'):
        """حفظ البيانات في ملفات CSV"""
        
        # 1. بيانات التيليماتري الكاملة (ثانية بثانية)
        full_telemetry = pd.concat(self.all_trips_telemetry, ignore_index=True)
        telemetry_path = f'{output_dir}/بيانات_التيليماتري_كاملة.csv'
        full_telemetry.to_csv(telemetry_path, index=False, encoding='utf-8-sig')
        print(f"\n💾 تم الحفظ: بيانات_التيليماتري_كاملة.csv")
        print(f"   عدد الصفوف: {len(full_telemetry):,}")
        
        # 2. بيانات ملخص الرحلات (صف واحد لكل رحلة)
        summary_df = pd.DataFrame(self.all_trips_summary)
        summary_path = f'{output_dir}/ملخص_الرحلات.csv'
        summary_df.to_csv(summary_path, index=False, encoding='utf-8-sig')
        print(f"💾 تم الحفظ: ملخص_الرحلات.csv")
        print(f"   عدد الصفوف: {len(summary_df)}")
        
        return telemetry_path, summary_path
    
    def print_statistics(self):
        """طباعة إحصائيات البيانات"""
        summary_df = pd.DataFrame(self.all_trips_summary)
        
        print("\n" + "="*60)
        print("📊 إحصائيات البيانات المولدة")
        print("="*60)
        
        print("\n🎯 توزيع أنواع السائقين:")
        print(summary_df['نوع_السائق_الفعلي'].value_counts())
        
        print("\n🏆 توزيع تصنيفات السائقين (حسب المؤشر):")
        print(summary_df['تصنيف_السائق'].value_counts())
        
        print("\n📈 إحصائيات مؤشر القيادة الآمنة:")
        print(f"   المتوسط: {summary_df['مؤشر_القيادة_الآمنة'].mean():.2f}")
        print(f"   الحد الأدنى: {summary_df['مؤشر_القيادة_الآمنة'].min():.2f}")
        print(f"   الحد الأقصى: {summary_df['مؤشر_القيادة_الآمنة'].max():.2f}")
        
        print("\n🛣️  توزيع أنواع الطرق:")
        print(summary_df['نوع_الطريق'].value_counts())
        
        print("\n⏰ توزيع أوقات اليوم:")
        print(summary_df['وقت_اليوم'].value_counts())
        
        print("\n" + "="*60)

# ============================
# 8. التشغيل الرئيسي
# ============================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🇸🇦 مولد بيانات القيادة الآمنة - المملكة العربية السعودية")
    print("="*60)
    
    # إعدادات التوليد
    NUM_TRIPS = 200  # غيري هذا الرقم لتوليد رحلات أكثر
    
    # توليد البيانات
    generator = DatasetGenerator(num_trips=NUM_TRIPS)
    generator.generate_dataset()
    
    # حفظ الملفات
    telemetry_file, summary_file = generator.save_to_csv()
    
    # طباعة الإحصائيات
    generator.print_statistics()
    
    print("\n✅ اكتمل! البيانات جاهزة لتدريب نموذج الذكاء الاصطناعي")
    print(f"\n📁 الملفات المُنشأة:")
    print(f"   1. ملخص_الرحلات.csv - للتدريب المباشر")
    print(f"   2. بيانات_التيليماتري_كاملة.csv - للتحليل التفصيلي")
    print("\n💡 الخطوة التالية:")
    print("   استخدمي ملف 'ملخص_الرحلات.csv' لتدريب النموذج")
    print("="*60 + "\n")