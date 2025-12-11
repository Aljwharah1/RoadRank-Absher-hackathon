#!/bin/bash
# RoadRank Project Setup & Execution Script
# استخدم: bash run_project.sh

set -e  # توقف عند أي خطأ

echo "🇸🇦 RoadRank - Safe Driving AI System"
echo "======================================"
echo ""

# الألوان
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. تفعيل البيئة
echo -e "${BLUE}Step 1: Activating Python Environment${NC}"
if [ -d "new" ]; then
    source new/bin/activate
    echo -e "${GREEN}✅ Environment activated${NC}"
else
    echo -e "${YELLOW}⚠️  Environment 'new' not found. Creating...${NC}"
    python3 -m venv new
    source new/bin/activate
    echo -e "${GREEN}✅ Environment created and activated${NC}"
fi
echo ""

# 2. تثبيت المكتبات
echo -e "${BLUE}Step 2: Installing Dependencies${NC}"
pip install -r requirements.txt -q
echo -e "${GREEN}✅ All packages installed${NC}"
echo ""

# 3. توليد البيانات
echo -e "${BLUE}Step 3: Generating Synthetic Data${NC}"
if [ -f "trip_summary.csv" ] && [ -f "telemetry_data.csv" ]; then
    echo -e "${YELLOW}Data files already exist. Skipping generation...${NC}"
else
    python data_generator_v2.py
    echo -e "${GREEN}✅ Data generated${NC}"
fi
echo ""

# 4. معالجة البيانات
echo -e "${BLUE}Step 4: Processing Data & Feature Engineering${NC}"
echo -e "${YELLOW}Open this file to run:${NC}"
echo "  jupyter notebook 01_data_exploration_and_features.ipynb"
echo ""

# 5. تدريب النموذج
echo -e "${BLUE}Step 5: Training ML Models${NC}"
if [ -f "X_train.csv" ] && [ -f "y_train.csv" ]; then
    python 02_model_training.py
    echo -e "${GREEN}✅ Models trained${NC}"
else
    echo -e "${YELLOW}⚠️  Training data not found. Please run the Jupyter notebook first.${NC}"
fi
echo ""

# 6. الملخص
echo -e "${GREEN}======================================"
echo "✅ Project Setup Complete!"
echo "======================================"
echo -e "Generated Files:${NC}"
echo "  1. telemetry_data.csv - Full telemetry (100K+ rows)"
echo "  2. trip_summary.csv - Trip summaries (200 rows)"
echo "  3. processed_data_with_features.csv - Processed data"
echo "  4. X_train.csv, X_test.csv - Training features"
echo "  5. y_train.csv, y_test.csv - Training labels"
echo "  6. safe_driving_model_*.pkl - Trained models"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "  - GUIDE.md - شرح شامل"
echo "  - PROJECT_SUMMARY.md - ملخص المشروع"
echo ""
echo -e "${YELLOW}💡 Next Steps:${NC}"
echo "  1. Review generated data"
echo "  2. Check model metrics"
echo "  3. Build FastAPI backend"
echo "  4. Create React frontend"
echo ""
