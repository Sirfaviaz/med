from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, abort, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import RequestEntityTooLarge
from models import db, User, MedicalReport, SmokingLog
from datetime import datetime, timedelta
import os
import re
import logging

app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
if config_name == 'production':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Validation utilities
def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_filename(filename):
    """Validate filename"""
    if not filename or len(filename) > 255:
        return False
    return secure_filename(filename) != ""


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""


def sanitize_input(text, max_length=200):
    """Sanitize user input"""
    if not text:
        return ""
    text = text.strip()
    if len(text) > max_length:
        text = text[:max_length]
    # Remove potentially harmful characters
    text = text.replace('<', '').replace('>', '')
    return text


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    flash('Page not found', 'error')
    return redirect(url_for('index'))


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f'Internal error: {error}')
    flash('An error occurred. Please try again later.', 'error')
    return redirect(url_for('index'))


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect(request.url)


@app.after_request
def make_session_permanent(response):
    """Make session permanent for authenticated users"""
    if current_user.is_authenticated:
        session.permanent = True
    return response


@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        else:
            return redirect(url_for('patient_dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        name = request.form.get('name', '').strip()
        role = request.form.get('role', 'patient')
        
        # Validate inputs
        if not username or not email or not password or not name:
            flash('All fields are required', 'error')
            return redirect(url_for('register'))
        
        if not is_valid_email(email):
            flash('Invalid email format', 'error')
            return redirect(url_for('register'))
        
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            flash(error_msg, 'error')
            return redirect(url_for('register'))
        
        # Sanitize inputs
        username = sanitize_input(username, 80)
        name = sanitize_input(name, 120)
        role = role if role in ['patient', 'doctor'] else 'patient'
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already taken!', 'error')
            return redirect(url_for('register'))
        
        # Check if email already exists
        if User.query.filter_by(email=email.lower()).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        
        try:
            # Create new user
            user = User(
                username=username,
                email=email.lower(),
                name=name,
                role=role,
                password_hash=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            
            logger.info(f'New user registered: {username} ({role})')
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f'Registration error: {e}')
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form.get('login', '').strip()  # Can be username or email
        password = request.form.get('password', '')
        
        # Validate inputs
        if not login_input or not password:
            flash('Username/Email and password are required', 'error')
            return render_template('login.html')
        
        try:
            # Try to find user by username or email
            user = User.query.filter(
                (User.username == login_input) | (User.email == login_input.lower())
            ).first()
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user, remember=True)
                session.permanent = True
                logger.info(f'User logged in: {user.username} ({user.role})')
                flash('Login successful!', 'success')
                
                # Redirect based on role
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif user.role == 'doctor':
                    return redirect(url_for('doctor_dashboard'))
                else:
                    return redirect(url_for('patient_dashboard'))
            else:
                logger.warning(f'Failed login attempt for: {login_input}')
                flash('Invalid username/email or password', 'error')
        except Exception as e:
            logger.error(f'Login error: {e}')
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if current_user.role == 'doctor':
        flash('Access denied', 'error')
        return redirect(url_for('doctor_dashboard'))
    
    # Get recent smoking logs
    recent_logs = SmokingLog.query.filter_by(user_id=current_user.id)\
        .order_by(SmokingLog.date.desc(), SmokingLog.time.desc())\
        .limit(10).all()
    
    # Get medical reports
    reports = MedicalReport.query.filter_by(user_id=current_user.id)\
        .order_by(MedicalReport.uploaded_at.desc()).all()
    
    # Get current date for the form
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('patient_dashboard.html', logs=recent_logs, reports=reports, date_str=date_str)


@app.route('/patient/add-smoking-log', methods=['POST'])
@login_required
def add_smoking_log():
    if current_user.role == 'doctor':
        flash('Access denied', 'error')
        return redirect(url_for('doctor_dashboard'))
    
    try:
        # Validate required fields
        date = request.form.get('date', '').strip()
        time = request.form.get('time', '').strip()
        urge_level = request.form.get('urge_level', '0')
        smoke_or_resist = request.form.get('smoke_or_resist', '').strip()
        
        if not date or not time or not smoke_or_resist:
            flash('Date, time, and action are required', 'error')
            return redirect(url_for('patient_dashboard'))
        
        # Validate urge level
        try:
            urge_level = int(urge_level)
            if urge_level < 1 or urge_level > 5:
                flash('Urge level must be between 1 and 5', 'error')
                return redirect(url_for('patient_dashboard'))
        except ValueError:
            flash('Invalid urge level', 'error')
            return redirect(url_for('patient_dashboard'))
        
        # Validate smoke_or_resist
        if smoke_or_resist not in ['Smoked', 'Resisted']:
            flash('Invalid action selected', 'error')
            return redirect(url_for('patient_dashboard'))
        
        # Sanitize optional fields
        location = sanitize_input(request.form.get('location', ''), 200)
        trigger = sanitize_input(request.form.get('trigger', ''), 200)
        emotion = sanitize_input(request.form.get('emotion', ''), 200)
        who_with = sanitize_input(request.form.get('who_with', ''), 200)
        notes = sanitize_input(request.form.get('notes', ''), 500)
        
        log = SmokingLog(
            user_id=current_user.id,
            date=date,
            time=time,
            location=location,
            trigger=trigger,
            emotion=emotion,
            who_with=who_with,
            urge_level=urge_level,
            smoke_or_resist=smoke_or_resist,
            notes=notes
        )
        
        db.session.add(log)
        db.session.commit()
        
        logger.info(f'Smoking log added by user {current_user.email}')
        flash('Smoking log entry added successfully!', 'success')
        return redirect(url_for('patient_dashboard'))
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error adding smoking log: {e}')
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('patient_dashboard'))


