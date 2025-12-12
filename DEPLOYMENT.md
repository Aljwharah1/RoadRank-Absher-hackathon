# Deploying RoadRank to Render

## Prerequisites
- GitHub account with your repository pushed
- Render account (free tier available at https://render.com)

## Step-by-Step Deployment Guide

### 1. Create a Render Account
- Go to https://render.com
- Sign up with your GitHub account

### 2. Create a New Web Service
1. Click **"New +"** → **"Web Service"**
2. Select **"Build and deploy from a Git repository"**
3. Connect your GitHub account if you haven't already
4. Select the **`RoadRank-Absher-hackathon`** repository

### 3. Configure the Service
Fill in the following settings:

| Field | Value |
|-------|-------|
| **Name** | `roadrank` (or any name you prefer) |
| **Environment** | `Python 3` |
| **Region** | Choose your closest region |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |

### 4. Environment Variables (Optional)
You can add environment variables if needed later via the Dashboard:
- Click **"Environment"** tab
- Add any custom variables your app needs

### 5. Deploy
1. Click **"Create Web Service"**
2. Render will automatically build and deploy your app
3. Watch the deployment logs to ensure it succeeds
4. Once deployed, you'll get a URL like: `https://roadrank.onrender.com`

### 6. Test Your Deployment
After deployment completes:

```bash
# Test the API health endpoint
curl https://roadrank.onrender.com/health

# View interactive API docs
https://roadrank.onrender.com/docs

# View API schema
https://roadrank.onrender.com/openapi.json
```

### 7. Update Your Frontend
Update your frontend's API base URL in `frontend/HDI.html`:

**Before (localhost):**
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

**After (Render):**
```javascript
const API_BASE_URL = 'https://roadrank.onrender.com';
```

Then redeploy the frontend or host it on Render as well.

---

## Hosting the Frontend on Render (Optional)

You can also deploy your frontend as a static site on Render:

### Option A: Deploy HTML as Static Site

1. Create a `public/` folder and copy `HDI.html` there:
   ```bash
   mkdir public
   cp frontend/HDI.html public/index.html
   ```

2. In Render Dashboard → Create new **"Static Site"**
3. Connect the same repository
4. Set **"Publish directory"** to `public`
5. Deploy

### Option B: Use a Simple Web Server for Frontend
Create a separate Render Web Service for the frontend using Python's http.server or serve the static files from your FastAPI backend.

---

## Important Notes

⚠️ **Free Tier Limitations:**
- Services spin down after 15 minutes of inactivity
- First request after spin-down may be slow (~30 seconds)
- Render provides 750 free instance hours per month
- Upgrade to paid plan for always-on service

📁 **File Structure for Deployment:**
```
RoadRank-Absher-hackathon/
├── requirements.txt        ← Needed by Render
├── Procfile               ← Optional but recommended
├── render.yaml            ← Alternative config file
├── runtime.txt            ← Specifies Python version
├── backend/
│   └── main.py
├── Model/
│   ├── xgboost_model.joblib
│   └── encoders.joblib
├── data/
│   └── Trip Summary.xlsx
└── frontend/
    └── HDI.html
```

---

## Troubleshooting

### Build Fails
- Check `requirements.txt` has all dependencies
- Ensure Python version is 3.10+
- Look at build logs in Render dashboard

### 502 Bad Gateway Error
- Wait 30 seconds if it's the first request (cold start)
- Check backend logs in Render dashboard
- Verify API endpoints are working with `/health`

### Model Files Not Loading
- Ensure `Model/` directory is in the repository
- Check file paths are relative and work from the root directory
- Verify joblib files aren't corrupted

### CORS Errors
- Your backend has CORS enabled for all origins (`allow_origins=["*"]`)
- Should work with any frontend URL

---

## Next Steps

1. Commit these deployment files:
   ```bash
   git add requirements.txt Procfile render.yaml runtime.txt DEPLOYMENT.md
   git commit -m "Add Render deployment configuration"
   git push
   ```

2. Deploy on Render following the steps above

3. Share your deployment URL!

---

For more help, visit:
- Render Docs: https://render.com/docs
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/
