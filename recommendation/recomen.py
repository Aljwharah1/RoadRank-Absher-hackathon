

import pandas as pd
import os

class RecommendationEngine:
    """محرك التوصيات"""
    
    def __init__(self, accidents_path=None):
        """تحميل بيانات الحوادث"""
        
        self.has_accident_data = False
        
        if accidents_path and os.path.exists(accidents_path):
            try:
                self.accidents_df = pd.read_excel(accidents_path)
                self.speeding_accidents = int(self.accidents_df['السرعة الزائدة'].sum())
                self.signal_accidents = int(self.accidents_df['عدم التقيد بالاشارة'].sum())
                self.overtaking_accidents = int(self.accidents_df['تجاوز غير نظامى'].sum())
                self.night_accidents = int(self.accidents_df['ليلا'].sum())
                self.day_accidents = int(self.accidents_df['نهارا'].sum())
                self.has_accident_data = True
            except Exception as e:
                pass
        
        if not self.has_accident_data:
            self.speeding_accidents = 109578
            self.signal_accidents = 83241
            self.overtaking_accidents = 34000
            self.night_accidents = 201702
            self.day_accidents = 25117
    
    def generate_recommendations(self, trip_data, include_basic=True):
        """
        توليد التوصيات
        
        المدخلات:
        ---------
        trip_data : dict
            بيانات الرحلة
        
        المخرجات:
        ---------
        dict يحتوي على:
            - safe_driving_score: المؤشر
            - risk_category: الفئة (آمن/متوسط/خطر)
            - detailed_recommendations: قائمة التوصيات
            - total_issues: عدد المشاكل الحرجة
        """
        
        score = trip_data.get('safe_driving_score', 0)
        recommendations = []
        
        # السرعة الزائدة
        speeding_pct = trip_data.get('speeding_percentage', 0)
        
        if speeding_pct > 20:
            total = self.speeding_accidents + self.signal_accidents + self.overtaking_accidents
            speeding_ratio = (self.speeding_accidents / total) * 100
            
            recommendations.append({
                'priority': 'critical' if speeding_pct > 40 else 'high',
                'category': 'speeding',
                'title': 'تحذير: السرعة الزائدة',
                'message': f"تجاوزت السرعة المحددة في {speeding_pct:.0f}% من الرحلة. البيانات تشير إلى أن السرعة الزائدة من أكثر أسباب الحوادث شيوعاً.",
                'tips': [
                    'استخدم مثبت السرعة',
                    'التزم بالسرعة المحددة',
                    'راقب لوحات السرعة'
                ]
            })
        
        # الفرملة الحادة
        harsh_brakes = trip_data.get('harsh_brakes_count', 0)
        
        if harsh_brakes > 5:
            recommendations.append({
                'priority': 'critical' if harsh_brakes > 10 else 'high',
                'category': 'braking',
                'title': 'فرملة مفاجئة متكررة',
                'message': f"سجلت {harsh_brakes} فرملة مفاجئة. هذا يزيد احتمالية التصادم الخلفي.",
                'tips': [
                    'احتفظ بمسافة 3 ثوانٍ من السيارة أمامك',
                    'راقب حركة المرور مبكراً',
                    'تجنب القيادة بسرعة في الازدحام'
                ]
            })
        
        # القيادة الليلية
        time_of_day = trip_data.get('time_of_day', '')
        
        if time_of_day in ['night', 'late_night']:
            total_time = self.night_accidents + self.day_accidents
            night_ratio = (self.night_accidents / total_time) * 100
            
            recommendations.append({
                'priority': 'high',
                'category': 'night_driving',
                'title': 'تنبيه: القيادة الليلية',
                'message': f"أنت تقود ليلاً. البيانات تشير إلى أن نسبة كبيرة من الحوادث تحدث ليلاً رغم قلة الحركة المرورية.",
                'tips': [
                    'تأكد من نظافة الزجاج والإضاءة',
                    'خفف السرعة بنسبة 10-15%',
                    'خذ استراحة كل ساعتين'
                ]
            })
        
        # تغيير المسار
        lane_changes = trip_data.get('lane_changes_count', 0)
        
        if lane_changes > 15:
            total = self.speeding_accidents + self.signal_accidents + self.overtaking_accidents
            overtaking_ratio = (self.overtaking_accidents / total) * 100
            
            recommendations.append({
                'priority': 'medium',
                'category': 'lane_changes',
                'title': 'تغيير مسار متكرر',
                'message': f"غيرت المسار {lane_changes} مرة خلال الرحلة. التغيير المتكرر للمسار يزيد من احتمالية الحوادث.",
                'tips': [
                    'خطط مسارك مسبقاً',
                    'تحقق من النقطة العمياء',
                    'استخدم الإشارة قبل 3 ثوانٍ'
                ]
            })
        
        # المناطق السكنية
        road_type = trip_data.get('road_type', '')
        avg_speed = trip_data.get('avg_speed', 0)
        
        if road_type == 'residential' and avg_speed > 50:
            recommendations.append({
                'priority': 'high',
                'category': 'residential',
                'title': 'منطقة سكنية - خفف السرعة',
                'message': f"سرعتك {avg_speed:.0f} كم/س في منطقة سكنية. السرعة المثالية 40-50 كم/س.",
                'tips': [
                    'راقب الأطفال والمشاة',
                    'انتبه للسيارات المتوقفة',
                    'خفف السرعة فوراً'
                ]
            })
        
        # توصية إيجابية
        if score >= 80 and harsh_brakes < 3:
            recommendations.append({
                'priority': 'positive',
                'category': 'achievement',
                'title': 'أداء ممتاز!',
                'message': f"رحلة آمنة بمؤشر {score:.0f}/100! استمر على هذا المنوال.",
                'tips': [
                    'أنت قدوة للآخرين',
                    'قد تكون مؤهلاً لخصم تأميني',
                    'شارك إنجازك'
                ]
            })
        
        # ترتيب حسب الأولوية
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'positive': 3}
        recommendations.sort(key=lambda x: priority_order[x['priority']])
        
        # النتيجة النهائية
        result = {
            'safe_driving_score': score,
            'risk_category': self._get_category(score),
            'detailed_recommendations': recommendations,
            'total_issues': len([r for r in recommendations if r['priority'] in ['critical', 'high']])
        }
        
        if include_basic and 'recommendation_ar' in trip_data:
            result['basic_recommendation'] = trip_data['recommendation_ar']
        
        return result
    
    def _get_category(self, score):
        """تصنيف السائق"""
        if score >= 80:
            return 'آمن'
        elif score >= 50:
            return 'متوسط'
        else:
            return 'خطر'