@app.route('/patient/upload-report', methods=['POST'])
@login_required
def upload_report():
    if current_user.role == 'doctor':
        flash('Access denied', 'error')
        return redirect(url_for('doctor_dashboard'))
    
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('patient_dashboard'))
    
    file = request.files['file']
    report_name = request.form.get('report_name', 'Unnamed Report')
    
    # Validate and sanitize report name
    report_name = sanitize_input(report_name, 200) or 'Unnamed Report'
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('patient_dashboard'))
    
    # Validate file
    if not allowed_file(file.filename):
        flash('Invalid file type. Only PDF, JPG, and PNG files are allowed.', 'error')
        return redirect(url_for('patient_dashboard'))
    
    if not is_valid_filename(file.filename):
        flash('Invalid filename', 'error')
        return redirect(url_for('patient_dashboard'))
    
    try:
        # Secure filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(filepath)
        
        # Create database entry
        report = MedicalReport(
            user_id=current_user.id,
            report_name=report_name,
            filename=filename
        )
        
        db.session.add(report)
        db.session.commit()
        
        logger.info(f'Medical report uploaded by user {current_user.email}: {report_name}')
        flash('Medical report uploaded successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error uploading report: {e}')
        flash('An error occurred during upload. Please try again.', 'error')
    
    return redirect(url_for('patient_dashboard'))


@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        flash('Access denied', 'error')
        return redirect(url_for('patient_dashboard'))
    
    # Get all patients (users who are not doctors)
    patients = User.query.filter_by(role='patient').all()
    
    return render_template('doctor_dashboard.html', patients=patients)


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        if current_user.role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        else:
            return redirect(url_for('patient_dashboard'))
    
    # Get all users
    users = User.query.order_by(User.created_at.desc()).all()
    
    # Get statistics
    stats = {
        'total_users': len(users),
        'patients': len([u for u in users if u.role == 'patient']),
        'doctors': len([u for u in users if u.role == 'doctor']),
        'admins': len([u for u in users if u.role == 'admin'])
    }
    
    return render_template('admin_dashboard.html', users=users, stats=stats)


@app.route('/admin/users/<int:user_id>')
@login_required
def view_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('patient_dashboard'))
    
    user = User.query.get_or_404(user_id)
    return render_template('view_user.html', user=user)


