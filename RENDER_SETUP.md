# Render Setup Instructions - FIXED VERSION

## Your Render Dashboard Settings

Go to your Render service → **Settings**

### 1. Build Command
```
pip install -r requirements.txt
```

### 2. Start Command
```
gunicorn --config gunicorn_config.py app:app
```

### 3. Environment Variables (Click "Environment")

Add these two variables:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | `your-random-secret-key-here` |

**To create a secret key:**
1. Go to: https://randomkeygen.com/
2. Copy any 32+ character string
3. Paste as `SECRET_KEY` value

### 4. Deploy

Click **"Manual Deploy"** → **"Deploy latest commit"**

Wait 3-5 minutes for deployment to complete.

---

## Test Your App

After deployment completes:

1. Open your Render URL (e.g., `medical-tracker.onrender.com`)
2. Click **"Register"**
3. Create a patient account
4. Create a doctor account
5. Test the features!

---

## Troubleshooting

### Still can't register users?

Check Render logs:
1. Go to Render Dashboard
2. Click on your service
3. Click **"Logs"** tab
4. Look for any error messages
5. Share the error with me

### Common Issues

**"Module not found"**
- Check that `requirements.txt` has all dependencies
- Wait for build to complete

**"Database error"**
- Database is created automatically
- Check logs for SQL errors

**"Permission denied"**
- Check SECRET_KEY is set
- Check FLASK_ENV is set to `production`

---

## Your App URL

After deployment, you'll have a URL like:
- `https://medical-tracker.onrender.com`

Access it and test registration!

