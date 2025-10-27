# Deploy to Render - Quick Guide

## Step 1: Create Render Account
1. Go to: https://render.com
2. Sign up with GitHub (recommended)
3. Connect your GitHub account

## Step 2: Deploy
1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `Sirfaviaz/med`
3. Configure:
   - **Name**: `medical-tracker`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   
4. **Environment Variables** (click "Advanced"):
   - `SECRET_KEY` - Click "Generate" (Render will create it)
   - `FLASK_ENV` - Set to `production`
   
5. Click **"Create Web Service"**

## Step 3: Wait for Deployment
- Render will build and deploy your app
- Takes 3-5 minutes
- You'll see the build logs in real-time

## Step 4: Access Your App
- Render will give you a URL like: `medical-tracker.onrender.com`
- Your app will be live!

## Step 5: Configure Database (Optional)
Render provides PostgreSQL for free:
1. Click **"New +"** → **"PostgreSQL"**
2. Connect it to your web service
3. Update `DATABASE_URL` in environment variables

## Important Notes
- Free tier has cold starts (30 second delay if inactive for 15+ min)
- Storage is ephemeral (uploads will be lost on restart)
- Consider using Render's disk for persistent storage

