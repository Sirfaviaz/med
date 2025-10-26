# Medical Tracker Web Application

A comprehensive medical tracking system for patients and doctors.

## Features

### For Patients:
- **Account Registration & Login** - Secure user authentication
- **Smoking Pattern Log** - Track smoking urges and habits with detailed information:
  - Date and Time
  - Location/Situation
  - Trigger/Cue
  - Emotion/Feeling
  - Who you were with
  - Urge Level (1-10)
  - Whether you smoked or resisted
  - Notes and reflections
- **Medical Report Upload** - Upload and manage lab reports (PDF, JPG, PNG)
- **View Recent Logs** - See your recent smoking log entries

### For Doctors:
- **Patient Dashboard** - View all registered patients
- **Patient Data Access** - Access detailed patient information
- **Smoking Pattern Analysis** - View complete smoking logs with statistics:
  - Total entries
  - Times smoked vs resisted
  - Average urge level
- **Medical Reports Tab** - Access all patient medical reports

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## First Time Setup

1. **Register an Account**:
   - For patient role: Select "Patient" when registering
   - For doctor role: Select "Doctor" when registering

2. **Login** with your credentials

## Usage

### As a Patient:
1. Login to your account
2. Use the smoking log form to track your patterns
3. Upload medical reports using the upload form
4. View your recent logs and uploaded reports on the dashboard

### As a Doctor:
1. Login to your account
2. View list of all patients
3. Click "View Data" on any patient to see:
   - Complete smoking pattern logs
   - Statistical summary
   - All medical reports in a separate tab

## Security Notes

- Change the `SECRET_KEY` in `app.py` for production use
- The application uses SQLite database (medical_app.db)
- Uploaded files are stored in the `uploads` directory
- Files are automatically named with timestamps to prevent conflicts

## File Structure

```
Medical/
├── app.py                  # Main Flask application
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── patient_dashboard.html
│   ├── doctor_dashboard.html
│   └── view_patient.html
├── static/                # Static files
│   └── style.css
└── uploads/               # Uploaded medical reports
```

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: SQLite (via SQLAlchemy)
- **Authentication**: Flask-Login
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Modern responsive design with gradient UI

## Security Features

- ✅ **Input Validation** - All user inputs are validated and sanitized
- ✅ **Password Security** - Minimum 6 characters, hashed with Werkzeug
- ✅ **File Upload Security** - Only PDF, JPG, PNG allowed; filename sanitization
- ✅ **SQL Injection Protection** - Using SQLAlchemy ORM
- ✅ **XSS Prevention** - Input sanitization removes harmful characters
- ✅ **Error Handling** - Comprehensive error handling and logging
- ✅ **Session Security** - Secure cookies in production
- ✅ **Access Control** - Role-based access control (patient/doctor)

## Development

The application runs in debug mode by default. 

### For Production Deployment:

1. **Set environment variables:**
```bash
export SECRET_KEY='your-strong-secret-key-here'
export FLASK_ENV='production'
```

2. **Install production dependencies:**
```bash
pip install waitress gunicorn
```

3. **Run in production mode:**
```bash
python run.py
# OR
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

See `PRODUCTION_DEPLOYMENT.md` for detailed deployment instructions.

## Validation & Testing

All routes now include:
- Input validation (email, password, dates, etc.)
- File type validation
- File size limits (16MB max)
- SQL injection prevention
- XSS protection
- Error logging
- Transaction rollback on errors