@app.route('/admin/users/<int:user_id>/update', methods=['POST'])
@login_required
def update_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('patient_dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deletion of admin role
    if user.id == current_user.id and request.form.get('role') != 'admin':
        flash('You cannot change your own admin role', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        user.username = sanitize_input(request.form.get('username', ''), 80)
        user.email = request.form.get('email', '').strip().lower()
        user.name = sanitize_input(request.form.get('name', ''), 120)
        user.role = request.form.get('role', 'patient')
        
        # Validate role
        if user.role not in ['patient', 'doctor', 'admin']:
            user.role = 'patient'
        
        # Check for duplicate username (excluding current user)
        existing = User.query.filter(User.id != user.id, User.username == user.username).first()
        if existing:
            flash('Username already taken', 'error')
            return redirect(url_for('view_user', user_id=user_id))
        
        # Check for duplicate email (excluding current user)
        existing = User.query.filter(User.id != user.id, User.email == user.email).first()
        if existing:
            flash('Email already registered', 'error')
            return redirect(url_for('view_user', user_id=user_id))
        
        db.session.commit()
        logger.info(f'User {user_id} updated by admin {current_user.username}')
        flash('User updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error updating user: {e}')
        flash('An error occurred. Please try again.', 'error')
    
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('patient_dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash('You cannot delete yourself', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        logger.info(f'User {user_id} deleted by admin {current_user.username}')
        flash('User deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting user: {e}')
        flash('An error occurred. Please try again.', 'error')
    
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def reset_password(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('patient_dashboard'))
    
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password', '')
    
    if not new_password:
        flash('Password is required', 'error')
        return redirect(url_for('view_user', user_id=user_id))
    
    is_valid, error_msg = validate_password(new_password)
    if not is_valid:
        flash(error_msg, 'error')
        return redirect(url_for('view_user', user_id=user_id))
    
    try:
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        logger.info(f'Password reset for user {user_id} by admin {current_user.username}')
        flash('Password reset successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error resetting password: {e}')
        flash('An error occurred. Please try again.', 'error')
    
    return redirect(url_for('view_user', user_id=user_id))


@app.route('/doctor/patient/<int:patient_id>')
@login_required
def view_patient_data(patient_id):
    if current_user.role != 'doctor':
        flash('Access denied', 'error')
        return redirect(url_for('patient_dashboard'))
    
    patient = User.query.get_or_404(patient_id)
    
    # Get all smoking logs
    smoking_logs = SmokingLog.query.filter_by(user_id=patient_id)\
        .order_by(SmokingLog.date.desc(), SmokingLog.time.desc()).all()
    
    # Get all medical reports
    reports = MedicalReport.query.filter_by(user_id=patient_id)\
        .order_by(MedicalReport.uploaded_at.desc()).all()
    
    # Calculate statistics
    stats = {
        'total_entries': len(smoking_logs),
        'smoked_count': len([log for log in smoking_logs if log.smoke_or_resist == 'Smoked']),
        'resisted_count': len([log for log in smoking_logs if log.smoke_or_resist == 'Resisted']),
        'avg_urge_level': sum(log.urge_level for log in smoking_logs) / len(smoking_logs) if smoking_logs else 0,
        'total_reports': len(reports)
    }
    
    # Prepare data for visualization charts
    trigger_data = {}
    location_data = {}
    emotion_data = {}
    who_with_data = {}
    urge_distribution = {}
    
    for log in smoking_logs:
        # Trigger data
        if log.trigger and log.trigger.strip():
            trigger_data[log.trigger] = trigger_data.get(log.trigger, 0) + 1
        
        # Location data
        if log.location and log.location.strip():
            location_data[log.location] = location_data.get(log.location, 0) + 1
        
        # Emotion data
        if log.emotion and log.emotion.strip():
            emotion_data[log.emotion] = emotion_data.get(log.emotion, 0) + 1
        
        # Who with data
        if log.who_with and log.who_with.strip():
            who_with_data[log.who_with] = who_with_data.get(log.who_with, 0) + 1
        
        # Urge level distribution
        urge_distribution[log.urge_level] = urge_distribution.get(log.urge_level, 0) + 1
    
    # Sort by count descending
    chart_data = {
        'trigger': sorted(trigger_data.items(), key=lambda x: x[1], reverse=True) if trigger_data else None,
        'location': sorted(location_data.items(), key=lambda x: x[1], reverse=True) if location_data else None,
        'emotion': sorted(emotion_data.items(), key=lambda x: x[1], reverse=True) if emotion_data else None,
        'who_with': sorted(who_with_data.items(), key=lambda x: x[1], reverse=True) if who_with_data else None,
        'urge_level': sorted(urge_distribution.items(), key=lambda x: x[0]) if urge_distribution else None
    }
    
    # Find patterns - what triggers lead to smoking
    trigger_smoke_pattern = {}
    for log in smoking_logs:
        if log.trigger and log.trigger.strip() and log.smoke_or_resist == 'Smoked':
            if log.trigger not in trigger_smoke_pattern:
                trigger_smoke_pattern[log.trigger] = 0
            trigger_smoke_pattern[log.trigger] += 1
    
    location_smoke_pattern = {}
    for log in smoking_logs:
        if log.location and log.location.strip() and log.smoke_or_resist == 'Smoked':
            if log.location not in location_smoke_pattern:
                location_smoke_pattern[log.location] = 0
            location_smoke_pattern[log.location] += 1
    
    chart_data['trigger_smoke'] = sorted(trigger_smoke_pattern.items(), key=lambda x: x[1], reverse=True) if trigger_smoke_pattern else None
    chart_data['location_smoke'] = sorted(location_smoke_pattern.items(), key=lambda x: x[1], reverse=True) if location_smoke_pattern else None

    # Summary: last 30 days smoked counts per day
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=29)
    daily_counts = {}
    for i in range(30):
        d = start_date + timedelta(days=i)
        daily_counts[d.strftime('%Y-%m-%d')] = 0
    for log in smoking_logs:
        if log.smoke_or_resist == 'Smoked':
            try:
                log_date = datetime.strptime(log.date, '%Y-%m-%d').date()
            except Exception:
                # Skip if date format is unexpected
                continue
            if start_date <= log_date <= end_date:
                key = log_date.strftime('%Y-%m-%d')
                daily_counts[key] = daily_counts.get(key, 0) + 1

    summary_last30 = {
        'labels': list(daily_counts.keys()),
        'counts': list(daily_counts.values())
    }
    
    return render_template('view_patient.html', patient=patient, logs=smoking_logs, reports=reports, stats=stats, chart_data=chart_data, summary_last30=summary_last30)


@app.route('/autocomplete/<field_name>')
@login_required
def get_autocomplete_suggestions(field_name):
    """Get autocomplete suggestions for a specific field (last 7 entries, most used first)"""
    if current_user.role == 'doctor':
        return jsonify([]), 403
    
    # Query is optional search term
    query = request.args.get('q', '').strip().lower()
    
    # Get field from SmokingLog model
    if field_name == 'location':
        field = SmokingLog.location
    elif field_name == 'trigger':
        field = SmokingLog.trigger
    elif field_name == 'emotion':
        field = SmokingLog.emotion
    elif field_name == 'who_with':
        field = SmokingLog.who_with
    else:
        return jsonify([])
    
    # Get all unique values for this field from user's logs
    logs = SmokingLog.query.filter_by(user_id=current_user.id).all()
    
    # Count occurrences and filter by query
    suggestions = {}
    for log in logs:
        value = getattr(log, field_name)
        if value and value.strip():
            value_lower = value.strip().lower()
            if not query or query in value_lower:
                if value not in suggestions:
                    suggestions[value] = 0
                suggestions[value] += 1
    
    # Sort by frequency (most used first), limit to 7
    sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)[:7]
    
    return jsonify([item[0] for item in sorted_suggestions])


@app.route('/view-report/<filename>')
@login_required
def view_report(filename):
    """View medical report in browser instead of downloading"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        flash('File not found', 'error')
        return redirect(url_for('patient_dashboard'))
    
    # Check if user has access to this file
    report = MedicalReport.query.filter_by(filename=filename).first()
    if current_user.role == 'patient' and report and report.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('patient_dashboard'))
    
    return send_file(filepath)


@app.route('/download/<filename>')
@login_required
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Security check
    if not os.path.exists(filepath):
        flash('File not found', 'error')
        return redirect(url_for('patient_dashboard'))
    
    return send_file(filepath, as_attachment=True)


# Initialize database
with app.app_context():
    db.create_all()
    logger.info('Database initialized')

if __name__ == '__main__':
    # Get port from environment (Render provides this)
    port = int(os.environ.get('PORT', 5000))
    
    # Check if waitress is explicitly requested OR running on Render/production platform
    is_production = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RENDER')
    
    # Only use production server if explicitly in production OR on Render
    if is_production and os.environ.get('RENDER'):
        logger.info(f'Starting in production mode on port {port}')
        try:
            from waitress import serve
            serve(app, host='0.0.0.0', port=port)
        except Exception as e:
            logger.error(f'Waitress failed, using Flask dev server: {e}')
            app.run(debug=False, host='0.0.0.0', port=port)
    else:
        logger.info(f'Starting in development mode on port {port}')
        app.run(debug=True, host='0.0.0.0', port=port)