# مثال الاستخدام (اختياري - يمكن حذفه)
if __name__ == "__main__":
    
    # المسار لملف الحوادث
    accidents_file = '/Users/aljawharah/RoadRank-Absher-hackathon/recomedon/Traffic Accident Statistics .xlsx'
    
    # إنشاء المحرك
    engine = RecommendationEngine(accidents_path=accidents_file)
    
    # بيانات رحلة تجريبية
    trip_data = {
        'safe_driving_score': 45.5,
        'avg_speed': 85.0,
        'harsh_brakes_count': 12,
        'lane_changes_count': 18,
        'speeding_percentage': 45.0,
        'road_type': 'highway',
        'time_of_day': 'night'
    }
    
    # توليد التوصيات
    result = engine.generate_recommendations(trip_data)
    
    # عرض النتائج
    print("=" * 70)
    print(f"المؤشر: {result['safe_driving_score']:.1f}/100")
    print(f"الفئة: {result['risk_category']}")
    print(f"عدد المشاكل الحرجة: {result['total_issues']}")
    print(f"\nالتوصيات ({len(result['detailed_recommendations'])}):")
    print("=" * 70)
    
    priority_icons = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'positive': '🟢'
    }
    
    for i, rec in enumerate(result['detailed_recommendations'], 1):
        icon = priority_icons[rec['priority']]
        print(f"\n{i}. {icon} {rec['title']}")
        print(f"   {rec['message']}")
        print(f"   نصائح:")
        for tip in rec['tips']:
            print(f"   • {tip}")
    
    print("\n" + "=" * 70)