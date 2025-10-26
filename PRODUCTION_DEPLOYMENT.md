# Production Deployment Guide

## Security Checklist

- ✅ Input validation and sanitization
- ✅ Password strength requirements
- ✅ File upload validation
- ✅ Secure filename handling
- ✅ Error handling and logging
- ✅ SQL injection prevention (using ORM)
- ✅ XSS prevention (sanitized inputs)
- ✅ Environment-based configuration
- ✅ Session security

## Environment Variables

Set these environment variables for production:

### Required
```bash
export SECRET_KEY='your-strong-secret-key-here-min-32-chars'
export FLASK_ENV='production'
```

### Optional
```bash
export DATABASE_URL='sqlite:///medical_app.db'
```

## Deployment Options

### Option 1: Using Gunicorn (Recommended)

1. Install gunicorn:
```bash
pip install gunicorn
```

2. Run the application:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. Run as background service:
```bash
nohup gunicorn -w 4 -b 0.0.0.0:5000 app:app > app.log 2>&1 &
```

### Option 2: Using Waitress (Windows)

The app is configured to use Waitress in production mode:

1. Set environment:
```bash
set FLASK_ENV=production
set SECRET_KEY=your-secret-key
```

2. Run:
```bash
python app.py
```

### Option 3: Using Apache with mod_wsgi

Create `wsgi.py`:
```python
from app import app

if __name__ == "__main__":
    app.run()
```

## Security Recommendations

1. **Change the SECRET_KEY** - Generate a strong random key:
```python
import secrets
print(secrets.token_hex(32))
```

2. **Enable HTTPS** - Use a reverse proxy (nginx/Apache) with SSL certificate

3. **Database** - For production, use PostgreSQL or MySQL instead of SQLite

4. **Rate Limiting** - Consider adding Flask-Limiter:
```bash
pip install Flask-Limiter
```

5. **Regular Backups** - Backup the database and uploads folder

## Database Migration

For production with PostgreSQL:

1. Install PostgreSQL adapter:
```bash
pip install psycopg2-binary
```

2. Update config.py:
```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'postgresql://user:password@localhost/medical_app'
```

## Reverse Proxy Setup (Nginx)

Example nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring

Monitor these logs:
- Application logs (check app.log)
- Server error logs
- Database connection logs

## Backup Strategy

1. Database backup:
```bash
# SQLite
cp medical_app.db backup_$(date +%Y%m%d).db
```

2. Uploads folder:
```bash
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

## Updates

Before deploying updates:
1. Backup database and uploads
2. Test in staging environment
3. Deploy during low-traffic hours
4. Monitor logs for errors

